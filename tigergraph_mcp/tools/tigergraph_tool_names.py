from enum import Enum
from typing import Optional


class TigerGraphToolName(str, Enum):
    # Schema Operations
    CREATE_SCHEMA = "graph/create_schema"
    GET_SCHEMA = "graph/get_schema"
    DROP_GRAPH = "graph/drop_graph"
    # Data Operations
    LOAD_DATA = "graph/load_data"
    # Node Operations
    ADD_NODE = "graph/add_node"
    ADD_NODES = "graph/add_nodes"
    CLEAR_GRAPH_DATA = "graph/clear_graph_data"
    GET_NODE_DATA = "graph/get_node_data"
    GET_NODE_EDGES = "graph/get_node_edges"
    HAS_NODE = "graph/has_node"
    REMOVE_NODE = "graph/remove_node"

    @classmethod
    def from_value(cls, value: str) -> Optional["TigerGraphToolName"]:
        try:
            return cls(value)
        except ValueError:
            return None
