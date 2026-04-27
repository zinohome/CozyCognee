"""FalkorDB dataset database handler for multi-tenant graph isolation."""

from uuid import UUID
from typing import Optional

from cognee.modules.users.models import User, DatasetDatabase
from cognee.infrastructure.databases.dataset_database_handler import (
    DatasetDatabaseHandlerInterface,
)


class FalkorDatasetDatabaseHandler(DatasetDatabaseHandlerInterface):
    """
    Handler for FalkorDB per-dataset graph isolation.

    Each dataset gets a unique named graph in FalkorDB: cognee_{user_id}_{dataset_id}.
    All graphs share the same FalkorDB/Redis instance but are completely isolated at
    the graph level — queries only see data within their named graph.
    """

    @classmethod
    async def create_dataset(cls, dataset_id: Optional[UUID], user: Optional[User]) -> dict:
        """Return connection info mapping this dataset to a unique FalkorDB graph."""
        from cognee.infrastructure.databases.graph.config import get_graph_config

        graph_config = get_graph_config()

        if graph_config.graph_database_provider != "falkor":
            raise ValueError(
                "FalkorDatasetDatabaseHandler can only be used with FalkorDB graph provider."
            )

        # Each dataset gets a uniquely named graph
        graph_name = f"cognee_{user.id}_{dataset_id}" if user else f"cognee_{dataset_id}"

        return {
            "graph_database_name": graph_name,
            "graph_database_url": graph_config.graph_database_url,
            "graph_database_provider": "falkor",
            "graph_database_key": graph_name,
            "graph_dataset_database_handler": "falkor",
            "graph_database_connection_info": {
                "graph_database_username": graph_config.graph_database_username,
                "graph_database_password": graph_config.graph_database_password,
            },
        }

    @classmethod
    async def delete_dataset(cls, dataset_database: DatasetDatabase):
        """Delete the FalkorDB graph for a dataset."""
        from cognee.infrastructure.databases.graph.get_graph_engine import (
            create_graph_engine,
        )

        graph_engine = create_graph_engine(
            graph_database_provider="falkor",
            graph_database_url=dataset_database.graph_database_url,
            graph_database_name=dataset_database.graph_database_name,
            graph_database_username=dataset_database.graph_database_connection_info.get(
                "graph_database_username", ""
            ),
            graph_database_password=dataset_database.graph_database_connection_info.get(
                "graph_database_password", ""
            ),
            graph_database_key=dataset_database.graph_database_key or dataset_database.graph_database_name,
            graph_file_path="",
            graph_dataset_database_handler="",
            graph_database_port="",
        )
        await graph_engine.delete_graph()
