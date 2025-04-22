# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Optional, Dict
from pydantic import Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName
from tigergraph_mcp.tools.base_tool_input import (
    BaseToolInput,
    TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
)


class HasNodeToolInput(BaseToolInput):
    """Input schema for checking node existence in a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph where the node exists."
    )
    node_id: str = Field(..., description="The identifier of the node to check.")
    node_type: Optional[str] = Field(
        None, description="The type of the node (optional)."
    )


tools = [
    Tool(
        name=TigerGraphToolName.HAS_NODE,
        description="""Checks if a node exists in a TigerGraph graph using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
node_id = "Alice"
node_type = "Person"  # Optional
```

**`tigergraph_connection_config`** must also be provided to establish the connection to TigerGraph.

### Configuration Options:
The `tigergraph_connection_config` is required to authenticate and configure the connection to the TigerGraph instance. It can either be explicitly provided or populated via environment variables (recommended). Do not mix both methods.

For more details on configuring `tigergraph_connection_config`, please refer to the following:
"""
        + "\n\n"
        + TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION.strip(),
        inputSchema=HasNodeToolInput.model_json_schema(),
    )
]


async def has_node(
    graph_name: str,
    node_id: str,
    node_type: Optional[str] = None,
    tigergraph_connection_config: Optional[Dict] = None,
) -> list[TextContent]:
    try:
        graph = Graph.from_db(graph_name, tigergraph_connection_config)
        exists = graph.has_node(node_id, node_type)
        result = f"✅ Node '{node_id}' of type '{node_type or 'default'}' exists in graph '{graph_name}': {exists}."
    except Exception as e:
        result = f"❌ Failed to check node existence in graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=result)]
