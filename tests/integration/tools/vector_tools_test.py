import pytest
import time
from mcp import ClientSession
from mcp.client.stdio import stdio_client

from tests.integration.base_graph_fixture import BaseGraphFixture
from tigergraph_mcp import TigerGraphToolName
from tigergraphx import Graph


class TestVectorTools(BaseGraphFixture):
    def setup_graph(self):
        """Set up the graph and add nodes and edges."""
        self.graph_name = "TigerVector"
        graph_schema = {
            "graph_name": self.graph_name,
            "nodes": {
                "Entity": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "entity_type": "STRING",
                        "description": "STRING",
                        "source_id": "STRING",
                    },
                    "vector_attributes": {"emb_description": 3},
                },
            },
            "edges": {
                "relationship": {
                    "is_directed_edge": True,
                    "from_node_type": "Entity",
                    "to_node_type": "Entity",
                    "attributes": {
                        "weight": "DOUBLE",
                        "description": "STRING",
                        "keywords": "STRING",
                        "source_id": "STRING",
                    },
                },
            },
        }
        self.G = Graph(
            graph_schema=graph_schema,
            tigergraph_connection_config=self.tigergraph_connection_config,
        )

    @pytest.fixture(autouse=True)
    def add_nodes_and_edges(self):
        """Add nodes and edges before each test case."""
        # Initialize the graph
        self.setup_graph()

        # Adding nodes and edges
        self.G.upsert(
            data=[
                {
                    "id": "Entity_1",
                    "entity_type": "Person",
                    "description": "Desc1",
                    "source_id": "Source1",
                    "emb_description": [-0.01773, -0.01019, -0.01657],
                },
            ],
            node_type="Entity",
        )
        self.G.add_nodes_from(
            [
                (
                    "Entity_2",
                    {
                        "entity_type": "Person",
                        "description": "Desc2",
                        "source_id": "Source2",
                        "emb_description": [-0.01926, 0.000496, 0.00671],
                    },
                ),
            ]
        )
        self.G.add_edge(
            "Entity_1",
            "Entity_2",
            "Entity",
            "relationship",
            "Entity",
            weight=1.0,
            description="Relates to",
            keywords="key1,key2",
            source_id="SourceRel",
        )
        time.sleep(3)

        yield  # The test case runs here

        self.G.clear()

    @pytest.fixture(scope="class", autouse=True)
    def drop_graph(self):
        """Drop the graph after all tests are done in the session."""
        yield
        self.setup_graph()
        self.G.drop_graph()

    @pytest.mark.asyncio
    async def test_upsert(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the upsert tool
                result = await session.call_tool(
                    TigerGraphToolName.UPSERT,
                    arguments={
                        "graph_name": self.graph_name,
                        "data": [
                            {
                                "id": "Entity_1",
                                "entity_type": "Person",
                                "description": "Desc1",
                                "source_id": "Source1",
                                "emb_description": [-0.01773, -0.01019, -0.01657],
                            },
                        ],
                        "node_type": "Entity",
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert "✅ Successfully upserted" in str(result)

    @pytest.mark.asyncio
    async def test_fetch_node(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the upsert tool
                result = await session.call_tool(
                    TigerGraphToolName.FETCH_NODE,
                    arguments={
                        "graph_name": self.graph_name,
                        "node_id": "Entity_1",
                        "vector_attribute_name": "emb_description",
                        "node_type": "Entity",
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert "📦 Retrieved vector for node" in str(result)

    @pytest.mark.asyncio
    async def test_fetch_nodes(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the upsert tool
                result = await session.call_tool(
                    TigerGraphToolName.FETCH_NODES,
                    arguments={
                        "graph_name": self.graph_name,
                        "node_ids": ["Entity_1", "Entity_2"],
                        "vector_attribute_name": "emb_description",
                        "node_type": "Entity",
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert "📦 Retrieved vectors" in str(result)

    @pytest.mark.asyncio
    async def test_search(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the upsert tool
                result = await session.call_tool(
                    TigerGraphToolName.SEARCH,
                    arguments={
                        "graph_name": self.graph_name,
                        "data": [-0.01926, 0.000496, 0.00671],
                        "vector_attribute_name": "emb_description",
                        "node_type": "Entity",
                        "limit": 1,
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert "🔍 Search results:" in str(result)

    @pytest.mark.asyncio
    async def test_search_top_k_similar_nodes(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Call the upsert tool
                result = await session.call_tool(
                    TigerGraphToolName.SEARCH_TOP_K_SIMILAR_NODES,
                    arguments={
                        "graph_name": self.graph_name,
                        "node_id": "Entity_1",
                        "vector_attribute_name": "emb_description",
                        "node_type": "Entity",
                        "limit": 1,
                        "tigergraph_connection_config": self.tigergraph_connection_config,
                    },
                )
                assert "🔍 Top-k similar nodes for" in str(result)
