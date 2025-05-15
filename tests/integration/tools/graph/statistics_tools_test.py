import pytest
from mcp import ClientSession
from mcp.client.stdio import stdio_client

from tests.integration.base_graph_fixture import UserProductGraphFixture
from tigergraph_mcp import TigerGraphToolName


class TestStatisticsTools(UserProductGraphFixture):
    @pytest.mark.asyncio
    async def test_degree(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the degree tool for an existing node
                result = await session.call_tool(
                    TigerGraphToolName.DEGREE,
                    arguments={
                        "graph_name": self.graph_name,
                        "node_id": "Product_1",
                        "node_type": "Product",
                        "edge_types": ["reverse_purchased", "similar_to"],
                    },
                )

                assert "Degree of node 'Product_1'" in str(result)
                assert "is 3" in str(result)

    @pytest.mark.asyncio
    async def test_number_of_nodes(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the degree tool for an existing node
                result = await session.call_tool(
                    TigerGraphToolName.NUMBER_OF_NODES,
                    arguments={
                        "graph_name": self.graph_name,
                    },
                )

                assert "has 6 node(s)" in str(result)

    @pytest.mark.asyncio
    async def test_number_of_edges(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the degree tool for an existing node
                result = await session.call_tool(
                    TigerGraphToolName.NUMBER_OF_EDGES,
                    arguments={
                        "graph_name": self.graph_name,
                    },
                )

                assert "has 6 edge(s)" in str(result)
