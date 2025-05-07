import pytest
from mcp import ClientSession
from mcp.client.stdio import stdio_client

from tests.integration.base_graph_fixture import UserProductGraphFixture
from tigergraph_mcp import TigerGraphToolName


class TestQueryTools(UserProductGraphFixture):
    @pytest.mark.asyncio
    async def test_get_nodes(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    TigerGraphToolName.GET_NODES,
                    arguments={
                        "graph_name": self.graph_name,
                        "node_type": "User",
                        "filter_expression": "s.age > 20",
                        "limit": 10,
                    },
                )
                assert "✅ Retrieved nodes" in str(result)

    @pytest.mark.asyncio
    async def test_get_neighbors(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    TigerGraphToolName.GET_NEIGHBORS,
                    arguments={
                        "graph_name": self.graph_name,
                        "start_nodes": ["User_A", "User_B"],
                        "start_node_type": "User",
                        "edge_types": ["purchased"],
                        "filter_expression": "s.id != t.id",
                        "return_attributes": ["id", "name", "price"],
                        "limit": 5,
                    },
                )
                assert "✅ Retrieved neighbors" in str(result)

    @pytest.mark.asyncio
    async def test_breadth_first_search(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    TigerGraphToolName.BREADTH_FIRST_SEARCH,
                    arguments={
                        "graph_name": self.graph_name,
                        "start_nodes": "Product_1",
                        "node_type": "Product",
                        "edge_types": ["similar_to"],
                        "max_hops": 1,
                    },
                )
                assert "✅ BFS traversal results" in str(result)
