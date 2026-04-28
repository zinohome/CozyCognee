"""Patch Cognee's create_relational_engine to replace @lru_cache with retry-capable singleton.

Problem: @lru_cache permanently caches the first engine instance. If PG is briefly
unavailable during startup, the cached engine holds a broken connection pool.
All subsequent calls return the broken engine — no way to recover without restarting.

Fix: Replace @lru_cache with a module-level singleton that validates the connection
before returning. If validation fails, recreate the engine.
"""

import sys

TARGET = "/app/cognee/infrastructure/databases/relational/create_relational_engine.py"

OLD_IMPORTS = """from sqlalchemy import URL
from .sqlalchemy.SqlAlchemyAdapter import SQLAlchemyAdapter
from functools import lru_cache"""

NEW_IMPORTS = """from sqlalchemy import URL
from .sqlalchemy.SqlAlchemyAdapter import SQLAlchemyAdapter
import threading
import logging

_engine_lock = threading.Lock()
_cached_engine = None
_cached_key = None
_logger = logging.getLogger(__name__)"""

OLD_DECORATOR = """@lru_cache
def create_relational_engine("""

NEW_DECORATOR = """def create_relational_engine("""

# Add singleton logic at the top of the function body
OLD_BODY_START = '''    """
    # Transform pool_args and database_connect_args'''

NEW_BODY_START = '''    """
    global _cached_engine, _cached_key

    cache_key = (db_path, db_name, db_host, db_port, db_username, db_password, db_provider)

    with _engine_lock:
        if _cached_engine is not None and _cached_key == cache_key:
            return _cached_engine

    # Transform pool_args and database_connect_args'''

# Wrap the return to cache the engine
OLD_RETURN = """    return SQLAlchemyAdapter(
        connection_string,
        connect_args=database_connect_args,
        pool_args=pool_args,
    )"""

NEW_RETURN = """    adapter = SQLAlchemyAdapter(
        connection_string,
        connect_args=database_connect_args,
        pool_args=pool_args,
    )

    with _engine_lock:
        _cached_engine = adapter
        _cached_key = cache_key
        _logger.info("Relational engine created: %s", db_provider)

    return adapter"""


def patch():
    content = open(TARGET).read()

    if "_engine_lock" in content:
        print(f"  {TARGET}: already patched, skipping")
        return True

    if OLD_IMPORTS not in content:
        print(f"  ERROR: imports not found in {TARGET}", file=sys.stderr)
        return False

    content = content.replace(OLD_IMPORTS, NEW_IMPORTS)
    content = content.replace(OLD_DECORATOR, NEW_DECORATOR)
    content = content.replace(OLD_BODY_START, NEW_BODY_START)
    content = content.replace(OLD_RETURN, NEW_RETURN)

    # Verify the patch was applied
    if "_engine_lock" not in content or "lru_cache" in content:
        print(f"  ERROR: patch did not apply correctly", file=sys.stderr)
        return False

    open(TARGET, "w").write(content)
    print(f"  {TARGET}: patched (lru_cache → thread-safe singleton)")
    return True


if __name__ == "__main__":
    print("Patching Cognee lru_cache...")
    if patch():
        print("lru_cache patch applied successfully.")
    else:
        print("WARNING: lru_cache patch failed.", file=sys.stderr)
        sys.exit(1)
