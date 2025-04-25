# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import List, Optional
from pydantic import Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName
from tigergraph_mcp.tools.base_tool_input import (
    BaseToolInput,
    TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
)


class NumberOfNodesToolInput(BaseToolInput):
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

**`tigergraph_connection_config`** must also be provided to establish the connection to TigerGraph.

### Configuration Options:
The `tigergraph_connection_config` is required to authenticate and configure the connection to the TigerGraph instance. It can either be explicitly provided or populated via environment variables (recommended). Do not mix both methods.

For more details on configuring `tigergraph_connection_config`, please refer to the following:
"""
        + TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
        inputSchema=NumberOfNodesToolInput.model_json_schema(),
    )
]


async def number_of_nodes(
    graph_name: str,
    node_type: Optional[str] = None,
    tigergraph_connection_config: Optional[dict] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name, tigergraph_connection_config)
        count = graph.number_of_nodes(node_type)
        result = f"🔢 Graph '{graph_name}' has {count} node(s)" + (
            f" of type '{node_type}'." if node_type else "."
        )
    except Exception as e:
        result = f"❌ Failed to count nodes in graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=result)]
