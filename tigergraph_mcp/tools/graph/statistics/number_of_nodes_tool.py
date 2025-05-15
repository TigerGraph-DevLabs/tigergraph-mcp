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


class NumberOfNodesToolInput(BaseModel):
    """Input schema for getting the number of nodes in a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph to query.")
    node_type: Optional[str] = Field(
        None,
        description="The type of nodes to count (optional). If omitted, counts all nodes.",
    )


tools = [
    Tool(
        name=TigerGraphToolName.NUMBER_OF_NODES,
        description="""Returns the number of nodes in a TigerGraph database using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
node_type = "Person"  # Optional
```

If `node_type` is not provided, all nodes will be counted.
""",
        inputSchema=NumberOfNodesToolInput.model_json_schema(),
    )
]


async def number_of_nodes(
    graph_name: str,
    node_type: Optional[str] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        count = graph.number_of_nodes(node_type)
        message = f"🔢 Graph '{graph_name}' has {count} node(s)" + (
            f" of type '{node_type}'." if node_type else "."
        )
    except Exception as e:
        message = f"❌ Failed to count nodes in graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
