import yaml
from pathlib import Path
from typing import Any, Dict
import time
import pytest
from mcp import StdioServerParameters
from tigergraphx import Graph


class BaseGraphFixture:
    tigergraph_connection_config: Dict[str, Any]
    server_params = StdioServerParameters(command="tigergraph-mcp")

    @pytest.fixture(scope="class", autouse=True)
    def load_connection_config(self, request):
        """Load connection config from YAML and attach to class."""
        config_path = Path(__file__).parent / "config" / "tigergraph_connection.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        request.cls.tigergraph_connection_config = config

class UserProductGraphFixture(BaseGraphFixture):
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
