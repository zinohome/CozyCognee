"""Wait for PostgreSQL to be fully ready before starting Cognee.

Simple and robust: loop psql with password auth until 5 consecutive successes.
Uses subprocess psql (not asyncpg) to match the exact auth path PG uses.
"""
import os
import sys
import time
import subprocess


def wait():
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    user = os.environ.get("DB_USERNAME", "cognee")
    password = os.environ.get("DB_PASSWORD", "cognee")
    dbname = os.environ.get("DB_NAME", "cognee_db")

    max_retries = 60
    delay = 3
    consecutive_ok = 0
    required_ok = 5

    env = {**os.environ, "PGPASSWORD": password}

    for i in range(1, max_retries + 1):
        try:
            r = subprocess.run(
                ["psql", "-h", host, "-p", port, "-U", user, "-d", dbname,
                 "-c", "SELECT 1", "-q", "--no-password"],
                env=env, capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0:
                consecutive_ok += 1
                if consecutive_ok >= required_ok:
                    print(f"[wait_for_pg] PostgreSQL stable after {i * delay}s ({required_ok} consecutive psql checks)")
                    return True
            else:
                consecutive_ok = 0
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
