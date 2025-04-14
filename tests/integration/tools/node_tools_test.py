import pytest
import time
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from tigergraphx import Graph

from tests.integration.base_graph_fixture import BaseGraphFixture
from tigergraph_mcp import TigerGraphToolNames


class TestNodeTools(BaseGraphFixture):
    def setup_graph(self):
        """Set up the graph shared across all tests."""
        self.graph_name = "UserProductGraph"
        self.graph_schema = {
            "graph_name": self.graph_name,
            "nodes": {
                "User": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "name": "STRING",
                        "age": "UINT",
                    },
                },
                "Product": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "name": "STRING",
                        "price": "DOUBLE",
                    },
                },
            },
            "edges": {
                "purchased": {
                    "is_directed_edge": True,
                    "from_node_type": "User",
                    "to_node_type": "Product",
                    "attributes": {
                        "purchase_date": "DATETIME",
                        "quantity": "DOUBLE",
                    },
                },
                "similar_to": {
                    "is_directed_edge": False,
                    "from_node_type": "Product",
                    "to_node_type": "Product",
                    "attributes": {
                        "purchase_date": "DATETIME",
                        "quantity": "DOUBLE",
                    },
                },
            },
        }
        self.G = Graph(
            graph_schema=self.graph_schema,
            tigergraph_connection_config=self.tigergraph_connection_config,
        )

    @pytest.fixture(autouse=True)
    def add_nodes_and_edges(self):
        """Add nodes and edges before each test case."""
        # Initialize the graph
        self.setup_graph()

        # Adding nodes and edges
        self.G.add_node("User_A", "User")
        self.G.add_node("User_B", "User", name="B")
        self.G.add_node("User_C", "User", name="C", age=30)
        self.G.add_node("Product_1", "Product")
        self.G.add_node("Product_2", "Product", name="2")
        self.G.add_node("Product_3", "Product", name="3", price=50)
        self.G.add_edge("User_A", "Product_1", "User", "purchased", "Product")
        self.G.add_edge(
            "User_B",
            "Product_2",
            "User",
            "purchased",
            "Product",
            purchase_date="2024-01-12",
        )
        self.G.add_edge(
            "User_C",
            "Product_1",
            "User",
            "purchased",
            "Product",
            purchase_date="2024-01-12",
            quantity=5.5,
        )
        self.G.add_edge(
            "User_C",
            "Product_2",
            "User",
            "purchased",
            "Product",
            purchase_date="2024-01-12",
            quantity=15.5,
        )
        ebunch_to_add = [
            ("User_C", "Product_3", {"purchase_date": "2024-01-12", "quantity": 25.5})
        ]
        self.G.add_edges_from(
            ebunch_to_add,
            "User",
            "purchased",
            "Product",
        )
        ebunch_to_add = [("Product_1", "Product_3")]
        self.G.add_edges_from(
            ebunch_to_add,
            "Product",
            "similar_to",
            "Product",
        )
        time.sleep(1)

        yield  # The test case runs here

        self.G.clear()

    @pytest.fixture(scope="class", autouse=True)
    def drop_graph(self):
        """Drop the graph after all tests are done in the session."""
        yield
        self.setup_graph()
        self.G.drop_graph()

    # ------------------------------ Test Cases ------------------------------
    @pytest.mark.asyncio
    async def test_add_node(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    TigerGraphToolNames.ADD_NODE,
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
                    TigerGraphToolNames.ADD_NODES,
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
                    TigerGraphToolNames.REMOVE_NODE,
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
                    TigerGraphToolNames.HAS_NODE,
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
                    TigerGraphToolNames.GET_NODE_DATA,
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
                    TigerGraphToolNames.GET_NODE_EDGES,
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
                    TigerGraphToolNames.CLEAR_GRAPH_DATA,
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
