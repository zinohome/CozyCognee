"""Wait for PostgreSQL and run alembic migration before Cognee starts.

Uses SQLAlchemy+asyncpg (same driver as Cognee) to verify PG is fully ready.
Requires 5 consecutive successful connections at 3s intervals to account for
PG's TCP restart window after init.sh completes.
"""
import os
import sys
import time
import asyncio
import subprocess


async def wait_for_pg():
    from sqlalchemy import URL, text
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.pool import NullPool

    url = URL.create(
        "postgresql+asyncpg",
        username=os.environ.get("DB_USERNAME", "cognee"),
        password=os.environ.get("DB_PASSWORD", "cognee"),
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "5432")),
        database=os.environ.get("DB_NAME", "cognee_db"),
    )

    max_retries = 60
    delay = 3
    consecutive_ok = 0
    required_ok = 5

    for i in range(1, max_retries + 1):
        try:
            engine = create_async_engine(url, poolclass=NullPool)
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            consecutive_ok += 1
            if consecutive_ok >= required_ok:
                print(f"[wait_for_pg] PostgreSQL stable after {i * delay}s ({required_ok} consecutive checks)")
                return True
        except Exception:
            consecutive_ok = 0
            if i == max_retries:
                print(f"[wait_for_pg] FAILED after {max_retries * delay}s", file=sys.stderr)
                return False
        time.sleep(delay)
    return False


def run_migration():
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd="/app/cognee",
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print("[wait_for_pg] Alembic migration OK")
            return True
        stderr = result.stderr + result.stdout
        if "UserAlreadyExists" in stderr or "already exists" in stderr.lower():
            print("[wait_for_pg] Migration: non-critical (already exists)")
            return True
        print(f"[wait_for_pg] Migration failed: {stderr[:200]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[wait_for_pg] Migration error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if not asyncio.run(wait_for_pg()):
        sys.exit(1)
    run_migration()
