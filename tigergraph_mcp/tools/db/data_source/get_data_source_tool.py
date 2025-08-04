# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import List
from pydantic import Field, BaseModel
from mcp.types import Tool, TextContent

from tigergraphx import TigerGraphDatabase
from tigergraph_mcp.tools import TigerGraphToolName


class GetDataSourceToolInput(BaseModel):
    """Input schema for retrieving a TigerGraph data source configuration."""

    name: str = Field(..., description="The name of the data source to retrieve.")


tools = [
    Tool(
        name=TigerGraphToolName.GET_DATA_SOURCE,
        description="""Retrieves the configuration details of a specified data source in TigerGraph
using TigerGraphX.

Example:
```python
name = "data_source_1"
```""",
        inputSchema=GetDataSourceToolInput.model_json_schema(),
    )
]


async def get_data_source(name: str) -> List[TextContent]:
    try:
        db = TigerGraphDatabase()

        result = db.get_data_source(name)

        message = f"✅ Successfully retrieved configuration for data source '{name}':\n{result}"

    except Exception as e:
        message = f"❌ Error retrieving data source '{name}': {str(e)}"

    return [TextContent(type="text", text=message)]
