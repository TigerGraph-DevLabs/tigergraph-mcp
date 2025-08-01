# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import List, Optional, Union
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class BFSToolInput(BaseModel):
    """Input schema for performing a BFS traversal on a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph to query.")
    start_nodes: Union[str, int, List[str], List[int]] = Field(
        ..., description="Starting node(s) for BFS traversal."
    )
    node_type: Optional[str] = Field(None, description="Type of the starting nodes.")
    edge_types: Optional[Union[str, List[str]]] = Field(
        None, description="Edge types to consider during traversal."
    )
    max_hops: Optional[int] = Field(
        None, description="Maximum number of hops (depth) for BFS traversal."
    )
    limit: Optional[int] = Field(
        None, description="Maximum number of neighbors to retrieve per hop."
    )


tools = [
    Tool(
        name=TigerGraphToolName.BREADTH_FIRST_SEARCH,
        description="""Performs a Breadth-First Search (BFS) traversal on a TigerGraph graph using
TigerGraphX.

Examples:
```python
graph_name = "SocialGraph"
start_nodes = ["Alice"]
node_type = "Person"
max_hops = 3
```

Notes:
- You can specify a single or multiple starting nodes.
- `max_hops` controls how far the search will go from the starting nodes.
- Optionally filter traversal by specifying `edge_types`.
- Returns all reachable nodes up to the specified depth with a '_bfs_level' indicating distance
  from the start node.
- Results are returned as a list of dictionaries.
""",
        inputSchema=BFSToolInput.model_json_schema(),
    )
]


async def breadth_first_search(
    graph_name: str,
    start_nodes: Union[str, int, List[str], List[int]],
    node_type: Optional[str] = None,
    edge_types: Optional[Union[str, List[str]]] = None,
    max_hops: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        bfs_result = graph.bfs(
            start_nodes=start_nodes,
            node_type=node_type,
            edge_types=edge_types,
            max_hops=max_hops,
            limit=limit,
            output_type="List",  # Force output as a List
        )
        assert isinstance(bfs_result, list)
        if not bfs_result:
            message = "⚠️ No nodes found during BFS traversal."
        else:
            message = "✅ BFS traversal results:\n" + "\n".join(
                [str(n) for n in bfs_result]
            )
    except Exception as e:
        message = f"❌ Failed to perform BFS traversal on graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
