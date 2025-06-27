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


class GetAllDataSourcesToolInput(BaseModel):
    """Input schema for retrieving all data sources."""

    graph_name: Optional[str] = Field(
        default=None,
        description="Optional graph name to filter data sources.",
    )


tools = [
    Tool(
        name=TigerGraphToolName.GET_ALL_DATA_SOURCES,
        description="""Retrieves all data sources in TigerGraph using TigerGraphX.

You may optionally filter by graph name.

Example:
```python
graph_name = "MyGraph"
```""",
        inputSchema=GetAllDataSourcesToolInput.model_json_schema(),
    )
]


async def get_all_data_sources(
    graph_name: Optional[str] = None,
) -> List[TextContent]:
    try:
        db = TigerGraphDatabase()
        result = db.get_all_data_sources(graph_name=graph_name)

        if result:
            message = "✅ Successfully retrieved all data sources:\n" + "\n".join(
                f"- {ds['name']} ({ds['type']})" for ds in result
            )
        else:
            message = "ℹ️ No data sources found."

    except Exception as e:
        message = f"❌ Error retrieving all data sources: {str(e)}"

    return [TextContent(type="text", text=message)]
