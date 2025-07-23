# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from mcp.types import Tool

from .graph.schema import (
    create_schema_tool,
    get_schema_tool,
    drop_graph_tool,
)
from .graph.data import (
    load_data_tool,
)
from .graph.node import (
    add_node_tool,
    add_nodes_tool,
    remove_node_tool,
    has_node_tool,
    get_node_data_tool,
    get_node_edges_tool,
    clear_graph_data_tool,
)
from .graph.edge import (
    add_edge_tool,
    add_edges_tool,
    has_edge_tool,
    get_edge_data_tool,
)
from .graph.statistics import (
    degree_tool,
    number_of_nodes_tool,
    number_of_edges_tool,
)
from .graph.query import (
    create_query_tool,
    install_query_tool,
    drop_query_tool,
    run_query_tool,
    get_nodes_tool,
    get_neighbors_tool,
    breadth_first_search_tool,
)
from .graph.vector import (
    upsert_tool,
    fetch_node_tool,
    fetch_nodes_tool,
    search_tool,
    search_multi_vector_attributes_tool,
    search_top_k_similar_nodes_tool,
)
from .db.gsql import list_metadata_tool
from .db.data_source import (
    create_data_source_tool,
    update_data_source_tool,
    get_data_source_tool,
    drop_data_source_tool,
    get_all_data_sources_tool,
    drop_all_data_sources_tool,
    preview_sample_data_tool,
)


def get_all_tools() -> list[Tool]:
    return (
        # Tools for Schema Operations
        create_schema_tool.tools
        + get_schema_tool.tools
        + drop_graph_tool.tools
        # Tools for Data Operations
        + load_data_tool.tools
        # Tools for Node Operations
        + add_node_tool.tools
        + add_nodes_tool.tools
        + remove_node_tool.tools
        + has_node_tool.tools
        + get_node_data_tool.tools
        + get_node_edges_tool.tools
        + clear_graph_data_tool.tools
        # Tools for Edge Operations
        + add_edge_tool.tools
        + add_edges_tool.tools
        + has_edge_tool.tools
        + get_edge_data_tool.tools
        # Tools for Statistics Operations
        + degree_tool.tools
        + number_of_nodes_tool.tools
        + number_of_edges_tool.tools
        # Tools for Query Operations
        + create_query_tool.tools
        + install_query_tool.tools
        + drop_query_tool.tools
        + run_query_tool.tools
        + get_nodes_tool.tools
        + get_neighbors_tool.tools
        + breadth_first_search_tool.tools
        # Tools for Vector Operations
        + upsert_tool.tools
        + fetch_node_tool.tools
        + fetch_nodes_tool.tools
        + search_tool.tools
        + search_multi_vector_attributes_tool.tools
        + search_top_k_similar_nodes_tool.tools
        # Tools for GSQL Operations
        + list_metadata_tool.tools
        # Tools for Data Source Operations
        + create_data_source_tool.tools
        + update_data_source_tool.tools
        + get_data_source_tool.tools
        + drop_data_source_tool.tools
        + get_all_data_sources_tool.tools
        + drop_all_data_sources_tool.tools
        + preview_sample_data_tool.tools
    )
