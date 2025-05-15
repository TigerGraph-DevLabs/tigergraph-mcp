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


class NumberOfEdgesToolInput(BaseModel):
    """Input schema for getting the number of edges in a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph to query.")
    edge_type: Optional[str] = Field(
        None,
        description="The type of edges to count (optional). If omitted, counts all edges.",
    )


tools = [
    Tool(
        name=TigerGraphToolName.NUMBER_OF_EDGES,
        description="""Returns the number of edges in a TigerGraph database using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
edge_type = "Friendship"  # Optional
```

If `edge_type` is not provided, all edges will be counted.
""",
        inputSchema=NumberOfEdgesToolInput.model_json_schema(),
    )
]


async def number_of_edges(
    graph_name: str,
    edge_type: Optional[str] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        count = graph.number_of_edges(edge_type)
        message = f"🔗 Graph '{graph_name}' has {count} edge(s)" + (
            f" of type '{edge_type}'." if edge_type else "."
        )
    except Exception as e:
        message = f"❌ Failed to count edges in graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
