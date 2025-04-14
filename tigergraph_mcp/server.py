# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import (
    TigerGraphToolNames,
    get_all_tools,
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
)

logger = logging.getLogger(__name__)


async def serve() -> None:
    server = Server("TigerGraph-MCP")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return get_all_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            match name:
                # Tools for Schema Operations
                case TigerGraphToolNames.CREATE_SCHEMA:
                    return await create_schema(**arguments)
                case TigerGraphToolNames.GET_SCHEMA:
                    return await get_schema(**arguments)
                case TigerGraphToolNames.DROP_GRAPH:
                    return await drop_graph(**arguments)
                # Tools for Data Operations
                case TigerGraphToolNames.LOAD_DATA:
                    return await load_data(**arguments)
                # Tools for Node Operations
                case TigerGraphToolNames.ADD_NODE:
                    return await add_node(**arguments)
                case TigerGraphToolNames.ADD_NODES:
                    return await add_nodes(**arguments)
                case TigerGraphToolNames.REMOVE_NODE:
                    return await remove_node(**arguments)
                case TigerGraphToolNames.HAS_NODE:
                    return await has_node(**arguments)
                case TigerGraphToolNames.GET_NODE_DATA:
                    return await get_node_data(**arguments)
                case TigerGraphToolNames.GET_NODE_EDGES:
                    return await get_node_edges(**arguments)
                case TigerGraphToolNames.CLEAR_GRAPH_DATA:
                    return await clear_graph_data(**arguments)
                # Tools for Edge Operations
                # Tools for Query Operations
                # Tools for Vector Operations
                case _:
                    raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.exception("Error in tool execution")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
