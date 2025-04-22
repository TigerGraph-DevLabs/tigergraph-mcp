# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Optional, Union, List, Dict
from pydantic import Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName
from tigergraph_mcp.tools.base_tool_input import (
    BaseToolInput,
    TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
)


class GetNodeEdgesToolInput(BaseToolInput):
    """Input schema for retrieving edges connected to a specific node."""

    graph_name: str = Field(
        ..., description="The name of the graph containing the node."
    )
    node_id: str = Field(
        ..., description="The identifier of the node to retrieve edges for."
    )
    node_type: Optional[str] = Field(
        None, description="The type of the node (optional)."
    )
    edge_types: Optional[Union[str, List[str]]] = Field(
        None,
        description="A single edge type or a list of edge types to filter by (optional).",
    )


tools = [
    Tool(
        name=TigerGraphToolName.GET_NODE_EDGES,
        description="""Retrieves edges connected to a specific node in a TigerGraph graph using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
node_id = "Alice"
node_type = "Person"  # Optional
edge_types = ["Friendship", "Colleague"]  # Optional filter
```

**`tigergraph_connection_config`** must also be provided to establish the connection to TigerGraph.

### Configuration Options:
The `tigergraph_connection_config` is required to authenticate and configure the connection to the TigerGraph instance. It can either be explicitly provided or populated via environment variables (recommended). Do not mix both methods.

For more details on configuring `tigergraph_connection_config`, please refer to the following:
"""
        + "\n\n"
        + TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION.strip(),
        inputSchema=GetNodeEdgesToolInput.model_json_schema(),
    )
]


async def get_node_edges(
    graph_name: str,
    node_id: str,
    node_type: Optional[str] = None,
    edge_types: Optional[Union[str, List[str]]] = None,
    tigergraph_connection_config: Optional[Dict] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name, tigergraph_connection_config)
        edges = graph.get_node_edges(node_id, node_type, edge_types)

        if not edges:
            result = f"⚠️ No edges found for node '{node_id}' of type '{node_type or 'default'}' in graph '{graph_name}'."
        else:
            result = f"✅ Edges connected to node '{node_id}' in graph '{graph_name}': {edges}"
    except Exception as e:
        result = f"❌ Failed to retrieve edges for node '{node_id}' in graph '{graph_name}': {str(e)}"

    return [TextContent(type="text", text=result)]
