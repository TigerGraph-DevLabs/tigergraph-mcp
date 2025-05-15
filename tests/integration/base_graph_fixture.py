from pathlib import Path
from dotenv import dotenv_values, load_dotenv
import time
import pytest
from mcp import StdioServerParameters
from tigergraphx import Graph


class BaseFixture:
    dotenv_path: Path = Path(".env")

    # Load env as dictionary for server_params
    env_dict: dict = dotenv_values(dotenv_path=dotenv_path.expanduser().resolve())

    # Server parameters using the parsed .env file
    server_params = StdioServerParameters(
        command="tigergraph-mcp",
        env=env_dict,
    )

    @pytest.fixture(scope="class", autouse=True)
    def load_env_file(self):
        """Load .env file so TigerGraphX can read connection info from it."""
        load_dotenv(dotenv_path=self.dotenv_path.expanduser().resolve(), override=True)


class UserProductGraphFixture(BaseFixture):
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
        self.G = Graph(graph_schema=self.graph_schema)

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
