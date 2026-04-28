"""Wait for PostgreSQL using psycopg2 (libpq) — same auth path as psql.

psycopg2 uses the C libpq library for scram-sha-256 auth, which is
proven reliable (CozyMemory uses it with zero password errors).
asyncpg's pure-Python scram implementation has intermittent auth failures.
"""
import os
import sys
import time


def wait():
    import psycopg2

    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    user = os.environ.get("DB_USERNAME", "cognee")
    password = os.environ.get("DB_PASSWORD", "cognee")
    dbname = os.environ.get("DB_NAME", "cognee_db")

    dsn = f"host={host} port={port} user={user} password={password} dbname={dbname} connect_timeout=5"

    max_retries = 60
    delay = 3
    consecutive_ok = 0
    required_ok = 5

    for i in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(dsn)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            consecutive_ok += 1
            if consecutive_ok >= required_ok:
                print(f"[wait_for_pg] PostgreSQL stable after {i * delay}s ({required_ok} consecutive psycopg2 checks)")
                return True
        except Exception:
            consecutive_ok = 0
            if i == max_retries:
                print(f"[wait_for_pg] FAILED after {max_retries * delay}s", file=sys.stderr)
                return False
        time.sleep(delay)
    return False


if __name__ == "__main__":
    if not wait():
        sys.exit(1)
