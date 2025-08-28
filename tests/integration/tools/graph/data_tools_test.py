import pytest

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from tigergraphx import Graph

from tests.integration.base_graph_fixture import BaseFixture
from tigergraph_mcp import TigerGraphToolName


# @pytest.mark.skip(
#     reason="""
# Skipped by default. To enable this test, you must manually place the following files in the
# TigerGraph server:
#
# 1. /home/tigergraph/data/person_data.csv
# Contents:
# name,age
# John,11
#
# 2. /home/tigergraph/data/friendship_data.csv
# Contents:
# source,target,closeness
# John,John,11
#
# 3. /home/tigergraph/data/purchase_data.csv
# Contents:
# John,Product_1,1,100
# Lily,Product_2,2,500
# """
# )
class TestDataTools(BaseFixture):
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
                "Product": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
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
                "Purchase": {
                    "is_directed_edge": False,
                    "from_node_type": "Person",
                    "to_node_type": "Product",
                    "attributes": {
                        "quantity": "DOUBLE",
                        "total_price": "DOUBLE",
                    },
                },
            },
        }

    @pytest.fixture(autouse=True)
    def setup_files_and_graph(self):
        # Initialize the graph
        self.setup_graph()

        yield  # The test case runs here

    @pytest.mark.asyncio
    async def test_load_data(self):
        self.G = Graph(graph_schema=self.graph_schema)
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
                {
                    "file_alias": "f_purchase",
                    "file_path": "/home/tigergraph/data/purchase_data.csv",
                    "csv_parsing_options": {
                        "separator": ",",
                        "header": False,  # No header row in the file
                        "quote": "DOUBLE",
                    },
                    "node_mappings": [
                        {
                            "target_name": "Person",
                            "attribute_column_mappings": {
                                "name": 0,  # First column
                            },
                        },
                        {
                            "target_name": "Product",
                            "attribute_column_mappings": {
                                "id": 1,  # Second column
                            },
                        },
                    ],
                    "edge_mappings": [
                        {
                            "target_name": "Purchase",
                            "source_node_column": 0,  # Person.person_id
                            "target_node_column": 1,  # Product.product_id
                            "attribute_column_mappings": {
                                "quantity": 2,
                                "total_price": 3,
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
                assert self.G.number_of_nodes() == 4
                assert self.G.number_of_edges() == 3

        self.G.drop_graph()
