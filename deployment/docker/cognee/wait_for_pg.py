"""Wait for PostgreSQL and run alembic migration before Cognee starts.

This prevents lru_cache poisoning: Cognee's entrypoint runs alembic migration
which creates an engine via @lru_cache. If PG isn't ready, the broken engine
is cached forever. By running migration here first (after PG is confirmed ready),
we ensure the cached engine has a working connection pool.
"""
import os
import sys
import time
import asyncio
import subprocess


async def wait_for_pg():
    """Wait until PG accepts SQLAlchemy+asyncpg connections."""
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

    max_retries = 30
    delay = 2
    consecutive_ok = 0
    required_ok = 3

    for i in range(1, max_retries + 1):
        try:
            engine = create_async_engine(url, poolclass=NullPool)
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            consecutive_ok += 1
            if consecutive_ok >= required_ok:
                print(f"[wait_for_pg] PostgreSQL ready after {i * delay}s")
                return True
        except Exception:
            consecutive_ok = 0
            if i == max_retries:
                print(f"[wait_for_pg] FAILED after {max_retries * delay}s", file=sys.stderr)
                return False
        time.sleep(delay)
    return False


def run_migration():
    """Run alembic migration. Returns True if successful."""
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd="/app/cognee",
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print("[wait_for_pg] Alembic migration completed successfully")
            return True
        else:
            # Check for known non-critical errors
            stderr = result.stderr + result.stdout
            if "UserAlreadyExists" in stderr or "already exists" in stderr.lower():
                print("[wait_for_pg] Migration: non-critical error (already exists), continuing")
                return True
            print(f"[wait_for_pg] Migration failed: {stderr[:200]}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("[wait_for_pg] Migration timed out after 60s", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[wait_for_pg] Migration error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if not asyncio.run(wait_for_pg()):
        sys.exit(1)

    # Run migration here so entrypoint.sh's migration becomes a no-op (already at head)
    if run_migration():
        # Set env flag so entrypoint.sh can skip migration
        # (entrypoint.sh checks MIGRATION_OUTPUT for errors)
        print("[wait_for_pg] Migration done, Cognee can start safely")
    else:
        print("[wait_for_pg] Migration failed, Cognee will retry in entrypoint.sh")
