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


class DropDataSourceToolInput(BaseModel):
    """Input schema for dropping a TigerGraph data source."""

    name: str = Field(..., description="The name of the data source to drop.")
    graph: Optional[str] = Field(
        None,
        description="The name of the graph if dropping from a graph-specific context (e.g., "
        "for local data sources).",
    )


tools = [
    Tool(
        name=TigerGraphToolName.DROP_DATA_SOURCE,
        description="""Drops a data source from TigerGraph using TigerGraphX.

Example input:
```python
name = "data_source_1"
graph = "MyGraph"  # optional
````

""",
        inputSchema=DropDataSourceToolInput.model_json_schema(),
    )
]


async def drop_data_source(name: str, graph_name: Optional[str] = None) -> List[TextContent]:
    try:
        db = TigerGraphDatabase()

        response = db.drop_data_source(name=name, graph_name=graph_name)

        if isinstance(response, str) and f"Data source {name} is dropped" in response:
            message = (
                f"✅ Successfully dropped data source '{name}'.\n\nTigerGraph response:\n{response}"
            )
        else:
            message = (
                f"⚠️ Attempted to drop data source '{name}', but received an unexpected "
                f"response:\n{response}"
            )

    except Exception as e:
        message = f"❌ Error dropping data source '{name}': {str(e)}"

    return [TextContent(type="text", text=message)]
