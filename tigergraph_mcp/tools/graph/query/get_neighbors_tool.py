# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import List, Optional
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class GetNeighborsToolInput(BaseModel):
    """Input schema for retrieving neighbors from a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph to query.")
    start_nodes: str | int | List[str] | List[int] = Field(
        ..., description="The starting node(s) from which to get neighbors."
    )
    start_node_type: Optional[str] = Field(None, description="The type of the starting nodes.")
    start_node_alias: Optional[str] = Field(
        "s", description="Alias for the starting node, used in the filter expression."
    )
    edge_types: Optional[str | List[str]] = Field(
        None, description="Edge types to consider when finding neighbors."
    )
    edge_alias: Optional[str] = Field(
        "e", description="Alias for the edge, used in the filter expression."
    )
    target_node_types: Optional[str | List[str]] = Field(
        None, description="Target node types to consider as neighbors."
    )
    target_node_alias: Optional[str] = Field(
        "t", description="Alias for the target node, used in the filter expression."
    )
    filter_expression: Optional[str] = Field(
        None,
        description="Optional filter expression for edge or target node filtering.",
    )
    return_attributes: Optional[List[str]] = Field(
        None,
        description="List of attributes to return for each neighbor. "
        "If omitted, returns all attributes.",
    )
    limit: Optional[int] = Field(None, description="Maximum number of neighbors to retrieve.")


tools = [
    Tool(
        name=TigerGraphToolName.GET_NEIGHBORS,
        description="""Retrieves neighbors of specific nodes in a TigerGraph database using
TigerGraphX.

Examples:
```python
graph_name = "SocialGraph"
start_nodes = "Alice"
start_node_type = "Person"
edge_types = "Friendship"
target_node_types = "Person"
filter_expression = "e.closeness > 1.5"
return_attributes = ["name", "gender"]
limit = 5
```

Notes:
- You can specify a single or multiple starting nodes.
- Filter neighbors using edge or node attributes via `filter_expression`.
- If `return_attributes` is specified, only those attributes will be included in the results.
- Results are always returned as a list of dictionaries.
""",
        inputSchema=GetNeighborsToolInput.model_json_schema(),
    )
]


async def get_neighbors(
    graph_name: str,
    start_nodes: str | int | List[str] | List[int],
    start_node_type: Optional[str] = None,
    start_node_alias: str = "s",
    edge_types: Optional[str | List[str]] = None,
    edge_alias: str = "e",
    target_node_types: Optional[str | List[str]] = None,
    target_node_alias: str = "t",
    filter_expression: Optional[str] = None,
    return_attributes: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        neighbors = graph.get_neighbors(
            start_nodes=start_nodes,
            start_node_type=start_node_type,
            start_node_alias=start_node_alias,
            edge_types=edge_types,
            edge_alias=edge_alias,
            target_node_types=target_node_types,
            target_node_alias=target_node_alias,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
            output_type="List",  # Ensure consistent return format
        )
        assert isinstance(neighbors, list)
        if not neighbors:
            message = "⚠️ No neighbors found."
        else:
            message = "✅ Retrieved neighbors:\n" + "\n".join([str(n) for n in neighbors])
    except Exception as e:
        message = f"❌ Failed to retrieve neighbors from graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
