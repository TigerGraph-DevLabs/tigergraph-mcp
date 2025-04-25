import pytest
from mcp import ClientSession
from mcp.client.stdio import stdio_client

from tests.integration.base_graph_fixture import UserProductGraphFixture
from tigergraph_mcp import TigerGraphToolName


class TestNodeTools(UserProductGraphFixture):
    @pytest.mark.asyncio
    async def test_add_node(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    TigerGraphToolName.ADD_NODE,
                    arguments={
                        "graph_name": self.graph_name,
                        "node_id": "User_D",
                        "node_type": "User",
                        "attributes": {"age": 30, "name": "John"},
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert "added successfully to graph" in str(result)
                assert self.G.has_node("User_D", "User")

    @pytest.mark.asyncio
    async def test_add_nodes(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    TigerGraphToolName.ADD_NODES,
                    arguments={
                        "graph_name": self.graph_name,
                        "nodes_for_adding": [
                            ("User_E", {"name": "John"}),
                            ("User_F", {"name": "Alice"}),
                        ],
                        "node_type": "User",
                        "common_attributes": {"age": 30},
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )

                assert "Successfully added 2 nodes" in str(result)

                assert self.G.has_node("User_E", "User")
                assert self.G.has_node("User_F", "User")

    @pytest.mark.asyncio
    async def test_remove_node(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the remove_node tool
                result = await session.call_tool(
                    TigerGraphToolName.REMOVE_NODE,
                    arguments={
                        "graph_name": self.graph_name,
                        "node_id": "User_C",
                        "node_type": "User",
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert "removed successfully" in str(result)

                # Verify node no longer exists
                assert not self.G.has_node("User_C", "User")

    @pytest.mark.asyncio
    async def test_has_node(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the has_node tool
                result = await session.call_tool(
                    TigerGraphToolName.HAS_NODE,
                    arguments={
                        "graph_name": self.graph_name,
                        "node_id": "User_C",
                        "node_type": "User",
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert f"exists in graph '{self.graph_name}': True" in str(result)

    @pytest.mark.asyncio
    async def test_get_node_data(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Retrieve data for an existing node
                result = await session.call_tool(
                    TigerGraphToolName.GET_NODE_DATA,
                    arguments={
                        "graph_name": self.graph_name,
                        "node_id": "User_C",
                        "node_type": "User",
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )

                # Check the result contains expected attributes
                assert "✅ Node data for 'User_C'" in str(result)
                assert "'name': 'C'" in str(result)
                assert "'age': 30" in str(result)

    @pytest.mark.asyncio
    async def test_get_node_edges(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    TigerGraphToolName.GET_NODE_EDGES,
                    arguments={
                        "graph_name": self.graph_name,
                        "node_id": "User_C",
                        "node_type": "User",
                        "edge_types": "purchased",
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )

                # Check the result includes edges from User_C to Product_1 and Product_2
                assert "✅ Edges connected to node 'User_C'" in str(result)
                assert "('User_C', 'Product_1')" in str(result)
                assert "('User_C', 'Product_2')" in str(result)
                assert "('User_C', 'Product_3')" in str(result)

    @pytest.mark.asyncio
    async def test_clear_graph_data(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Clear graph data
                result = await session.call_tool(
                    TigerGraphToolName.CLEAR_GRAPH_DATA,
                    arguments={
                        "graph_name": self.graph_name,
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert (
                    f"✅ All data cleared from graph '{self.graph_name}' successfully."
                    in str(result)
                )

                # Check that data is now gone
                assert not self.G.has_node("User_C", "User")
