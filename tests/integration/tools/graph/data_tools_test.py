import pytest

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from tigergraphx import Graph

from tests.integration.base_graph_fixture import BaseGraphFixture
from tigergraph_mcp import TigerGraphToolName


@pytest.mark.skip(
    reason="""
Skipped by default. To enable this test, you must manually place the following files in the TigerGraph server:

1. /home/tigergraph/data/person_data.csv
Contents:
name,age
John,11

2. /home/tigergraph/data/friendship_data.csv
Contents:
source,target,closeness
John,John,11
"""
)
class TestDataTools(BaseGraphFixture):
    def setup_graph(self):
        """Set up the graph shared across all tests."""
        self.graph_name = "SocialGraph"
        self.graph_schema = {
            "graph_name": self.graph_name,
            "nodes": {
                "Person": {
                    "primary_key": "name",
                    "attributes": {
                        "name": "STRING",
                        "age": "INT",
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
        }
        self.G = Graph(graph_schema=self.graph_schema)

    @pytest.fixture(autouse=True)
    def setup_files_and_graph(self):
        # Initialize the graph
        self.setup_graph()

        yield  # The test case runs here

        self.G.clear()

    @pytest.fixture(scope="class", autouse=True)
    def drop_graph(self):
        """Drop the graph after all tests are done in the session."""
        yield
        self.setup_graph()
        self.G.drop_graph()

    @pytest.mark.asyncio
    async def test_load_data(self):
        loading_job_config = {
            "loading_job_name": "loading_job_Social",
            "files": [
                {
                    "file_alias": "f_person",
                    "file_path": "/home/tigergraph/data/person_data.csv",
                    "csv_parsing_options": {
                        "separator": ",",
                        "header": True,
                        "EOL": "\\n",
                        "quote": "DOUBLE",
                    },
                    "node_mappings": [
                        {
                            "target_name": "Person",
                            "attribute_column_mappings": {
                                "name": "name",
                                "age": "age",
                            },
                        }
                    ],
                },
                {
                    "file_alias": "f_friendship",
                    "file_path": "/home/tigergraph/data/friendship_data.csv",
                    "csv_parsing_options": {
                        "separator": ",",
                        "header": True,
                        "EOL": "\\n",
                        "quote": "DOUBLE",
                    },
                    "edge_mappings": [
                        {
                            "target_name": "Friendship",
                            "source_node_column": "source",
                            "target_node_column": "target",
                            "attribute_column_mappings": {
                                "closeness": "closeness",
                            },
                        }
                    ],
                },
            ],
        }

        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    TigerGraphToolName.LOAD_DATA,
                    arguments={
                        "graph_name": self.graph_name,
                        "loading_job_config": loading_job_config,
                    },
                )
                assert "Data loaded successfully into graph" in str(result)
                assert self.G.number_of_nodes() == 1
                assert self.G.number_of_edges() == 1
