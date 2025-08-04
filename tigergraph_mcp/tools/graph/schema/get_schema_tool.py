# Copyright 2025 TigerGraph Inc.
#
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import List
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName


class GetSchemaToolInput(BaseModel):
    """Input schema for retrieving a TigerGraph graph schema."""

    graph_name: str = Field(..., description="The name of the graph to retrieve schema for.")


tools = [
    Tool(
        name=TigerGraphToolName.GET_SCHEMA,
        description="""Retrieves the schema of a graph within TigerGraph using TigerGraphX.

Example input:
```python
graph_name = "MyGraph"
```
""",
        inputSchema=GetSchemaToolInput.model_json_schema(),
    )
]


async def get_schema(
    graph_name: str,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        schema = graph.get_schema()
        message = f"✅ Schema for graph '{graph_name}': {schema}"
    except Exception as e:
        message = f"❌ Failed to retrieve schema for graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
