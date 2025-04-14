# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Optional, Dict, Union
from pydantic import Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolNames
from tigergraph_mcp.tools.base_tool_input import (
    BaseToolInput,
    TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
)


class LoadDataToolInput(BaseToolInput):
    """Input schema for loading data into a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph where data will be loaded."
    )
    loading_job_config: Union[Dict, str] = Field(
        ...,
        description=(
            "The loading job configuration used to load data into the graph.\n"
            "This can be a dictionary or a JSON file path."
        ),
    )


tools = [
    Tool(
        name=TigerGraphToolNames.LOAD_DATA,
        description="""Loads data into a TigerGraph database using a defined loading job configuration.

Example input:
```python
graph_name = "Social"
loading_job_config = {
    "loading_job_name": "loading_job_Social",
    "files": [
        {
            "file_alias": "f_person",
            "file_path": "/path/to/person_data.csv",
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
            "file_path": "/path/to/friendship_data.csv",
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
```

**`tigergraph_connection_config`** must also be provided to establish the connection to TigerGraph.

### Configuration Options:
The `tigergraph_connection_config` is required to authenticate and configure the connection to the TigerGraph instance. It can either be explicitly provided or populated via environment variables (recommended). Do not mix both methods.

For more details on configuring `tigergraph_connection_config`, please refer to the following:
"""
        + "\n\n"
        + TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION.strip(),
        inputSchema=LoadDataToolInput.model_json_schema(),
    )
]


async def load_data(
    graph_name: str,
    loading_job_config: Dict,
    tigergraph_connection_config: Optional[Dict] = None,
) -> list[TextContent]:
    try:
        graph = Graph.from_db(graph_name, tigergraph_connection_config)
        graph.load_data(loading_job_config)
        result = f"✅ Data loaded successfully into graph '{graph_name}'."
    except Exception as e:
        result = f"❌ Failed to load data into graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=result)]
