"""Patch Cognee source to register FalkorDB as a graph database provider.

This script modifies two files:
1. get_graph_engine.py — add 'falkor' provider case
2. supported_dataset_database_handlers.py — register FalkorDatasetDatabaseHandler
"""

import sys


def patch_get_graph_engine(filepath: str) -> bool:
    """Add falkor provider to the graph engine factory."""
    content = open(filepath).read()
    if 'graph_database_provider == "falkor"' in content:
        print(f"  {filepath}: already patched, skipping")
        return True

    # Insert before 'elif graph_database_provider == "kuzu-remote"'
    insert_code = '''
    elif graph_database_provider == "falkor":
        if not graph_database_url:
            raise EnvironmentError("Missing required FalkorDB URL (GRAPH_DATABASE_URL).")

        from .falkor.adapter import FalkorAdapter

        return FalkorAdapter(
            graph_database_url=graph_database_url,
            graph_database_port=graph_database_port,
            graph_database_username=graph_database_username,
            graph_database_password=graph_database_password,
            graph_database_key=graph_database_key,
            database_name=graph_database_name or "cognee",
        )

'''
    anchor = '    elif graph_database_provider == "kuzu-remote":'
    if anchor not in content:
        print(f"  ERROR: anchor not found in {filepath}", file=sys.stderr)
        return False

    content = content.replace(anchor, insert_code + anchor)
    open(filepath, "w").write(content)
    print(f"  {filepath}: patched successfully")
    return True


def patch_supported_handlers(filepath: str) -> bool:
    """Register FalkorDatasetDatabaseHandler."""
    content = open(filepath).read()
    if "FalkorDatasetDatabaseHandler" in content:
        print(f"  {filepath}: already patched, skipping")
        return True

    # Add import
    import_line = (
        "from cognee.infrastructure.databases.graph.falkor.FalkorDatasetDatabaseHandler "
        "import (\n    FalkorDatasetDatabaseHandler,\n)\n"
    )
    # Insert after the last existing import block
    anchor = "from cognee.infrastructure.databases.vector.pgvector.PGVectorDatasetDatabaseHandler import ("
    if anchor not in content:
        print(f"  ERROR: import anchor not found in {filepath}", file=sys.stderr)
        return False

    # Find end of that import block and insert after
    idx = content.index(anchor)
    # Find the closing paren + newline
    close_idx = content.index(")", idx) + 1
    # Skip any trailing newline
    if close_idx < len(content) and content[close_idx] == "\n":
        close_idx += 1
    content = content[:close_idx] + import_line + content[close_idx:]

    # Add handler entry
    entry = '    "falkor": {"handler_instance": FalkorDatasetDatabaseHandler, "handler_provider": "falkor"},\n'
    # Insert before the closing }
    last_brace = content.rindex("}")
    content = content[:last_brace] + entry + content[last_brace:]

    open(filepath, "w").write(content)
    print(f"  {filepath}: patched successfully")
    return True


if __name__ == "__main__":
    print("Patching Cognee for FalkorDB support...")
    base = "/app/cognee/infrastructure/databases"

    ok1 = patch_get_graph_engine(f"{base}/graph/get_graph_engine.py")
    ok2 = patch_supported_handlers(f"{base}/dataset_database_handler/supported_dataset_database_handlers.py")

    if ok1 and ok2:
        print("FalkorDB patches applied successfully.")
    else:
        print("WARNING: Some patches failed. FalkorDB may not work.", file=sys.stderr)
        sys.exit(1)
