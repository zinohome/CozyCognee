"""Patch Cognee alembic migration to handle missing pipelinerunstatus type.

Problem: Migration 1d0bb7fede17 runs ALTER TYPE pipelinerunstatus ADD VALUE,
but on a fresh database this enum type doesn't exist yet (it's created by
SQLAlchemy's create_all in Cognee's fallback mode). This causes migration
to fail with UndefinedObjectError.

Fix: Wrap the ALTER TYPE in a try-except so the migration is a no-op if
the type doesn't exist. The type will be created later by create_all.
"""

import sys

TARGET = "/app/cognee/alembic/versions/1d0bb7fede17_add_pipeline_run_status.py"


def patch():
    content = open(TARGET).read()

    if "except Exception" in content:
        print(f"  {TARGET}: already patched, skipping")
        return True

    old = '''    if db_engine.engine.dialect.name == "postgresql":
        op.execute(
            "ALTER TYPE pipelinerunstatus ADD VALUE IF NOT EXISTS 'DATASET_PROCESSING_INITIATED'"
        )'''

    new = '''    if db_engine.engine.dialect.name == "postgresql":
        try:
            op.execute(
                "ALTER TYPE pipelinerunstatus ADD VALUE IF NOT EXISTS 'DATASET_PROCESSING_INITIATED'"
            )
        except Exception:
            # Type may not exist on fresh databases; create_all will handle it
            pass'''

    if old not in content:
        print(f"  ERROR: target code not found in {TARGET}", file=sys.stderr)
        return False

    content = content.replace(old, new)
    open(TARGET, "w").write(content)
    print(f"  {TARGET}: patched (added try-except for missing enum)")
    return True


if __name__ == "__main__":
    print("Patching Cognee migration...")
    if patch():
        print("Migration patch applied successfully.")
    else:
        print("Migration patch failed.", file=sys.stderr)
        sys.exit(1)
