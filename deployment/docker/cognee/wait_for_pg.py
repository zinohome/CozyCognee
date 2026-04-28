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
    consecutive_ok = 0
    required_ok = 3  # 连续 3 次成功才算就绪

    for i in range(1, max_retries + 1):
        try:
            conn = await asyncpg.connect(db_url)
            await conn.fetchval("SELECT 1")
            await conn.close()
            consecutive_ok += 1
            if consecutive_ok >= required_ok:
                print(f"[wait_for_pg] PostgreSQL ready after {i * delay}s ({required_ok} consecutive checks)")
                return
        except Exception as e:
            consecutive_ok = 0
            if i == max_retries:
                print(f"[wait_for_pg] FAILED after {max_retries * delay}s: {e}", file=sys.stderr)
                sys.exit(1)
        time.sleep(delay)


if __name__ == "__main__":
    asyncio.run(wait())
