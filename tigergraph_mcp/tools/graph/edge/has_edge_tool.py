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


class HasEdgeToolInput(BaseModel):
    """Input schema for checking if an edge exists in a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph to check for the edge.")
    src_node_id: str | int = Field(..., description="The source node identifier.")
    tgt_node_id: str | int = Field(..., description="The target node identifier.")
    src_node_type: Optional[str] = Field(
        None, description="The type of the source node (optional)."
    )
    edge_type: Optional[str] = Field(None, description="The type of the edge (optional).")
    tgt_node_type: Optional[str] = Field(
        None, description="The type of the target node (optional)."
    )


tools = [
    Tool(
        name=TigerGraphToolName.HAS_EDGE,
        description="""Checks whether an edge exists between two nodes in a TigerGraph database
using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
src_node_id = "Alice"
tgt_node_id = "Mike"
src_node_type = "Person"
edge_type = "Friendship"
tgt_node_type = "Person"
```

This will return a boolean value indicating whether the specified edge exists.
""",
        inputSchema=HasEdgeToolInput.model_json_schema(),
    )
]


async def has_edge(
    graph_name: str,
    src_node_id: str | int,
    tgt_node_id: str | int,
    src_node_type: Optional[str] = None,
    edge_type: Optional[str] = None,
    tgt_node_type: Optional[str] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        exists = graph.has_edge(
            src_node_id,
            tgt_node_id,
            src_node_type=src_node_type,
            edge_type=edge_type,
            tgt_node_type=tgt_node_type,
        )
        message = (
            f"✅ Edge between '{src_node_id}' and '{tgt_node_id}' exists "
            f"in graph '{graph_name}': {exists}."
        )
    except Exception as e:
        message = (
            f"❌ Failed to check edge between '{src_node_id}' and '{tgt_node_id}' "
            f"in graph '{graph_name}': {str(e)}"
        )
    return [TextContent(type="text", text=message)]
