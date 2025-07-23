# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from .tigergraph_tool_names import TigerGraphToolName
from .tool_registry import get_all_tools
from .graph import (
    create_schema,
    get_schema,
    drop_graph,
    load_data,
    add_node,
    add_nodes,
    remove_node,
    has_node,
    get_node_data,
    get_node_edges,
    clear_graph_data,
    add_edge,
    add_edges,
    has_edge,
    get_edge_data,
    degree,
    number_of_nodes,
    number_of_edges,
    create_query,
    install_query,
    drop_query,
    run_query,
    get_nodes,
    get_neighbors,
    breadth_first_search,
    upsert,
    fetch_node,
    fetch_nodes,
    search,
    search_multi_vector_attributes,
    search_top_k_similar_nodes,
)
from .db import (
    list_metadata,
    create_data_source,
    update_data_source,
    get_data_source,
    drop_data_source,
    get_all_data_sources,
    drop_all_data_sources,
    preview_sample_data,
)

__all__ = [
    # TigerGraph Tool Names
    "TigerGraphToolName",
    # Get All Tools
    "get_all_tools",
    # Tools for Schema Operations
    "create_schema",
    "get_schema",
    "drop_graph",
    # Tools for Data Operations
    "load_data",
    # Tools for Node Operations
    "add_node",
    "add_nodes",
    "remove_node",
    "has_node",
    "get_node_data",
    "has_node",
    "get_node_edges",
    "clear_graph_data",
    # Tools for Edge Operations
    "add_edge",
    "add_edges",
    "has_edge",
    "get_edge_data",
    # Tools for Statistics Operations
    "degree",
    "number_of_nodes",
    "number_of_edges",
    # Tools for Query Operations
    "create_query",
    "install_query",
    "drop_query",
    "run_query",
    "get_nodes",
    "get_neighbors",
    "breadth_first_search",
    # Tools for Vector Operations
    "upsert",
    "fetch_node",
    "fetch_nodes",
    "search",
    "search_multi_vector_attributes",
    "search_top_k_similar_nodes",
    # Tools for GSQL Operations
    "list_metadata",
    # Tools for Data Source Operations
    "create_data_source",
    "update_data_source",
    "get_data_source",
    "drop_data_source",
    "get_all_data_sources",
    "drop_all_data_sources",
    "preview_sample_data",
]
