"""FalkorDB adapter implementing Cognee's GraphDBInterface.

FalkorDB is a Redis-based graph database supporting OpenCypher queries.
This adapter uses the falkordb async Python client (v1.6.0+).

Storage layout:
  - All nodes stored with label Node and a string `id` property (UUID).
  - Node type stored as `_node_type` property.
  - Extra properties JSON-serialised into `_props` string field.
  - Edges use relationship type `REL` with `_rel_name` and `_props` properties.

Connection string: redis://host:port  (graph_database_url constructor arg)
Graph name: `database_name` constructor arg (default "cognee").
"""

import json
import asyncio
import time
from uuid import UUID
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Type, Union, Set

try:
    from falkordb.asyncio import FalkorDB
    from redis.asyncio import BlockingConnectionPool
except ImportError:  # pragma: no cover – only missing at static-analysis time
    FalkorDB = None  # type: ignore[misc,assignment]
    BlockingConnectionPool = None  # type: ignore[misc,assignment]

from cognee.shared.logging_utils import get_logger
from cognee.infrastructure.databases.graph.graph_db_interface import (
    GraphDBInterface,
    NodeData,
    EdgeData,
    Node,
)
from cognee.infrastructure.engine import DataPoint

logger = get_logger()

# ---------------------------------------------------------------------------
# Tiny JSON serialiser that handles UUID / datetime (mirrors KuzuAdapter's
# JSONEncoder but avoids the import path that may not exist in the image).
# ---------------------------------------------------------------------------

class _Encoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:  # type: ignore[override]
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def _dumps(obj: Any) -> str:
    return json.dumps(obj, cls=_Encoder)


def _loads_safe(s: Any) -> Any:
    if not isinstance(s, str) or not s:
        return {}
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return {}


# ---------------------------------------------------------------------------
# Result-row helpers
# ---------------------------------------------------------------------------

def _node_obj_to_dict(node: Any) -> Dict[str, Any]:
    """Convert a falkordb Node object to a plain dict."""
    props: Dict[str, Any] = dict(node.properties) if hasattr(node, "properties") else {}
    return props


def _edge_obj_to_dict(edge: Any) -> Dict[str, Any]:
    props: Dict[str, Any] = dict(edge.properties) if hasattr(edge, "properties") else {}
    return props


def _expand_props(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Merge `_props` JSON field into the top-level dict and remove it."""
    extra = _loads_safe(raw.pop("_props", None))
    if isinstance(extra, dict):
        raw.update(extra)
    return raw


# ---------------------------------------------------------------------------
# FalkorAdapter
# ---------------------------------------------------------------------------

class FalkorAdapter(GraphDBInterface):
    """
    Adapter for FalkorDB (Redis-backed OpenCypher graph) implementing
    Cognee's GraphDBInterface (26 methods).

    Constructor parameters match Cognee's graph_db_config pattern:
      graph_database_url  – Redis URL, e.g. "redis://localhost:6379"
      graph_database_key  – used as the FalkorDB graph name (dataset/tenant key)
      database_name       – fallback graph name when graph_database_key is empty
    """

    def __init__(
        self,
        graph_database_url: str = "redis://localhost:6379",
        graph_database_port: str = "",
        graph_database_username: str = "",
        graph_database_password: str = "",
        graph_database_key: str = "",
        database_name: str = "cognee",
    ) -> None:
        self._url = graph_database_url
        self._graph_name = graph_database_key if graph_database_key else database_name
        self._pool: Optional[Any] = None
        self._db: Optional[Any] = None
        self._graph: Optional[Any] = None
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Internal connection helpers
    # ------------------------------------------------------------------

    async def _get_graph(self) -> Any:
        """Return the FalkorDB Graph object, initialising lazily."""
        if self._graph is not None:
            return self._graph
        async with self._lock:
            if self._graph is not None:
                return self._graph
            self._pool = BlockingConnectionPool.from_url(
                self._url,
                max_connections=16,
                decode_responses=True,
            )
            self._db = FalkorDB(connection_pool=self._pool)
            self._graph = self._db.select_graph(self._graph_name)
        return self._graph

    async def _query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[List[Any]]:
        """Execute a Cypher query and return result_set rows."""
        graph = await self._get_graph()
        try:
            result = await graph.query(cypher, params or {})
            return result.result_set or []
        except Exception as exc:
            msg = str(exc)
            # Graph does not exist yet → treat as empty
            if "graph not found" in msg.lower() or "unknown graph" in msg.lower():
                return []
            logger.warning("FalkorDB query error: %s | query: %.200s", exc, cypher)
            raise

    # ------------------------------------------------------------------
    # Node serialisation
    # ------------------------------------------------------------------

    @staticmethod
    def _datapoint_to_props(node: DataPoint) -> Dict[str, Any]:
        raw: Dict[str, Any] = (
            node.model_dump() if hasattr(node, "model_dump") else vars(node)
        )
        node_id = str(raw.pop("id", ""))
        name = str(raw.pop("name", ""))
        node_type = str(raw.pop("type", type(node).__name__))
        # Remove any remaining Pydantic internal keys
        raw.pop("model_fields", None)
        raw.pop("model_config", None)
        return {
            "id": node_id,
            "name": name,
            "_node_type": node_type,
            "_props": _dumps(raw),
        }

    @staticmethod
    def _row_to_nodedata(props: Dict[str, Any]) -> NodeData:
        """Expand _props JSON and return a clean NodeData dict."""
        data = dict(props)
        return _expand_props(data)

    # ------------------------------------------------------------------
    # 1. is_empty
    # ------------------------------------------------------------------

    async def is_empty(self) -> bool:
        rows = await self._query("MATCH (n) RETURN n LIMIT 1")
        return len(rows) == 0

    # ------------------------------------------------------------------
    # 2. query  (raw Cypher passthrough)
    # ------------------------------------------------------------------

    async def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Any]:  # type: ignore[override]
        rows = await self._query(query, params)
        return rows

    # ------------------------------------------------------------------
    # 3. add_node
    # ------------------------------------------------------------------

    async def add_node(
        self,
        node: Union[DataPoint, str],
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        if isinstance(node, str):
            node_id = node
            props = dict(properties or {})
            name = str(props.pop("name", ""))
            node_type = str(props.pop("type", "Node"))
            cypher = (
                "MERGE (n:Node {id: $id}) "
                "SET n.name = $name, n._node_type = $nt, n._props = $props"
            )
            await self._query(cypher, {
                "id": node_id,
                "name": name,
                "nt": node_type,
                "props": _dumps(props),
            })
        else:
            p = self._datapoint_to_props(node)
            cypher = (
                "MERGE (n:Node {id: $id}) "
                "SET n.name = $name, n._node_type = $nt, n._props = $props"
            )
            await self._query(cypher, {
                "id": p["id"],
                "name": p["name"],
                "nt": p["_node_type"],
                "props": p["_props"],
            })

    # ------------------------------------------------------------------
    # 4. add_nodes
    # ------------------------------------------------------------------

    async def add_nodes(self, nodes: Union[List[Node], List[DataPoint]]) -> None:
        if not nodes:
            return
        first = nodes[0]
        if isinstance(first, tuple):
            # List[Node] = List[Tuple[str, NodeData]]
            for node_id, node_data in nodes:  # type: ignore[misc]
                data = dict(node_data)
                name = str(data.pop("name", ""))
                node_type = str(data.pop("type", "Node"))
                await self._query(
                    "MERGE (n:Node {id: $id}) "
                    "SET n.name = $name, n._node_type = $nt, n._props = $props",
                    {"id": str(node_id), "name": name, "nt": node_type, "props": _dumps(data)},
                )
        else:
            for node in nodes:
                await self.add_node(node)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # 5. delete_node
    # ------------------------------------------------------------------

    async def delete_node(self, node_id: str) -> None:
        await self._query(
            "MATCH (n:Node {id: $id}) DETACH DELETE n",
            {"id": node_id},
        )

    # ------------------------------------------------------------------
    # 6. delete_nodes
    # ------------------------------------------------------------------

    async def delete_nodes(self, node_ids: List[str]) -> None:
        if not node_ids:
            return
        await self._query(
            "MATCH (n:Node) WHERE n.id IN $ids DETACH DELETE n",
            {"ids": node_ids},
        )

    # ------------------------------------------------------------------
    # 7. get_node
    # ------------------------------------------------------------------

    async def get_node(self, node_id: str) -> Optional[NodeData]:
        rows = await self._query(
            "MATCH (n:Node {id: $id}) RETURN n",
            {"id": node_id},
        )
        if not rows:
            return None
        node_obj = rows[0][0]
        props = _node_obj_to_dict(node_obj)
        return self._row_to_nodedata(props)

    # ------------------------------------------------------------------
    # 8. get_nodes
    # ------------------------------------------------------------------

    async def get_nodes(self, node_ids: List[str]) -> List[NodeData]:
        if not node_ids:
            return []
        rows = await self._query(
            "MATCH (n:Node) WHERE n.id IN $ids RETURN n",
            {"ids": node_ids},
        )
        result = []
        for row in rows:
            props = _node_obj_to_dict(row[0])
            result.append(self._row_to_nodedata(props))
        return result

    # ------------------------------------------------------------------
    # 9. add_edge
    # ------------------------------------------------------------------

    async def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_name: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        props = dict(properties or {})
        # FalkorDB relationship type must be alphanumeric/underscore; sanitise.
        rel_type = _sanitise_rel_type(relationship_name)
        cypher = (
            "MATCH (a:Node {id: $src}), (b:Node {id: $dst}) "
            f"MERGE (a)-[r:{rel_type} {{_rel_name: $rel_name}}]->(b) "
            "SET r._props = $props"
        )
        await self._query(cypher, {
            "src": source_id,
            "dst": target_id,
            "rel_name": relationship_name,
            "props": _dumps(props),
        })

    # ------------------------------------------------------------------
    # 10. add_edges
    # ------------------------------------------------------------------

    async def add_edges(
        self,
        edges: Union[List[EdgeData], List[Tuple[str, str, str, Optional[Dict[str, Any]]]]],
    ) -> None:
        if not edges:
            return
        for edge in edges:
            if len(edge) >= 4:
                src, dst, rel, props = edge[0], edge[1], edge[2], edge[3]
            else:
                src, dst, rel = edge[0], edge[1], edge[2]
                props = {}
            await self.add_edge(str(src), str(dst), rel, props or {})

    # ------------------------------------------------------------------
    # 11. delete_graph
    # ------------------------------------------------------------------

    async def delete_graph(self) -> None:
        try:
            graph = await self._get_graph()
            await graph.delete()
        except Exception as exc:
            if "graph not found" in str(exc).lower():
                logger.warning("delete_graph: graph '%s' does not exist", self._graph_name)
            else:
                raise
        finally:
            # Reset so next operation recreates
            self._graph = None

    # ------------------------------------------------------------------
    # 12. get_graph_data
    # ------------------------------------------------------------------

    async def get_graph_data(self) -> Tuple[List[Node], List[EdgeData]]:
        start = time.time()
        try:
            node_rows = await self._query("MATCH (n:Node) RETURN n")
            formatted_nodes: List[Node] = []
            for row in node_rows:
                props = _node_obj_to_dict(row[0])
                node_id = props.get("id", "")
                data = self._row_to_nodedata(props)
                formatted_nodes.append((str(node_id), data))

            edge_rows = await self._query(
                "MATCH (a:Node)-[r]->(b:Node) "
                "RETURN a.id, b.id, r._rel_name, r._props"
            )
            formatted_edges: List[EdgeData] = []
            for row in edge_rows:
                src, dst, rel_name, props_str = row[0], row[1], row[2], row[3]
                ep = _loads_safe(props_str)
                formatted_edges.append((str(src), str(dst), str(rel_name or ""), ep))

            if formatted_nodes and not formatted_edges:
                # Visualisation compatibility: add self-loop placeholders
                for nid, _ in formatted_nodes:
                    formatted_edges.append((nid, nid, "SELF", {
                        "relationship_name": "SELF",
                        "relationship_type": "SELF",
                        "vector_distance": 0.0,
                    }))

            logger.info(
                "get_graph_data: %d nodes, %d edges in %.2fs",
                len(formatted_nodes), len(formatted_edges), time.time() - start,
            )
            return formatted_nodes, formatted_edges
        except Exception as exc:
            logger.error("get_graph_data failed: %s", exc)
            raise

    # ------------------------------------------------------------------
    # 13. get_graph_metrics
    # ------------------------------------------------------------------

    async def get_graph_metrics(self, include_optional: bool = False) -> Dict[str, Any]:
        try:
            node_rows = await self._query("MATCH (n:Node) RETURN count(n)")
            num_nodes = int(node_rows[0][0]) if node_rows else 0

            edge_rows = await self._query("MATCH ()-[r]->() RETURN count(r)")
            num_edges = int(edge_rows[0][0]) if edge_rows else 0

            metrics: Dict[str, Any] = {
                "num_nodes": num_nodes,
                "num_edges": num_edges,
                "mean_degree": (2 * num_edges) / num_nodes if num_nodes else None,
                "edge_density": num_edges / (num_nodes * (num_nodes - 1)) if num_nodes > 1 else 0,
                "num_connected_components": -1,
                "sizes_of_connected_components": [],
                "num_selfloops": -1,
                "diameter": -1,
                "avg_shortest_path_length": -1,
                "avg_clustering": -1,
            }

            if include_optional:
                sl_rows = await self._query(
                    "MATCH (n:Node)-[r]->(n) RETURN count(r)"
                )
                metrics["num_selfloops"] = int(sl_rows[0][0]) if sl_rows else 0

            return metrics
        except Exception as exc:
            logger.error("get_graph_metrics failed: %s", exc)
            return {
                "num_nodes": 0,
                "num_edges": 0,
                "mean_degree": 0,
                "edge_density": 0,
                "num_connected_components": 0,
                "sizes_of_connected_components": [],
                "num_selfloops": -1,
                "diameter": -1,
                "avg_shortest_path_length": -1,
                "avg_clustering": -1,
            }

    # ------------------------------------------------------------------
    # 14. has_edge
    # ------------------------------------------------------------------

    async def has_edge(self, source_id: str, target_id: str, relationship_name: str) -> bool:
        rows = await self._query(
            "MATCH (a:Node {id: $src})-[r {_rel_name: $rel}]->(b:Node {id: $dst}) "
            "RETURN count(r) > 0",
            {"src": source_id, "dst": target_id, "rel": relationship_name},
        )
        if not rows:
            return False
        return bool(rows[0][0])

    # ------------------------------------------------------------------
    # 15. has_edges
    # ------------------------------------------------------------------

    async def has_edges(self, edges: List[EdgeData]) -> List[EdgeData]:
        if not edges:
            return []
        existing: List[EdgeData] = []
        for edge in edges:
            if len(edge) >= 4:
                src, dst, rel, props = edge[0], edge[1], edge[2], edge[3]
            else:
                src, dst, rel = edge[0], edge[1], edge[2]
                props = {}
            if await self.has_edge(str(src), str(dst), rel):
                existing.append((str(src), str(dst), rel, props))
        return existing

    # ------------------------------------------------------------------
    # 16. get_edges
    # ------------------------------------------------------------------

    async def get_edges(self, node_id: str) -> List[EdgeData]:
        rows = await self._query(
            "MATCH (a:Node {id: $id})-[r]-(b:Node) "
            "RETURN a.id, b.id, r._rel_name, r._props",
            {"id": node_id},
        )
        result: List[EdgeData] = []
        for row in rows:
            src, dst, rel, props_str = row[0], row[1], row[2], row[3]
            ep = _loads_safe(props_str)
            result.append((str(src), str(dst), str(rel or ""), ep))
        return result

    # ------------------------------------------------------------------
    # 17. get_neighbors
    # ------------------------------------------------------------------

    async def get_neighbors(self, node_id: str) -> List[NodeData]:
        rows = await self._query(
            "MATCH (n:Node {id: $id})-[]-(m:Node) RETURN DISTINCT m",
            {"id": node_id},
        )
        result: List[NodeData] = []
        for row in rows:
            props = _node_obj_to_dict(row[0])
            result.append(self._row_to_nodedata(props))
        return result

    # ------------------------------------------------------------------
    # 18. get_nodeset_subgraph
    # ------------------------------------------------------------------

    async def get_nodeset_subgraph(
        self,
        node_type: Type[Any],
        node_name: List[str],
        node_name_filter_operator: str = "OR",
    ) -> Tuple[List[Tuple[str, dict]], List[Tuple[str, str, str, dict]]]:
        label = node_type.__name__
        primary_rows = await self._query(
            "MATCH (n:Node) "
            "WHERE n._node_type = $label AND n.name IN $names "
            "RETURN DISTINCT n.id",
            {"label": label, "names": node_name},
        )
        primary_ids: List[str] = [str(row[0]) for row in primary_rows]
        if not primary_ids:
            return [], []

        if node_name_filter_operator == "OR":
            nbr_rows = await self._query(
                "MATCH (n:Node)-[]-(m:Node) "
                "WHERE n.id IN $ids "
                "RETURN DISTINCT m.id",
                {"ids": primary_ids},
            )
            neighbor_ids: List[str] = [str(row[0]) for row in nbr_rows]
        else:
            # AND operator: neighbour must be connected to ALL primary nodes
            nbr_rows = await self._query(
                "MATCH (n:Node)-[]-(m:Node) "
                "WHERE n.id IN $ids "
                "WITH m.id AS mid, count(DISTINCT n.id) AS cnt "
                "WHERE cnt = $cnt "
                "RETURN mid",
                {"ids": primary_ids, "cnt": len(primary_ids)},
            )
            neighbor_ids = [str(row[0]) for row in nbr_rows]

        all_ids = list(set(primary_ids) | set(neighbor_ids))

        node_rows = await self._query(
            "MATCH (n:Node) WHERE n.id IN $ids RETURN n",
            {"ids": all_ids},
        )
        nodes: List[Tuple[str, dict]] = []
        for row in node_rows:
            props = _node_obj_to_dict(row[0])
            nid = str(props.get("id", ""))
            data = self._row_to_nodedata(props)
            nodes.append((nid, data))

        edge_rows = await self._query(
            "MATCH (a:Node)-[r]->(b:Node) "
            "WHERE a.id IN $ids AND b.id IN $ids "
            "RETURN a.id, b.id, r._rel_name, r._props",
            {"ids": all_ids},
        )
        edges: List[Tuple[str, str, str, dict]] = []
        for row in edge_rows:
            src, dst, rel, props_str = row[0], row[1], row[2], row[3]
            ep = _loads_safe(props_str)
            edges.append((str(src), str(dst), str(rel or ""), ep))

        return nodes, edges

    # ------------------------------------------------------------------
    # 19. get_connections
    # ------------------------------------------------------------------

    async def get_connections(
        self, node_id: Union[str, UUID]
    ) -> List[Tuple[NodeData, Dict[str, Any], NodeData]]:
        nid = str(node_id)
        rows = await self._query(
            "MATCH (a:Node {id: $id})-[r]-(b:Node) "
            "RETURN a, r, b",
            {"id": nid},
        )
        result: List[Tuple[NodeData, Dict[str, Any], NodeData]] = []
        for row in rows:
            a_props = _expand_props(_node_obj_to_dict(row[0]))
            r_props = _edge_obj_to_dict(row[1])
            r_name = r_props.pop("_rel_name", "")
            r_extra = _loads_safe(r_props.pop("_props", None))
            rel_data: Dict[str, Any] = {"relationship_name": r_name, **r_extra}
            b_props = _expand_props(_node_obj_to_dict(row[2]))
            result.append((a_props, rel_data, b_props))
        return result

    # ------------------------------------------------------------------
    # 20. get_neighborhood
    # ------------------------------------------------------------------

    async def get_neighborhood(
        self,
        node_ids: List[str],
        depth: int = 1,
        edge_types: Optional[List[str]] = None,
    ) -> Tuple[List[Node], List[EdgeData]]:
        if not node_ids:
            return [], []
        start = time.time()
        try:
            # Variable-length path traversal to collect all neighbour IDs
            # FalkorDB supports OpenCypher variable-length patterns
            path_cypher = (
                f"MATCH (seed:Node)-[*1..{depth}]-(neighbor:Node) "
                "WHERE seed.id IN $ids "
                "RETURN DISTINCT neighbor.id"
            )
            nbr_rows = await self._query(path_cypher, {"ids": node_ids})
            neighbor_ids = [str(r[0]) for r in nbr_rows]
            all_ids = list(set(node_ids) | set(neighbor_ids))

            node_rows = await self._query(
                "MATCH (n:Node) WHERE n.id IN $ids RETURN n",
                {"ids": all_ids},
            )
            formatted_nodes: List[Node] = []
            for row in node_rows:
                props = _node_obj_to_dict(row[0])
                nid = str(props.get("id", ""))
                data = self._row_to_nodedata(props)
                formatted_nodes.append((nid, data))

            if not formatted_nodes:
                return [], []

            edge_filter = ""
            edge_params: Dict[str, Any] = {"ids": all_ids}
            if edge_types:
                edge_filter = " AND r._rel_name IN $etypes"
                edge_params["etypes"] = edge_types

            edge_rows = await self._query(
                "MATCH (a:Node)-[r]->(b:Node) "
                f"WHERE a.id IN $ids AND b.id IN $ids{edge_filter} "
                "RETURN a.id, b.id, r._rel_name, r._props",
                edge_params,
            )
            formatted_edges: List[EdgeData] = []
            for row in edge_rows:
                src, dst, rel, props_str = row[0], row[1], row[2], row[3]
                ep = _loads_safe(props_str)
                formatted_edges.append((str(src), str(dst), str(rel or ""), ep))

            logger.info(
                "get_neighborhood (%d-hop): %d nodes, %d edges in %.2fs",
                depth, len(formatted_nodes), len(formatted_edges), time.time() - start,
            )
            return formatted_nodes, formatted_edges
        except Exception as exc:
            logger.error("get_neighborhood failed: %s", exc)
            raise

    # ------------------------------------------------------------------
    # 21. get_filtered_graph_data
    # ------------------------------------------------------------------

    async def get_filtered_graph_data(
        self,
        attribute_filters: List[Dict[str, List[Union[str, int]]]],
    ) -> Tuple[List[Node], List[EdgeData]]:
        where_parts: List[str] = []
        params: Dict[str, Any] = {}

        for i, fdict in enumerate(attribute_filters):
            for attr, values in fdict.items():
                key = f"v_{i}_{attr}"
                where_parts.append(f"n.{attr} IN ${key}")
                params[key] = values

        if not where_parts:
            return await self.get_graph_data()

        where_clause = " AND ".join(where_parts)
        node_rows = await self._query(
            f"MATCH (n:Node) WHERE {where_clause} RETURN n",
            params,
        )
        formatted_nodes: List[Node] = []
        node_id_set: Set[str] = set()
        for row in node_rows:
            props = _node_obj_to_dict(row[0])
            nid = str(props.get("id", ""))
            data = self._row_to_nodedata(props)
            formatted_nodes.append((nid, data))
            node_id_set.add(nid)

        if not formatted_nodes:
            return [], []

        edge_rows = await self._query(
            "MATCH (a:Node)-[r]->(b:Node) "
            "WHERE a.id IN $ids AND b.id IN $ids "
            "RETURN a.id, b.id, r._rel_name, r._props",
            {"ids": list(node_id_set)},
        )
        formatted_edges: List[EdgeData] = []
        for row in edge_rows:
            src, dst, rel, props_str = row[0], row[1], row[2], row[3]
            ep = _loads_safe(props_str)
            formatted_edges.append((str(src), str(dst), str(rel or ""), ep))

        return formatted_nodes, formatted_edges

    # ------------------------------------------------------------------
    # 22. get_node_feedback_weights  (optional)
    # ------------------------------------------------------------------

    async def get_node_feedback_weights(self, node_ids: List[str]) -> Dict[str, float]:
        if not node_ids:
            return {}
        nodes = await self.get_nodes(node_ids)
        result: Dict[str, float] = {}
        for node in nodes:
            nid = node.get("id")
            if isinstance(nid, str):
                try:
                    result[nid] = float(node.get("feedback_weight", 0.5))
                except (TypeError, ValueError):
                    result[nid] = 0.5
        return result

    # ------------------------------------------------------------------
    # 23. set_node_feedback_weights  (optional)
    # ------------------------------------------------------------------

    async def set_node_feedback_weights(
        self, node_feedback_weights: Dict[str, float]
    ) -> Dict[str, bool]:
        if not node_feedback_weights:
            return {}
        result: Dict[str, bool] = {}
        nodes = await self.get_nodes(list(node_feedback_weights.keys()))
        for node in nodes:
            nid = str(node.get("id", ""))
            if nid not in node_feedback_weights:
                continue
            # Reconstruct _props with updated feedback_weight
            extra = {k: v for k, v in node.items() if k not in {"id", "name", "_node_type"}}
            extra["feedback_weight"] = float(node_feedback_weights[nid])
            try:
                await self._query(
                    "MATCH (n:Node {id: $id}) SET n._props = $props",
                    {"id": nid, "props": _dumps(extra)},
                )
                result[nid] = True
            except Exception as exc:
                logger.warning("set_node_feedback_weights failed for %s: %s", nid, exc)
                result[nid] = False
        for nid in node_feedback_weights:
            if nid not in result:
                result[nid] = False
        return result

    # ------------------------------------------------------------------
    # 24. get_edge_feedback_weights  (optional)
    # ------------------------------------------------------------------

    async def get_edge_feedback_weights(self, edge_object_ids: List[str]) -> Dict[str, float]:
        if not edge_object_ids:
            return {}
        # edge_object_id is stored inside _props JSON
        rows = await self._query(
            "MATCH ()-[r]->() RETURN r._rel_name, r._props"
        )
        result: Dict[str, float] = {}
        target_set = set(edge_object_ids)
        for row in rows:
            props_str = row[1] if len(row) > 1 else None
            ep = _loads_safe(props_str)
            eid = ep.get("edge_object_id")
            if eid and eid in target_set:
                try:
                    result[eid] = float(ep.get("feedback_weight", 0.5))
                except (TypeError, ValueError):
                    result[eid] = 0.5
        return result

    # ------------------------------------------------------------------
    # 25. set_edge_feedback_weights  (optional)
    # ------------------------------------------------------------------

    async def set_edge_feedback_weights(
        self, edge_feedback_weights: Dict[str, float]
    ) -> Dict[str, bool]:
        if not edge_feedback_weights:
            return {}
        rows = await self._query(
            "MATCH (a:Node)-[r]->(b:Node) RETURN a.id, b.id, r._rel_name, r._props"
        )
        result: Dict[str, bool] = {eid: False for eid in edge_feedback_weights}
        for row in rows:
            src, dst, rel, props_str = row[0], row[1], row[2], row[3]
            ep = _loads_safe(props_str)
            eid = ep.get("edge_object_id")
            if eid and eid in edge_feedback_weights:
                ep["feedback_weight"] = float(edge_feedback_weights[eid])
                rel_type = _sanitise_rel_type(rel or "REL")
                try:
                    await self._query(
                        f"MATCH (a:Node {{id: $src}})-[r:{rel_type} {{_rel_name: $rel}}]->(b:Node {{id: $dst}}) "
                        "SET r._props = $props",
                        {"src": str(src), "dst": str(dst), "rel": str(rel), "props": _dumps(ep)},
                    )
                    result[eid] = True
                except Exception as exc:
                    logger.warning("set_edge_feedback_weights failed for %s: %s", eid, exc)
        return result

    # ------------------------------------------------------------------
    # 26. get_triplets_batch  (optional)
    # ------------------------------------------------------------------

    async def get_triplets_batch(self, offset: int, limit: int) -> List[Dict[str, Any]]:
        if offset < 0:
            raise ValueError(f"offset must be non-negative, got {offset}")
        if limit < 0:
            raise ValueError(f"limit must be non-negative, got {limit}")
        rows = await self._query(
            "MATCH (a:Node)-[r]->(b:Node) "
            "RETURN a, r, b "
            f"SKIP {offset} LIMIT {limit}"
        )
        triplets: List[Dict[str, Any]] = []
        for row in rows:
            a_props = _expand_props(_node_obj_to_dict(row[0]))
            r_props = _edge_obj_to_dict(row[1])
            rel_name = r_props.pop("_rel_name", "")
            r_extra = _loads_safe(r_props.pop("_props", None))
            b_props = _expand_props(_node_obj_to_dict(row[2]))
            triplets.append({
                "start_node": a_props,
                "relationship_properties": {"relationship_name": rel_name, **r_extra},
                "end_node": b_props,
            })
        return triplets


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _sanitise_rel_type(name: str) -> str:
    """
    FalkorDB relationship types must match [A-Za-z_][A-Za-z0-9_]*.
    Replace any illegal character with underscore and ensure the result
    is not empty.
    """
    if not name:
        return "REL"
    sanitised = "".join(c if c.isalnum() or c == "_" else "_" for c in name)
    if sanitised[0].isdigit():
        sanitised = "R_" + sanitised
    return sanitised or "REL"
