# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Any, Dict, List, Optional, Tuple
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName


class AddNodesToolInput(BaseModel):
    """Input schema for adding multiple nodes to a graph."""

    graph_name: str = Field(..., description="The name of the graph where the nodes will be added.")
    nodes_for_adding: List[str | int] | List[List] = Field(
        ...,
        description="A list of node IDs or [node ID, attribute dict] pairs to be added.",
    )
    node_type: Optional[str] = Field(None, description="The type of the nodes (optional).")
    common_attributes: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Attributes applied to all nodes in the list.",
    )


tools = [
    Tool(
        name=TigerGraphToolName.ADD_NODES,
        description="""Adds multiple nodes to a TigerGraph graph using TigerGraphX.

Example input:
```python
{
  "graph_name": "SocialGraph",
  "nodes_for_adding": [
    ("Alice", {"age": 30, "gender": "Female"}),
    ("Mike", {"age": 29})
  ],
  "node_type": "Person",
  "common_attributes": {"city": "New York"},
}
```
""",
        inputSchema=AddNodesToolInput.model_json_schema(),
    )
]


async def add_nodes(
    graph_name: str,
    nodes_for_adding: List[str | int] | List[List | Tuple[str | int, Dict[str, Any]]],
    node_type: Optional[str] = None,
    common_attributes: Optional[Dict[str, Any]] = None,
) -> List[TextContent]:
    try:
        # Normalize the nodes_for_adding list to ensure each item is a (node_id, attributes_dict)
        # tuple. This is necessary because JSON doesn't distinguish between lists and tuples —
        # any tuple (e.g., ("User_A", {"age": 25})) sent by the client will arrive as a list
        # (["User_A", {"age": 25}]). To handle this gracefully, we treat any 2-element list or
        # tuple where the second item is a dict as a valid node+attribute pair, and any
        # string/int as a bare node ID with no attributes.
        normalized_nodes = []
        for item in nodes_for_adding:
            if isinstance(item, (str, int)):
                normalized_nodes.append((item, {}))
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                node_id, attributes = item
                if not isinstance(attributes, dict):
                    raise ValueError("Each node's attributes must be a dictionary.")
                normalized_nodes.append((node_id, attributes))
            else:
                raise ValueError(
                    "Each item in nodes_for_adding must be a node ID or [node ID, attribute dict]."
                )
        graph = Graph.from_db(graph_name)
        count = graph.add_nodes_from(normalized_nodes, node_type, **(common_attributes or {}))
        if count:
            message = (
                f"✅ Successfully added {str(count)} nodes of type"
                f"'{node_type or 'default'}' to graph '{graph_name}'."
            )
        else:
            message = f"❌ Failed to add nodes to graph '{graph_name}'"
    except Exception as e:
        message = f"❌ Failed to add nodes to graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
