"""Patch Cognee's alembic env.py to use psycopg2 instead of asyncpg for migrations.

Problem: asyncpg's pure-Python scram-sha-256 implementation has intermittent
auth failures during PG startup. psycopg2 (libpq C library) is 100% reliable.

Fix: Replace 'postgresql+asyncpg' with 'postgresql+psycopg2' in the alembic URL
so migrations use the synchronous psycopg2 driver. This only affects alembic
migrations — Cognee's runtime still uses asyncpg for async operations.
"""

import sys

TARGET = "/app/cognee/alembic/env.py"


def patch():
    content = open(TARGET).read()

    if "replace_asyncpg" in content or "psycopg2" in content:
        print(f"  {TARGET}: already patched, skipping")
        return True

    # Find where db_uri is set and add a replacement line after it
    old = '''db_uri = (
    db_engine.db_uri
    if isinstance(db_engine.db_uri, str)
    else db_engine.db_uri.render_as_string(hide_password=False)
)'''

    new = '''db_uri = (
    db_engine.db_uri
    if isinstance(db_engine.db_uri, str)
    else db_engine.db_uri.render_as_string(hide_password=False)
)

# CozyCognee patch: use psycopg2 (libpq) for migration instead of asyncpg
# asyncpg has intermittent scram-sha-256 auth failures during PG startup
def replace_asyncpg(uri):
    if isinstance(uri, str) and "asyncpg" in uri:
        return uri.replace("postgresql+asyncpg", "postgresql+psycopg2")
    return str(uri).replace("postgresql+asyncpg", "postgresql+psycopg2")
db_uri = replace_asyncpg(db_uri)'''

    if old not in content:
        print(f"  ERROR: target code not found in {TARGET}", file=sys.stderr)
        return False

    content = content.replace(old, new)

    # Also change async_engine_from_config to engine_from_config for sync psycopg2
    content = content.replace(
        "from sqlalchemy.ext.asyncio import async_engine_from_config",
        "from sqlalchemy import create_engine"
    )

    # Replace the async migration runner with sync version
    old_async = '''async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())'''

    new_sync = '''def run_migrations_online() -> None:
    """Run migrations in 'online' mode using psycopg2 (sync, reliable scram-sha-256)."""

    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()'''

    if old_async in content:
        content = content.replace(old_async, new_sync)
        # Remove unused asyncio import if present
        content = content.replace("import asyncio\n", "")
    else:
        print(f"  WARNING: async migration code not found, skipping sync conversion")

    open(TARGET, "w").write(content)
    print(f"  {TARGET}: patched (asyncpg → psycopg2 for alembic)")
    return True


if __name__ == "__main__":
    print("Patching Cognee alembic driver...")
    if patch():
        print("Alembic driver patch applied successfully.")
    else:
        print("Patch failed.", file=sys.stderr)
        sys.exit(1)
