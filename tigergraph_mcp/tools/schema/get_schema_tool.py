# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Optional, Dict
from pydantic import Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName
from tigergraph_mcp.tools.base_tool_input import (
    BaseToolInput,
    TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION,
)


class GetSchemaToolInput(BaseToolInput):
    """Input schema for retrieving a TigerGraph graph schema."""

    graph_name: str = Field(
        ..., description="The name of the graph to retrieve schema for."
    )


tools = [
    Tool(
        name=TigerGraphToolName.GET_SCHEMA,
        description="""Retrieves the schema of a graph within TigerGraph using TigerGraphX.

Example input:
```python
graph_name = "MyGraph"
```

**`tigergraph_connection_config`** must also be provided to establish the connection to TigerGraph.

### Configuration Options:
The `tigergraph_connection_config` is required to authenticate and configure the connection to the TigerGraph instance. It can either be explicitly provided or populated via environment variables (recommended). Do not mix both methods.

For more details on configuring `tigergraph_connection_config`, please refer to the following:
"""
        + "\n\n"
        + TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION.strip(),
        inputSchema=GetSchemaToolInput.model_json_schema(),
    )
]


async def get_schema(
    graph_name: str,
    tigergraph_connection_config: Optional[Dict] = None,
) -> list[TextContent]:
    try:
        graph = Graph.from_db(graph_name, tigergraph_connection_config)
        schema = graph.get_schema()
        result = f"✅ Schema for graph '{graph_name}': {schema}"
    except Exception as e:
        result = f"❌ Failed to retrieve schema for graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=result)]
