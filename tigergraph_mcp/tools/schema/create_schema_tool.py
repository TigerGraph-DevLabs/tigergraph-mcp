# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Dict, Optional
from pydantic import Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolNames
from tigergraph_mcp.tools.base_tool_input import (
    BaseToolInput,
    TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
)


class CreateSchemaToolInput(BaseToolInput):
    """Input schema for creating a TigerGraph graph schema."""

    graph_schema: Dict = Field(..., description="The schema definition of the graph.")


tools = [
    Tool(
        name=TigerGraphToolNames.CREATE_SCHEMA,
        description="""Creates a schema inside TigerGraph using TigerGraphX.

Example input:
```python
graph_schema = {
    "graph_name": "FinancialGraph",  # Example of a graph with nodes and edges
    "nodes": {
        "Account": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING",
                "isBlocked": "BOOL",
            },
            "vector_attributes": {"emb1": 3},
        },
        "City": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING",
            },
        },
        "Phone": {
            "primary_key": "number",
            "attributes": {
                "number": "STRING",
                "isBlocked": "BOOL",
            },
            "vector_attributes": {"emb1": 3},
        },
    },
    "edges": {
        "transfer": {
            "is_directed_edge": True,
            "from_node_type": "Account",
            "to_node_type": "Account",
            "discriminator": "date",
            "attributes": {
                "date": "DATETIME",
                "amount": "INT",
            },
        },
        "hasPhone": {
            "is_directed_edge": False,
            "from_node_type": "Account",
            "to_node_type": "Phone",
        },
        "isLocatedIn": {
            "is_directed_edge": True,
            "from_node_type": "Account",
            "to_node_type": "City",
        },
    },
}
```
**`tigergraph_connection_config`** must also be provided to establish the connection to TigerGraph.

### Configuration Options:
The `tigergraph_connection_config` is required to authenticate and configure the connection to the TigerGraph instance. It can either be explicitly provided or populated via environment variables (recommended). Do not mix both methods.

For more details on configuring `tigergraph_connection_config`, please refer to the following:
"""
        + "\n\n"
        + TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION.strip(),
        inputSchema=CreateSchemaToolInput.model_json_schema(),
    )
]


async def create_schema(
    graph_schema: Dict,
    tigergraph_connection_config: Optional[Dict] = None,
) -> list[TextContent]:
    try:
        graph = Graph(graph_schema, tigergraph_connection_config)
        result = f"✅ Schema for graph '{graph.name}' created successfully."
    except Exception as e:
        result = f"❌ Schema creation failed: {str(e)}."

    return [TextContent(type="text", text=result)]
