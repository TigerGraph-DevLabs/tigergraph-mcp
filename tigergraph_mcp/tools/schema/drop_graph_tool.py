# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Optional, Dict, List
from pydantic import Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName
from tigergraph_mcp.tools.base_tool_input import (
    BaseToolInput,
    TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
)


class GraphDropToolInput(BaseToolInput):
    """Input schema for dropping a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph to drop.")


tools = [
    Tool(
        name=TigerGraphToolName.DROP_GRAPH,
        description="""Drops a graph inside TigerGraph using TigerGraphX.

Example input:
```python
graph_name = "MyGraph"
```
"""
        + TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
        inputSchema=GraphDropToolInput.model_json_schema(),
    )
]


async def drop_graph(
    graph_name: str,
    tigergraph_connection_config: Optional[Dict] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name, tigergraph_connection_config)
        graph.drop_graph()
        result = f"✅ Graph '{graph_name}' dropped successfully."
    except Exception as e:
        result = f"❌ Graph drop failed: {str(e)}"

    return [TextContent(type="text", text=result)]
