# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import logging
from typing import Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import (
    TigerGraphToolName,
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
    list_metadata,
    create_data_source,
    update_data_source,
    get_data_source,
    drop_data_source,
    get_all_data_sources,
    drop_all_data_sources,
    preview_sample_data,
)

logger = logging.getLogger(__name__)


async def serve() -> None:
    server = Server("TigerGraph-MCP")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return get_all_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict) -> List[TextContent]:
        try:
            match name:
                # Tools for Schema Operations
                case TigerGraphToolName.CREATE_SCHEMA:
                    return await create_schema(**arguments)
                case TigerGraphToolName.GET_SCHEMA:
                    return await get_schema(**arguments)
                case TigerGraphToolName.DROP_GRAPH:
                    return await drop_graph(**arguments)
                # Tools for Data Operations
                case TigerGraphToolName.LOAD_DATA:
                    return await load_data(**arguments)
                # Tools for Node Operations
                case TigerGraphToolName.ADD_NODE:
                    return await add_node(**arguments)
                case TigerGraphToolName.ADD_NODES:
                    return await add_nodes(**arguments)
                case TigerGraphToolName.REMOVE_NODE:
                    return await remove_node(**arguments)
                case TigerGraphToolName.HAS_NODE:
                    return await has_node(**arguments)
                case TigerGraphToolName.GET_NODE_DATA:
                    return await get_node_data(**arguments)
                case TigerGraphToolName.GET_NODE_EDGES:
                    return await get_node_edges(**arguments)
                case TigerGraphToolName.CLEAR_GRAPH_DATA:
                    return await clear_graph_data(**arguments)
                # Tools for Edge Operations
                case TigerGraphToolName.ADD_EDGE:
                    return await add_edge(**arguments)
                case TigerGraphToolName.ADD_EDGES:
                    return await add_edges(**arguments)
                case TigerGraphToolName.HAS_EDGE:
                    return await has_edge(**arguments)
                case TigerGraphToolName.GET_EDGE_DATA:
                    return await get_edge_data(**arguments)
                # Tools for Statistics Operations
                case TigerGraphToolName.DEGREE:
                    return await degree(**arguments)
                case TigerGraphToolName.NUMBER_OF_NODES:
                    return await number_of_nodes(**arguments)
                case TigerGraphToolName.NUMBER_OF_EDGES:
                    return await number_of_edges(**arguments)
                # Tools for Query Operations
                case TigerGraphToolName.CREATE_QUERY:
                    return await create_query(**arguments)
                case TigerGraphToolName.INSTALL_QUERY:
                    return await install_query(**arguments)
                case TigerGraphToolName.DROP_QUERY:
                    return await drop_query(**arguments)
                case TigerGraphToolName.RUN_QUERY:
                    return await run_query(**arguments)
                case TigerGraphToolName.GET_NODES:
                    return await get_nodes(**arguments)
                case TigerGraphToolName.GET_NEIGHBORS:
                    return await get_neighbors(**arguments)
                case TigerGraphToolName.BREADTH_FIRST_SEARCH:
                    return await breadth_first_search(**arguments)
                # Tools for Vector Operations
                case TigerGraphToolName.UPSERT:
                    return await upsert(**arguments)
                case TigerGraphToolName.FETCH_NODE:
                    return await fetch_node(**arguments)
                case TigerGraphToolName.FETCH_NODES:
                    return await fetch_nodes(**arguments)
                case TigerGraphToolName.SEARCH:
                    return await search(**arguments)
                case TigerGraphToolName.SEARCH_MULTI_VECTOR_ATTRIBUTES:
                    return await search_multi_vector_attributes(**arguments)
                case TigerGraphToolName.SEARCH_TOP_K_SIMILAR_NODES:
                    return await search_top_k_similar_nodes(**arguments)
                case TigerGraphToolName.LIST_METADATA:
                    return await list_metadata(**arguments)
                case TigerGraphToolName.CREATE_DATA_SOURCE:
                    return await create_data_source(**arguments)
                case TigerGraphToolName.UPDATE_DATA_SOURCE:
                    return await update_data_source(**arguments)
                case TigerGraphToolName.GET_DATA_SOURCE:
                    return await get_data_source(**arguments)
                case TigerGraphToolName.DROP_DATA_SOURCE:
                    return await drop_data_source(**arguments)
                case TigerGraphToolName.GET_ALL_DATA_SOURCES:
                    return await get_all_data_sources(**arguments)
                case TigerGraphToolName.DROP_ALL_DATA_SOURCES:
                    return await drop_all_data_sources(**arguments)
                case TigerGraphToolName.PREVIEW_SAMPLE_DATA:
                    return await preview_sample_data(**arguments)
                case _:
                    raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.exception("Error in tool execution")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
