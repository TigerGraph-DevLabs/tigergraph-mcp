# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Optional
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName


class GetEdgeDataToolInput(BaseModel):
    """Input schema for retrieving a specific edge's data from a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph where the edge is located.")
    src_node_id: str | int = Field(..., description="The identifier of the source node.")
    tgt_node_id: str | int = Field(..., description="The identifier of the target node.")
    src_node_type: Optional[str] = Field(
        None, description="The type of the source node (optional)."
    )
    edge_type: Optional[str] = Field(None, description="The type of the edge (optional).")
    tgt_node_type: Optional[str] = Field(
        None, description="The type of the target node (optional)."
    )


tools = [
    Tool(
        name=TigerGraphToolName.GET_EDGE_DATA,
        description="""Retrieves data for a specific edge in a TigerGraph database using
TigerGraphX.

You must provide the source and target node IDs. Optionally, specify the source node type,
edge type, and target node type.

Example input:
```python
graph_name = "SocialGraph"
src_node_id = "Alice"
tgt_node_id = "Mike"
src_node_type = "Person"
edge_type = "Friendship"
tgt_node_type = "Person"
```
""",
        inputSchema=GetEdgeDataToolInput.model_json_schema(),
    )
]


async def get_edge_data(
    graph_name: str,
    src_node_id: str | int,
    tgt_node_id: str | int,
    src_node_type: Optional[str] = None,
    edge_type: Optional[str] = None,
    tgt_node_type: Optional[str] = None,
) -> list[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        response = graph.get_edge_data(
            src_node_id=src_node_id,
            tgt_node_id=tgt_node_id,
            src_node_type=src_node_type,
            edge_type=edge_type,
            tgt_node_type=tgt_node_type,
        )
        if response is None:
            message = (
                f"⚠️ No edge found between '{src_node_id}' and '{tgt_node_id}' "
                f"in graph '{graph_name}'."
            )
        else:
            message = f"✅ Edge data retrieved: {response}"
    except Exception as e:
        message = f"❌ Failed to retrieve edge data from graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
