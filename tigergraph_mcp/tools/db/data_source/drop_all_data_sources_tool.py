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


class DropAllDataSourcesToolInput(BaseModel):
    """Input schema for dropping all data sources."""

    graph_name: Optional[str] = Field(
        default=None,
        description="Optional graph name to scope the data source removal.",
    )


tools = [
    Tool(
        name=TigerGraphToolName.DROP_ALL_DATA_SOURCES,
        description="""Drops all data sources in TigerGraph using TigerGraphX.

You may optionally scope the drop operation to a specific graph.

Example:
```python
graph_name = "MyGraph"
```""",
        inputSchema=DropAllDataSourcesToolInput.model_json_schema(),
    )
]


async def drop_all_data_sources(
    graph_name: Optional[str] = None,
) -> List[TextContent]:
    try:
        db = TigerGraphDatabase()
        result = db.drop_all_data_sources(graph_name=graph_name)

        if "is dropped" in result or "is dropped successfully" in result:
            message = f"✅ {result}"
        else:
            message = f"⚠️ Attempted to drop all data sources but got unexpected response:\n{result}"

    except Exception as e:
        message = f"❌ Error dropping all data sources: {str(e)}"

    return [TextContent(type="text", text=message)]
