import pytest
from mcp import ClientSession
from mcp.client.stdio import stdio_client

from tests.integration.base_graph_fixture import UserProductGraphFixture
from tigergraph_mcp import TigerGraphToolName


class TestEdgeTools(UserProductGraphFixture):
    @pytest.mark.asyncio
    async def test_add_edge(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                assert not self.G.has_edge(
                    "User_B", "Product_1", "User", "purchased", "Product"
                )
                result = await session.call_tool(
                    TigerGraphToolName.ADD_EDGE,
                    arguments={
                        "graph_name": self.graph_name,
                        "src_node_id": "User_B",
                        "tgt_node_id": "Product_1",
                        "src_node_type": "User",
                        "edge_type": "purchased",
                        "tgt_node_type": "Product",
                        "attributes": {"purchase_date": "2024-01-12"},
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert "added successfully to graph" in str(result)
                assert self.G.has_edge(
                    "User_B", "Product_1", "User", "purchased", "Product"
                )

    @pytest.mark.asyncio
    async def test_add_edges(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Ensure the edge does not exist initially
                assert not self.G.has_edge(
                    "User_B", "Product_1", "User", "purchased", "Product"
                )

                result = await session.call_tool(
                    TigerGraphToolName.ADD_EDGES,
                    arguments={
                        "graph_name": self.graph_name,
                        "ebunch_to_add": [
                            ["User_B", "Product_1", {"purchase_date": "2024-01-15"}]
                        ],
                        "src_node_type": "User",
                        "edge_type": "purchased",
                        "tgt_node_type": "Product",
                        "attributes": {"quantity": 1},
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )

                assert "Successfully added" in str(result)
                assert self.G.has_edge(
                    "User_B", "Product_1", "User", "purchased", "Product"
                )

    @pytest.mark.asyncio
    async def test_has_edge(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    TigerGraphToolName.HAS_EDGE,
                    arguments={
                        "graph_name": self.graph_name,
                        "src_node_id": "User_A",
                        "tgt_node_id": "Product_1",
                        "src_node_type": "User",
                        "edge_type": "purchased",
                        "tgt_node_type": "Product",
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert f"exists in graph '{self.graph_name}': True" in str(result)

    @pytest.mark.asyncio
    async def test_get_edge_data(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call get_edge_data tool
                result = await session.call_tool(
                    TigerGraphToolName.GET_EDGE_DATA,
                    arguments={
                        "graph_name": self.graph_name,
                        "src_node_id": "User_B",
                        "tgt_node_id": "Product_2",
                        "src_node_type": "User",
                        "edge_type": "purchased",
                        "tgt_node_type": "Product",
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert "✅ Edge data retrieved:" in str(result)
                assert "'purchase_date': '2024-01-12 00:00:00'" in str(result)
