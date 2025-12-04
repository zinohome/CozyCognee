"""
Data models for Cognee SDK.

All models use Pydantic BaseModel for type validation and serialization.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class SearchType(str, Enum):
    """Search type enumeration."""

    SUMMARIES = "SUMMARIES"
    CHUNKS = "CHUNKS"
    RAG_COMPLETION = "RAG_COMPLETION"
    GRAPH_COMPLETION = "GRAPH_COMPLETION"
    GRAPH_SUMMARY_COMPLETION = "GRAPH_SUMMARY_COMPLETION"
    CODE = "CODE"
    CYPHER = "CYPHER"
    NATURAL_LANGUAGE = "NATURAL_LANGUAGE"
    GRAPH_COMPLETION_COT = "GRAPH_COMPLETION_COT"
    GRAPH_COMPLETION_CONTEXT_EXTENSION = "GRAPH_COMPLETION_CONTEXT_EXTENSION"
    FEELING_LUCKY = "FEELING_LUCKY"
    FEEDBACK = "FEEDBACK"
    TEMPORAL = "TEMPORAL"
    CODING_RULES = "CODING_RULES"
    CHUNKS_LEXICAL = "CHUNKS_LEXICAL"


class PipelineRunStatus(str, Enum):
    """Pipeline run status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class User(BaseModel):
    """User model."""

    id: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")


class Dataset(BaseModel):
    """Dataset model."""

    id: UUID = Field(..., description="Dataset ID")
    name: str = Field(..., description="Dataset name")
    created_at: datetime = Field(..., description="Dataset creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    owner_id: UUID = Field(..., description="Dataset owner ID")


class DataItem(BaseModel):
    """Data item model."""

    id: UUID = Field(..., description="Data item ID")
    name: str = Field(..., description="Data item name")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    extension: str = Field(..., description="File extension")
    mime_type: str = Field(..., description="MIME type")
    raw_data_location: str = Field(..., description="Raw data storage location")
    dataset_id: UUID = Field(..., description="Dataset ID")


class AddResult(BaseModel):
    """Result model for add operation."""

    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")
    data_id: Optional[UUID] = Field(None, description="Created data ID")
    dataset_id: Optional[UUID] = Field(None, description="Dataset ID")


class DeleteResult(BaseModel):
    """Result model for delete operation."""

    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")


class CognifyResult(BaseModel):
    """Result model for cognify operation."""

    pipeline_run_id: UUID = Field(..., description="Pipeline run ID")
    status: str = Field(..., description="Pipeline status")
    entity_count: Optional[int] = Field(None, description="Number of entities extracted")
    duration: Optional[float] = Field(None, description="Processing duration in seconds")
    message: Optional[str] = Field(None, description="Status message")


class MemifyResult(BaseModel):
    """Result model for memify operation."""

    pipeline_run_id: UUID = Field(..., description="Pipeline run ID")
    status: str = Field(..., description="Pipeline status")
    message: Optional[str] = Field(None, description="Status message")


class UpdateResult(BaseModel):
    """Result model for update operation."""

    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")
    data_id: Optional[UUID] = Field(None, description="Updated data ID")


class SearchResult(BaseModel):
    """Search result model.

    Note: The actual structure may vary based on search_type.
    This is a base model that can be extended.
    """

    # Common fields that appear in most search results
    id: Optional[str] = Field(None, description="Result ID")
    text: Optional[str] = Field(None, description="Result text content")
    score: Optional[float] = Field(None, description="Relevance score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    # Allow additional fields
    class Config:
        extra = "allow"


class CombinedSearchResult(BaseModel):
    """Combined search result model."""

    result: str = Field(..., description="Combined result text")
    context: Optional[List[str]] = Field(None, description="Context chunks")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SearchHistoryItem(BaseModel):
    """Search history item model."""

    id: UUID = Field(..., description="Search history ID")
    text: str = Field(..., description="Search query text")
    user: str = Field(..., description="User who performed the search")
    created_at: datetime = Field(..., description="Search timestamp")


class GraphNode(BaseModel):
    """Graph node model."""

    id: UUID = Field(..., description="Node ID")
    label: str = Field(..., description="Node label")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")


class GraphEdge(BaseModel):
    """Graph edge model."""

    source: UUID = Field(..., description="Source node ID")
    target: UUID = Field(..., description="Target node ID")
    label: str = Field(..., description="Edge label")


class GraphData(BaseModel):
    """Graph data model."""

    nodes: List[GraphNode] = Field(..., description="List of graph nodes")
    edges: List[GraphEdge] = Field(..., description="List of graph edges")


class SyncResult(BaseModel):
    """Result model for sync operation."""

    run_id: str = Field(..., description="Sync operation run ID")
    status: str = Field(..., description="Sync status")
    dataset_ids: List[UUID] = Field(..., description="Dataset IDs being synced")
    dataset_names: List[str] = Field(..., description="Dataset names being synced")
    message: str = Field(..., description="Status message")
    timestamp: Optional[datetime] = Field(None, description="Sync initiation timestamp")
    user_id: Optional[UUID] = Field(None, description="User ID who initiated sync")


class SyncStatus(BaseModel):
    """Sync status model."""

    has_running_sync: bool = Field(..., description="Whether there are running syncs")
    running_sync_count: int = Field(..., description="Number of running sync operations")
    latest_running_sync: Optional[Dict[str, Any]] = Field(
        None, description="Information about the latest running sync"
    )


class HealthStatus(BaseModel):
    """Health check status model."""

    status: str = Field(..., description="Health status")
    version: Optional[str] = Field(None, description="API version")

