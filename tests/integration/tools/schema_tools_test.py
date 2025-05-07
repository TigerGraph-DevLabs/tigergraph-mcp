import time
import pytest

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from tests.integration.base_graph_fixture import BaseGraphFixture


class TestSchemaTools(BaseGraphFixture):
    @pytest.mark.asyncio
    async def test_schema_tools(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()

                # Create Schema
                graph_name = "Social"
                create_result = await session.call_tool(
                    "graph/create_schema",
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
                        # "dotenv_path": self.dotenv_path,
                    },
                )
                assert "✅ Schema for graph 'Social' created successfully." in str(
                    create_result
                )

                # Get Schema
                time.sleep(3)
                get_result = await session.call_tool(
                    "graph/get_schema",
                    arguments={
                        "graph_name": graph_name,
                        # "dotenv_path": self.dotenv_path,
                    },
                )
                assert "Person" in str(get_result)

                # Drop Graph
                drop_result = await session.call_tool(
                    "graph/drop_graph",
                    arguments={
                        "graph_name": graph_name,
                        # "dotenv_path": self.dotenv_path,
                    },
                )
                assert "✅" in str(drop_result)
