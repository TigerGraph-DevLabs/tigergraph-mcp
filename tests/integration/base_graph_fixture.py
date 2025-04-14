import yaml
from pathlib import Path
from typing import Any, Dict
import pytest
from mcp import StdioServerParameters


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
