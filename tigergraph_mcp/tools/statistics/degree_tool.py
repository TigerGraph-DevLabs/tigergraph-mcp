# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Optional, List
from pydantic import Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName
from tigergraph_mcp.tools.base_tool_input import (
    BaseToolInput,
    TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
)


class DegreeToolInput(BaseToolInput):
    """Input schema for computing the degree of a node in a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph containing the node."
    )
    node_id: str | int = Field(
        ..., description="The identifier of the node whose degree is to be computed."
    )
    node_type: Optional[str] = Field(
        None, description="The type of the node (optional)."
    )
    edge_types: Optional[List[str] | str] = Field(
        None,
        description="A single edge type or list of edge types to consider. If omitted, all edge types are included.",
    )


tools = [
    Tool(
        name=TigerGraphToolName.DEGREE,
        description="""Returns the degree of a node in a TigerGraph database using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
node_id = "Alice"
node_type = "Person"
edge_types = ["Friendship", "Follow"]
```

If no `edge_types` are provided, all edge types will be used.
"""
        + TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
        inputSchema=DegreeToolInput.model_json_schema(),
    )
]


async def degree(
    graph_name: str,
    node_id: str | int,
    node_type: Optional[str] = None,
    edge_types: Optional[List[str] | str] = None,
    tigergraph_connection_config: Optional[dict] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name, tigergraph_connection_config)
        deg = graph.degree(node_id, node_type=node_type, edge_types=edge_types)
        result = f"📏 Degree of node '{node_id}' (Type: {node_type or 'default'}) in graph '{graph_name}' is {deg}."
    except Exception as e:
        result = f"❌ Failed to compute degree for node '{node_id}' in graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=result)]
