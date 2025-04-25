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
    # Edge Operations
    ADD_EDGE = "graph/add_edge"
    ADD_EDGES = "graph/add_edges_from"
    HAS_EDGE = "graph/has_edge"
    GET_EDGE_DATA = "graph/get_edge_data"
    # Statistics Operations
    DEGREE = "graph/degree"
    NUMBER_OF_NODES = "graph/number_of_nodes"
    NUMBER_OF_EDGES = "graph/number_of_edges"
    # Query Operations
    GET_NODES = "graph/get_nodes"
    GET_NEIGHBORS = "graph/get_neighbors"
    BREADTH_FIRST_SEARCH = "graph/breadth_first_search"
    RUN_QUERY = "graph/run_query"
    # Vector Operations
    UPSERT = "graph/upsert"
    FETCH_NODE = "graph/fetch_node"
    FETCH_NODES = "graph/fetch_nodes"
    SEARCH = "graph/search"
    SEARCH_MULTI_VECTOR_ATTRIBUTES = "graph/search_multi_vector_attributes"
    SEARCH_TOP_K_SIMILAR_NODES = "graph/search_top_k_similar_nodes"

    @classmethod
    def from_value(cls, value: str) -> Optional["TigerGraphToolName"]:
        try:
            return cls(value)
        except ValueError:
            return None
