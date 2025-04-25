# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Dict, List, Optional
from pydantic import Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName
from tigergraph_mcp.tools.base_tool_input import (
    BaseToolInput,
    TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
)


class ClearGraphDataToolInput(BaseToolInput):
    """Input schema for clearing all data from a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph to clear all data from."
    )


tools = [
    Tool(
        name=TigerGraphToolName.CLEAR_GRAPH_DATA,
        description="""Clears all nodes and edges from a graph in TigerGraph using TigerGraphX.

Example Input:
```python
graph_name = "MyGraph"
```
"""
        + TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
        inputSchema=ClearGraphDataToolInput.model_json_schema(),
    )
]


async def clear_graph_data(
    graph_name: str,
    tigergraph_connection_config: Optional[Dict] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name, tigergraph_connection_config)
        result = graph.clear()
        if result:
            message = f"\u2705 All data cleared from graph '{graph_name}' successfully."
        else:
            message = f"\u274c Failed to clear data from graph '{graph_name}'."
    except Exception as e:
        message = f"\u274c Failed to clear data from graph '{graph_name}': {str(e)}"

    return [TextContent(type="text", text=message)]
