from enum import Enum
from typing import Optional


class TigerGraphToolName(str, Enum):
    # -------------------- Graph Operations --------------------
    # Schema Operations
    CREATE_SCHEMA = "graph__create_schema"
    GET_SCHEMA = "graph__get_schema"
    DROP_GRAPH = "graph__drop_graph"
    # Data Operations
    LOAD_DATA = "graph__load_data"
    # Node Operations
    ADD_NODE = "graph__add_node"
    ADD_NODES = "graph__add_nodes"
    REMOVE_NODE = "graph__remove_node"
    HAS_NODE = "graph__has_node"
    GET_NODE_DATA = "graph__get_node_data"
    GET_NODE_EDGES = "graph__get_node_edges"
    CLEAR_GRAPH_DATA = "graph__clear_graph_data"
    # Edge Operations
    ADD_EDGE = "graph__add_edge"
    ADD_EDGES = "graph__add_edges_from"
    HAS_EDGE = "graph__has_edge"
    GET_EDGE_DATA = "graph__get_edge_data"
    # Statistics Operations
    DEGREE = "graph__degree"
    NUMBER_OF_NODES = "graph__number_of_nodes"
    NUMBER_OF_EDGES = "graph__number_of_edges"
    # Query Operations
    CREATE_QUERY = "graph__create_query"
    INSTALL_QUERY = "graph__install_query"
    DROP_QUERY = "graph__drop_query"
    RUN_QUERY = "graph__run_query"
    GET_NODES = "graph__get_nodes"
    GET_NEIGHBORS = "graph__get_neighbors"
    BREADTH_FIRST_SEARCH = "graph__breadth_first_search"
    # Vector Operations
    UPSERT = "graph__upsert"
    FETCH_NODE = "graph__fetch_node"
    FETCH_NODES = "graph__fetch_nodes"
    SEARCH = "graph__search"
    SEARCH_MULTI_VECTOR_ATTRIBUTES = "graph__search_multi_vector_attributes"
    SEARCH_TOP_K_SIMILAR_NODES = "graph__search_top_k_similar_nodes"

    # -------------------- Database Operations --------------------
    # GSQL Operations
    LIST_METADATA = "list_metadata"
    # Data Source Operations
    CREATE_DATA_SOURCE = "db__create_data_source"
    UPDATE_DATA_SOURCE = "db__update_data_source"
    GET_DATA_SOURCE = "db__get_data_source"
    DROP_DATA_SOURCE = "db__drop_data_source"
    GET_ALL_DATA_SOURCES = "get_all_data_sources"
    DROP_ALL_DATA_SOURCES = "drop_all_data_sources"
    PREVIEW_SAMPLE_DATA = "db__preview_sample_data"

    @classmethod
    def from_value(cls, value: str) -> Optional["TigerGraphToolName"]:
        try:
            return cls(value)
        except ValueError:
            return None
