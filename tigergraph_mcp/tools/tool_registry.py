# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from mcp.types import Tool

from .schema import (
    create_schema_tool,
    get_schema_tool,
    drop_graph_tool,
)
from .data import load_data_tool
from .node import (
    add_node_tool,
    add_nodes_tool,
    remove_node_tool,
    has_node_tool,
    get_node_data_tool,
    get_node_edges_tool,
    clear_graph_data_tool,
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
    )
