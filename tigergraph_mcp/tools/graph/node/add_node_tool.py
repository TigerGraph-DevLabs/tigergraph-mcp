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


class AddNodeToolInput(BaseModel):
    """Input schema for adding a node to a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph where the node will be added.")
    node_id: str | int = Field(..., description="The unique identifier of the node.")
    node_type: Optional[str] = Field(None, description="The type of the node (optional).")
    attributes: Optional[Dict] = Field(
        default_factory=dict, description="Additional attributes for the node."
    )


tools = [
    Tool(
        name=TigerGraphToolName.ADD_NODE,
        description="""Adds a node to a TigerGraph database using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
node_id = "Alice"
node_type = "Person"
attributes = {"age": 30, "gender": "Female"}
```
""",
        inputSchema=AddNodeToolInput.model_json_schema(),
    )
]


async def add_node(
    graph_name: str,
    node_id: str | int,
    node_type: Optional[str] = None,
    attributes: Optional[Dict] = None,
) -> List[TextContent]:
    try:
        attributes = attributes or {}
        graph = Graph.from_db(graph_name)
        graph.add_node(node_id, node_type, **attributes)
        message = (
            f"✅ Node '{node_id}' (Type: {node_type or 'default'}) "
            f"added successfully to graph '{graph_name}'."
        )
    except Exception as e:
        message = f"❌ Failed to add node '{node_id}' to graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
