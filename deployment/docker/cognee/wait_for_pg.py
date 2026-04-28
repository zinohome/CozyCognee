"""Wait for PostgreSQL, then run Cognee migration in the SAME Python process.

Key insight: Cognee's get_relational_engine() uses a singleton. If we create
the engine in this process after PG is confirmed ready, AND then run alembic
in the same process, the singleton is guaranteed to have a working connection.

When entrypoint.sh then starts gunicorn, it's a NEW process — but alembic is
already at head, so Cognee's migration is a fast no-op.
"""
import os
import sys
import time
import asyncio


async def wait_for_pg():
    """Wait until PG accepts SQLAlchemy+asyncpg connections (same driver as Cognee)."""
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
                print(f"[wait_for_pg] PostgreSQL stable after {i * delay}s")
                return True
        except Exception:
            consecutive_ok = 0
            if i == max_retries:
                print(f"[wait_for_pg] FAILED after {max_retries * delay}s", file=sys.stderr)
                return False
        time.sleep(delay)
    return False


def run_migration_in_process():
    """Run alembic migration using Cognee's own engine (in-process, not subprocess).

    This ensures the singleton engine is created with a working PG connection.
    """
    try:
        # Import Cognee's engine — creates the singleton with current (working) PG connection
        from cognee.infrastructure.databases.relational.get_relational_engine import get_relational_engine
        engine = get_relational_engine()
        uri = engine.db_uri if isinstance(engine.db_uri, str) else engine.db_uri.render_as_string(hide_password=True)
        print(f"[wait_for_pg] Engine created: {uri}")

        # Run alembic programmatically using the same engine
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config("/app/cognee/alembic.ini")
        alembic_cfg.set_main_option("script_location", "/app/cognee/alembic")

        # Set the database URL from the engine (matches what env.py would compute)
        db_uri = engine.db_uri if isinstance(engine.db_uri, str) else engine.db_uri.render_as_string(hide_password=False)
        alembic_cfg.set_section_option(
            alembic_cfg.config_ini_section,
            "SQLALCHEMY_DATABASE_URI",
            db_uri,
        )

        command.upgrade(alembic_cfg, "head")
        print("[wait_for_pg] Alembic migration OK (in-process)")
        return True
    except Exception as e:
        err = str(e)
        if "UserAlreadyExists" in err or "already exists" in err.lower():
            print("[wait_for_pg] Migration: non-critical (already exists)")
            return True
        print(f"[wait_for_pg] Migration error: {err[:200]}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if not asyncio.run(wait_for_pg()):
        sys.exit(1)
    run_migration_in_process()
