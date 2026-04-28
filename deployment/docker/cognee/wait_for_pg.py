"""Wait for PostgreSQL to be fully ready before starting Cognee.

Uses the same connection method as Cognee (SQLAlchemy + asyncpg via DB_* env vars)
to prevent lru_cache poisoning from early connection failures.
"""
import os
import sys
import time
import asyncio


async def wait():
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
                print(f"[wait_for_pg] PostgreSQL ready after {i * delay}s ({required_ok} consecutive SQLAlchemy+asyncpg checks)")
                return
        except Exception as e:
            consecutive_ok = 0
            if i == max_retries:
                print(f"[wait_for_pg] FAILED after {max_retries * delay}s: {e}", file=sys.stderr)
                sys.exit(1)
        time.sleep(delay)


if __name__ == "__main__":
    asyncio.run(wait())
