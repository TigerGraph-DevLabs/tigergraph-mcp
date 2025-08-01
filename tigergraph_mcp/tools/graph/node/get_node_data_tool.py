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


class GetNodeDataToolInput(BaseModel):
    """Input schema for retrieving node data from a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph containing the node.")
    node_id: str | int = Field(..., description="The identifier of the node to retrieve data for.")
    node_type: Optional[str] = Field(None, description="The type of the node (optional).")


tools = [
    Tool(
        name=TigerGraphToolName.GET_NODE_DATA,
        description="""Retrieves data for a specific node in a TigerGraph graph using TigerGraphX.

Example Input:
```python
graph_name = "SocialGraph"
node_id = "Alice"
node_type = "Person"  # Optional
```
""",
        inputSchema=GetNodeDataToolInput.model_json_schema(),
    )
]


async def get_node_data(
    graph_name: str,
    node_id: str | int,
    node_type: Optional[str] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        node_data = graph.get_node_data(node_id, node_type)
        if node_data is None:
            message = (
                f"⚠️ Node '{node_id}' of type '{node_type or 'default'}' "
                "not found in graph '{graph_name}'."
            )
        else:
            message = f"✅ Node data for '{node_id}' in graph '{graph_name}': {node_data}"
    except Exception as e:
        message = f"❌ Failed to retrieve node data in graph '{graph_name}': {str(e)}"

    return [TextContent(type="text", text=message)]
