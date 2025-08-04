# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Dict, Optional, Any, List
from pydantic import Field, BaseModel
from mcp.types import Tool, TextContent

from tigergraphx import TigerGraphDatabase
from tigergraph_mcp.tools import TigerGraphToolName


class UpdateDataSourceToolInput(BaseModel):
    """Input schema for updating a TigerGraph data source."""

    name: str = Field(..., description="The name of the data source to update.")
    data_source_type: str = Field(
        ..., description="The type of the data source (e.g., s3, gcs, abs)."
    )
    access_key: Optional[str] = Field(
        None, description="New access key for the data source (if applicable)."
    )
    secret_key: Optional[str] = Field(
        None, description="New secret key for the data source (if applicable)."
    )
    extra_config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional configuration to include or override in the update.",
    )
    graph: Optional[str] = Field(
        None,
        description="The name of the graph associated with the data source (optional).",
    )


tools = [
    Tool(
        name=TigerGraphToolName.UPDATE_DATA_SOURCE,
        description="""Updates an existing data source in TigerGraph using TigerGraphX.

You can update credentials or append/override extra configuration fields.

Example:
```python
name = "data_source_1"
data_source_type = "s3"
access_key = "new-access"
secret_key = "new-secret"
extra_config = {
    "file.reader.settings.fs.s3a.aws.credentials.provider":
        "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
}
graph = "MyGraph"  # optional
```""",
        inputSchema=UpdateDataSourceToolInput.model_json_schema(),
    )
]


async def update_data_source(
    name: str,
    data_source_type: str,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    extra_config: Optional[Dict[str, Any]] = None,
    graph: Optional[str] = None,
) -> List[TextContent]:
    try:
        db = TigerGraphDatabase()

        response = db.update_data_source(
            name=name,
            data_source_type=data_source_type,
            access_key=access_key,
            secret_key=secret_key,
            extra_config=extra_config,
            graph_name=graph,
        )

        if isinstance(response, str) and f"Data source {name} is created" in response:
            message = (
                f"✅ Successfully updated data source '{name}'.\n\n"
                "TigerGraph response:\n{response}"
            )
        else:
            message = (
                f"⚠️ Attempted to update data source '{name}', "
                f"but received an unexpected response:\n{response}"
            )

    except Exception as e:
        message = f"❌ Error updating data source '{name}': {str(e)}"

    return [TextContent(type="text", text=message)]
