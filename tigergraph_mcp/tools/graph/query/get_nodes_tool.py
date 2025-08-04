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


class GetNodesToolInput(BaseModel):
    """Input schema for retrieving nodes from a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph to query.")
    node_type: Optional[str] = Field(
        None,
        description="The type of nodes to retrieve. If omitted, retrieves nodes of all types.",
    )
    all_node_types: Optional[bool] = Field(
        False,
        description="Whether to retrieve nodes of all types, ignoring `node_type`.",
    )
    node_alias: Optional[str] = Field(
        "s",
        description="Alias for the node, mainly used inside the filter expression. "
        "Defaults to 's'.",
    )
    filter_expression: Optional[str] = Field(
        None,
        description="An optional filter expression to apply when retrieving nodes.",
    )
    return_attributes: Optional[List[str]] = Field(
        None,
        description="A list of attributes to return for each node. "
        "If omitted, returns all attributes.",
    )
    limit: Optional[int] = Field(None, description="The maximum number of nodes to retrieve.")


tools = [
    Tool(
        name=TigerGraphToolName.GET_NODES,
        description="""Retrieves nodes from a TigerGraph database using TigerGraphX.

Examples:
```python
graph_name = "SocialGraph"
node_type = "Person"
all_node_types = False
node_alias = "s"  # Optional
filter_expression = "s.age >= 30"
return_attributes = ["name", "gender"]
limit = 10
```

Notes:
- Set `all_node_types=True` to retrieve nodes of all types, ignoring `node_type`.
- Use `filter_expression` to apply conditions (e.g., "s.age >= 25 and s.gender == 'Female'").
- If `return_attributes` is specified, only the listed attributes will be returned.
- Results are always returned as a list of dictionaries.
""",
        inputSchema=GetNodesToolInput.model_json_schema(),
    )
]


async def get_nodes(
    graph_name: str,
    node_type: Optional[str] = None,
    all_node_types: bool = False,
    node_alias: str = "s",
    filter_expression: Optional[str] = None,
    return_attributes: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        nodes = graph.get_nodes(
            node_type=node_type,
            all_node_types=all_node_types,
            node_alias=node_alias,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
            output_type="List",  # Always enforce List output
        )
        assert isinstance(nodes, List)
        if not nodes:
            message = "⚠️ No nodes found."
        else:
            message = "✅ Retrieved nodes:\n" + "\n".join([str(node) for node in nodes])
    except Exception as e:
        message = f"❌ Failed to retrieve nodes from graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
