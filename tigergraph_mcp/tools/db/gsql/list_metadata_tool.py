# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Optional, List
from pydantic import Field, BaseModel
from mcp.types import Tool, TextContent

from tigergraphx import TigerGraphDatabase
from tigergraph_mcp.tools import TigerGraphToolName


class ListMetadataToolInput(BaseModel):
    """Input schema for listing TigerGraph metadata."""

    graph_name: Optional[str] = Field(
        None, description="Optional graph name to scope the metadata listing."
    )


tools = [
    Tool(
        name=TigerGraphToolName.LIST_METADATA,
        description="""Lists metadata from the TigerGraph database, including:

- Vertex and edge types
- Graphs
- Jobs
- Data sources
- Queries (graph-specific)
- Packages (global-only)

If a graph name is provided, runs `USE GRAPH {graph_name}` followed by `LS`.
Otherwise, runs a global `LS`.

Example:
```python
graph_name = "MyGraph"  # optional
```""",
        inputSchema=ListMetadataToolInput.model_json_schema(),
    )
]


async def list_metadata(graph_name: Optional[str] = None) -> List[TextContent]:
    try:
        db = TigerGraphDatabase()
        result = db.list_metadata(graph_name=graph_name)
        message = f"✅ Successfully listed metadata:\n{result}"
    except Exception as e:
        message = f"❌ Error listing metadata: {str(e)}"

    return [TextContent(type="text", text=message)]
