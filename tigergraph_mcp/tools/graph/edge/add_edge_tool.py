# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Dict, List, Optional
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName


class AddEdgeToolInput(BaseModel):
    """Input schema for adding an edge to a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph where the edge will be added.")
    src_node_id: str | int = Field(..., description="The ID of the source node.")
    tgt_node_id: str | int = Field(..., description="The ID of the target node.")
    src_node_type: Optional[str] = Field(
        None, description="The type of the source node (optional)."
    )
    edge_type: Optional[str] = Field(None, description="The type of the edge (optional).")
    tgt_node_type: Optional[str] = Field(
        None, description="The type of the target node (optional)."
    )
    attributes: Optional[Dict] = Field(
        default_factory=dict, description="Additional edge attributes."
    )


tools = [
    Tool(
        name=TigerGraphToolName.ADD_EDGE,
        description="""Adds an edge between two nodes in a TigerGraph database using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
src_node_id = "Alice"
tgt_node_id = "Mike"
src_node_type = "Person"
edge_type = "Friendship"
tgt_node_type = "Person"
attributes = {"closeness": 2.5}
```

If node types and edge type are not specified, default single-type behavior is assumed.
""",
        inputSchema=AddEdgeToolInput.model_json_schema(),
    )
]


async def add_edge(
    graph_name: str,
    src_node_id: str | int,
    tgt_node_id: str | int,
    src_node_type: Optional[str] = None,
    edge_type: Optional[str] = None,
    tgt_node_type: Optional[str] = None,
    attributes: Optional[Dict] = None,
) -> List[TextContent]:
    try:
        attributes = attributes or {}
        graph = Graph.from_db(graph_name)
        graph.add_edge(
            src_node_id,
            tgt_node_id,
            src_node_type,
            edge_type,
            tgt_node_type,
            **attributes,
        )
        message = (
            f"✅ Edge from '{src_node_id}' to '{tgt_node_id}' (EdgeType: {edge_type or 'default'})"
            f"added successfully to graph '{graph_name}'."
        )
    except Exception as e:
        message = (
            f"❌ Failed to add edge from '{src_node_id}' to '{tgt_node_id}'"
            f"in graph '{graph_name}': {str(e)}"
        )
    return [TextContent(type="text", text=message)]
