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


class GSQLToolInput(BaseModel):
    """Input schema for running raw GSQL commands."""

    command: str = Field(..., description="A raw GSQL command string to execute.")


tools = [
    Tool(
        name=TigerGraphToolName.GSQL,
        description="""Executes a raw GSQL command using TigerGraphX.

Use this tool to issue arbitrary GSQL DDL or DML commands.

Example:
```python
command = "DROP GRAPH MyGraph"
````

""",
        inputSchema=GSQLToolInput.model_json_schema(),
    )
]


async def gsql(command: str) -> List[TextContent]:
    try:
        db = TigerGraphDatabase()
        result = db.gsql(command)
        return [TextContent(type="text", text=f"✅ GSQL Response:\n{result}")]
    except Exception as e:
        return [
            TextContent(type="text", text=f"❌ Error executing GSQL command: {str(e)}")
        ]
