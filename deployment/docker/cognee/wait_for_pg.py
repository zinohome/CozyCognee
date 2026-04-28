"""Wait for PostgreSQL to be fully ready before starting Cognee.

Prevents lru_cache poisoning: if the first PG connection attempt fails,
SQLAlchemy's cached engine holds a broken connection pool. This script
ensures PG is reachable with correct credentials before Cognee starts.
"""
import os
import sys
import time
import asyncio


async def wait():
    import asyncpg

    db_url = os.environ.get("DATABASE_URL", "")
    max_retries = 30
    delay = 2

    for i in range(1, max_retries + 1):
        try:
            conn = await asyncpg.connect(db_url)
            await conn.fetchval("SELECT 1")
            await conn.close()
            print(f"[wait_for_pg] PostgreSQL ready after {i * delay}s")
            return
        except Exception as e:
            if i == max_retries:
                print(f"[wait_for_pg] FAILED after {max_retries * delay}s: {e}", file=sys.stderr)
                sys.exit(1)
            time.sleep(delay)


if __name__ == "__main__":
    asyncio.run(wait())
