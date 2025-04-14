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

from tigergraph_mcp.tools import TigerGraphToolNames
from tigergraph_mcp.tools.base_tool_input import (
    BaseToolInput,
    TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
)


class GetNodeDataToolInput(BaseToolInput):
    """Input schema for retrieving node data from a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph containing the node."
    )
    node_id: str = Field(
        ..., description="The identifier of the node to retrieve data for."
    )
    node_type: Optional[str] = Field(
        None, description="The type of the node (optional)."
    )


tools = [
    Tool(
        name=TigerGraphToolNames.GET_NODE_DATA,
        description="""Retrieves data for a specific node in a TigerGraph graph using TigerGraphX.

Example Input:
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
        inputSchema=GetNodeDataToolInput.model_json_schema(),
    )
]


async def get_node_data(
    graph_name: str,
    node_id: str,
    node_type: Optional[str] = None,
    tigergraph_connection_config: Optional[Dict] = None,
) -> list[TextContent]:
    try:
        graph = Graph.from_db(graph_name, tigergraph_connection_config)
        node_data = graph.get_node_data(node_id, node_type)
        if node_data is None:
            result = f"⚠️ Node '{node_id}' of type '{node_type or 'default'}' not found in graph '{graph_name}'."
        else:
            result = (
                f"✅ Node data for '{node_id}' in graph '{graph_name}': {node_data}"
            )
    except Exception as e:
        result = f"❌ Failed to retrieve node data in graph '{graph_name}': {str(e)}"

    return [TextContent(type="text", text=result)]
