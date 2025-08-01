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


class RemoveNodeToolInput(BaseModel):
    """Input schema for removing a node from a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph from which the node will be removed."
    )
    node_id: str = Field(..., description="The identifier of the node to be removed.")
    node_type: Optional[str] = Field(None, description="The type of the node (optional).")


tools = [
    Tool(
        name=TigerGraphToolName.REMOVE_NODE,
        description="""Removes a node from a TigerGraph database using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
node_id = "Alice"
node_type = "Person"
```
""",
        inputSchema=RemoveNodeToolInput.model_json_schema(),
    )
]


async def remove_node(
    graph_name: str,
    node_id: str,
    node_type: Optional[str] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        success = graph.remove_node(node_id, node_type)
        if success:
            message = (
                f"✅ Node '{node_id}' of type '{node_type or 'default'}' removed "
                f"successfully from graph '{graph_name}'."
            )
        else:
            message = f"⚠️ Node '{node_id}' not found in graph '{graph_name}'."
    except Exception as e:
        message = f"❌ Failed to remove node '{node_id}' from graph '{graph_name}': {str(e)}"

    return [TextContent(type="text", text=message)]
