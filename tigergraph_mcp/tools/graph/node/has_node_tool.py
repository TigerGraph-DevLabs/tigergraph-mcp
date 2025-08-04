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


class HasNodeToolInput(BaseModel):
    """Input schema for checking node existence in a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph where the node exists.")
    node_id: str | int = Field(..., description="The identifier of the node to check.")
    node_type: Optional[str] = Field(None, description="The type of the node (optional).")


tools = [
    Tool(
        name=TigerGraphToolName.HAS_NODE,
        description="""Checks if a node exists in a TigerGraph graph using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
node_id = "Alice"
node_type = "Person"  # Optional
```
""",
        inputSchema=HasNodeToolInput.model_json_schema(),
    )
]


async def has_node(
    graph_name: str,
    node_id: str | int,
    node_type: Optional[str] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        exists = graph.has_node(node_id, node_type)
        message = (
            f"✅ Node '{node_id}' of type '{node_type or 'default'}' exists "
            f"in graph '{graph_name}': {exists}."
        )
    except Exception as e:
        message = f"❌ Failed to check node existence in graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
