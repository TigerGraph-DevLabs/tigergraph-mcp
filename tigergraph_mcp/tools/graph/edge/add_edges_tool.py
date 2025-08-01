# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Any, Dict, List, Optional, Tuple, Sequence
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName


class AddEdgesFromToolInput(BaseModel):
    """Input schema for adding multiple edges to a graph."""

    graph_name: str = Field(..., description="The name of the graph where the edges will be added.")
    ebunch_to_add: Sequence[List] = Field(
        ...,
        description="A list of (src, tgt) or (src, tgt, attribute_dict) edge tuples.",
    )
    src_node_type: Optional[str] = Field(
        None, description="The type of the source nodes (optional)."
    )
    edge_type: Optional[str] = Field(None, description="The type of the edge (optional).")
    tgt_node_type: Optional[str] = Field(
        None, description="The type of the target nodes (optional)."
    )
    attributes: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Common attributes applied to all edges.",
    )


tools = [
    Tool(
        name=TigerGraphToolName.ADD_EDGES,
        description="""Adds multiple edges to a TigerGraph graph using TigerGraphX.

Example input:
```python
{
  "graph_name": "SocialGraph",
  "ebunch_to_add": [
    ["Alice", "Mike"],
    ["Alice", "John", {"closeness": 2.5}]
  ],
  "src_node_type": "Person",
  "edge_type": "Friendship",
  "tgt_node_type": "Person",
  "attributes": {"verified": true}
}
```""",
        inputSchema=AddEdgesFromToolInput.model_json_schema(),
    )
]


async def add_edges(
    graph_name: str,
    ebunch_to_add: Sequence[
        List | Tuple[str | int, str | int] | Tuple[str | int, str | int, Dict[str, Any]]
    ],
    src_node_type: Optional[str] = None,
    edge_type: Optional[str] = None,
    tgt_node_type: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> List[TextContent]:
    try:
        # Normalize ebunch so each item is a (src, tgt, attributes) tuple
        normalized_edges = []
        for item in ebunch_to_add:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                src, tgt = item
                normalized_edges.append((src, tgt, {}))
            elif isinstance(item, (list, tuple)) and len(item) == 3:
                src, tgt, attr = item
                if not isinstance(attr, dict):
                    raise ValueError("Edge attributes must be a dictionary.")
                normalized_edges.append((src, tgt, attr))
            else:
                raise ValueError(
                    "Each item in ebunch_to_add must be (src, tgt) or (src, tgt, attribute dict)."
                )

        graph = Graph.from_db(graph_name)
        count = graph.add_edges_from(
            normalized_edges,
            src_node_type,
            edge_type,
            tgt_node_type,
            **(attributes or {}),
        )

        if count:
            message = (
                f"✅ Successfully added {count} edge(s) of type "
                f"'{edge_type or 'default'}' to graph '{graph_name}'."
            )
        else:
            message = f"❌ Failed to add edges to graph '{graph_name}'."
    except Exception as e:
        message = f"❌ Failed to add edges to graph '{graph_name}': {str(e)}"

    return [TextContent(type="text", text=message)]
