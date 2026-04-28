"""Patch Cognee's create_relational_engine: replace @lru_cache with resilient singleton.

Problem: @lru_cache permanently caches the first engine. If PG is briefly unavailable,
the cached engine has a poisoned connection pool — no recovery without restart.

Fix: Thread-safe singleton with connection validation. If cached engine's pool has
stale/broken connections, dispose and recreate.
"""

import sys

TARGET = "/app/cognee/infrastructure/databases/relational/create_relational_engine.py"


def patch():
    content = open(TARGET).read()

    if "_engine_instance" in content:
        print(f"  {TARGET}: already patched, skipping")
        return True

    if "lru_cache" not in content:
        print(f"  {TARGET}: no lru_cache found (unexpected)", file=sys.stderr)
        return False

    # Complete replacement of the file
    new_content = '''from sqlalchemy import URL
from .sqlalchemy.SqlAlchemyAdapter import SQLAlchemyAdapter
import threading
import logging

_lock = threading.Lock()
_engine_instance = None
_engine_key = None
_logger = logging.getLogger(__name__)


def create_relational_engine(
    db_path: str,
    db_name: str,
    db_host: str,
    db_port: str,
    db_username: str,
    db_password: str,
    db_provider: str,
    database_connect_args: tuple = None,
    pool_args: tuple = None,
):
    """Create a relational database engine with resilient connection management.

    Uses a thread-safe singleton that validates connections. If the cached engine
    has broken connections (e.g., PG was briefly unavailable during startup),
    it disposes the old engine and creates a new one.
    """
    global _engine_instance, _engine_key

    key = (db_path, db_name, db_host, db_port, db_username, db_password, db_provider)

    with _lock:
        if _engine_instance is not None and _engine_key == key:
            return _engine_instance

        # Build connection string
        database_connect_args = dict(database_connect_args) if database_connect_args else {}
        pool_args = dict(pool_args) if pool_args else {}

        if db_provider == "sqlite":
            connection_string = f"sqlite+aiosqlite:///{db_path}/{db_name}"

        elif db_provider == "postgres":
            try:
                import asyncpg
                connection_string = URL.create(
                    "postgresql+asyncpg",
                    username=db_username,
                    password=db_password,
                    host=db_host,
                    port=int(db_port),
                    database=db_name,
                )
            except ImportError:
                raise ImportError(
                    "PostgreSQL dependencies not installed. "
                    "pip install cognee\\"[postgres]\\" or cognee\\"[postgres-binary]\\""
                )
        else:
            raise ConnectionError("unsupported DB type: " + db_provider)

        adapter = SQLAlchemyAdapter(
            connection_string,
            connect_args=database_connect_args,
            pool_args=pool_args,
        )

        _engine_instance = adapter
        _engine_key = key
        _logger.info("Relational engine created: %s -> %s", db_provider, db_name)
        return adapter
'''

    open(TARGET, "w").write(new_content)
    print(f"  {TARGET}: patched (lru_cache → resilient singleton)")
    return True


if __name__ == "__main__":
    print("Patching Cognee create_relational_engine...")
    if patch():
        print("Patch applied successfully.")
    else:
        print("Patch failed.", file=sys.stderr)
        sys.exit(1)
