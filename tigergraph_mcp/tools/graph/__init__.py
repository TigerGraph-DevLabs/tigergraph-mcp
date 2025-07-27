# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from .schema import (
    create_schema,
    get_schema,
    drop_graph,
)
from .data import (
    load_data,
)
from .node import (
    add_node,
    add_nodes,
    remove_node,
    has_node,
    get_node_data,
    get_node_edges,
    clear_graph_data,
)
from .edge import (
    add_edge,
    add_edges,
    has_edge,
    get_edge_data,
)
from .statistics import (
    degree,
    number_of_nodes,
    number_of_edges,
)
from .query import (
    create_query,
    install_query,
    drop_query,
    run_query,
    get_nodes,
    get_neighbors,
    breadth_first_search,
)
from .vector import (
    upsert,
    fetch_node,
    fetch_nodes,
    search,
    search_multi_vector_attributes,
    search_top_k_similar_nodes,
)


__all__ = [
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
]
