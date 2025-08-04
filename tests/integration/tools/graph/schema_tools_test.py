import time
import pytest

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from tigergraph_mcp import TigerGraphToolName

from tests.integration.base_graph_fixture import BaseFixture


class TestSchemaTools(BaseFixture):
    @pytest.mark.asyncio
    async def test_schema_tools(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()

                # Create Schema
                graph_name = "Social"
                create_result = await session.call_tool(
                    TigerGraphToolName.CREATE_SCHEMA,
                    arguments={
                        "graph_schema": {
                            "graph_name": graph_name,
                            "nodes": {
                                "Person": {
                                    "primary_key": "name",
                                    "attributes": {
                                        "name": "STRING",
                                        "age": "UINT",
                                        "gender": "STRING",
                                    },
                                },
                            },
                            "edges": {
                                "Friendship": {
                                    "is_directed_edge": False,
                                    "from_node_type": "Person",
                                    "to_node_type": "Person",
                                    "attributes": {
                                        "closeness": "DOUBLE",
                                    },
                                },
                            },
                        },
                    },
                )
                assert "✅ Schema for graph 'Social' created successfully." in str(
                    create_result
                )

                # Get Schema
                time.sleep(3)
                get_result = await session.call_tool(
                    TigerGraphToolName.GET_SCHEMA,
                    arguments={
                        "graph_name": graph_name,
                    },
                )
                assert "Person" in str(get_result)

                # Drop Graph
                drop_result = await session.call_tool(
                    TigerGraphToolName.DROP_GRAPH,
                    arguments={
                        "graph_name": graph_name,
                    },
                )
                assert "✅" in str(drop_result)

    @pytest.mark.asyncio
    async def test_reserved_keyword_in_node_attribute(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                graph_name = "TestReservedKeyword"
                # Use a reserved keyword "type" as an attribute name
                create_result = await session.call_tool(
                    TigerGraphToolName.CREATE_SCHEMA,
                    arguments={
                        "graph_schema": {
                            "graph_name": graph_name,
                            "nodes": {
                                "Entity": {
                                    "primary_key": "id",
                                    "attributes": {
                                        "id": "STRING",
                                        "type": "STRING",  # Reserved keyword
                                    },
                                },
                            },
                            "edges": {},
                        }
                    },
                )
                assert "Schema creation failed:" in str(create_result)
                assert "Attribute name 'type' is a reserved keyword." in str(create_result)
