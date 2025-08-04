# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Optional, List, Literal
from pydantic import Field, BaseModel
from mcp.types import Tool, TextContent

from tigergraphx import TigerGraphDatabase
from tigergraph_mcp.tools import TigerGraphToolName


class PreviewSampleDataInput(BaseModel):
    """Input schema for previewing sample data from a file."""

    path: str = Field(
        ..., description="The full file path or URI to preview data from."
    )
    data_source_type: Optional[str] = Field(
        None, description="The type of the data source (e.g., s3, gcs, abs)."
    )
    data_source: Optional[str] = Field(
        None, description="Optional name of a configured data source to use."
    )
    data_format: Optional[Literal["csv", "json"]] = Field(
        default="csv", description="The format of the file (csv or json)."
    )
    size: Optional[int] = Field(
        default=10, description="The number of rows to preview."
    )
    has_header: bool = Field(
        default=True, description="Whether the file contains a header row."
    )
    separator: Optional[str] = Field(
        default=",", description="Field separator used in the file."
    )
    quote: Optional[Literal["'", '"']] = Field(
        default='"', description="Quote character used in the file."
    )


tools = [
    Tool(
        name=TigerGraphToolName.PREVIEW_SAMPLE_DATA,
        description="""Previews sample data from a file located in a data source using TigerGraphX.

Use this tool to fetch a preview of the file contents (typically CSV or JSON).
This is useful to inspect data before schema creation or loading.

Note: For S3 paths, always use the `s3a://` protocol (e.g., `s3a://my-bucket/my-file.csv`)
instead of `s3://`. This ensures compatibility and avoids preview failures.

Example input:
```python
path = "s3a://my-bucket/my-file.csv"
data_source_type = "s3"
data_source = "my_data_source"
data_format = "csv"
size = 5
has_header = True
separator = ","
quote = '"'
````

""",
        inputSchema=PreviewSampleDataInput.model_json_schema(),
    )
]


async def preview_sample_data(
    path: str,
    data_source_type: Optional[str] = None,
    data_source: Optional[str] = None,
    data_format: Optional[Literal["csv", "json"]] = "csv",
    size: Optional[int] = 10,
    has_header: bool = True,
    separator: Optional[str] = ",",
    quote: Optional[Literal["'", '"']] = '"',
) -> List[TextContent]:
    try:
        db = TigerGraphDatabase()

        preview = db.preview_sample_data(
            path=path,
            data_source_type=data_source_type,
            data_source=data_source,
            data_format=data_format,
            size=size,
            has_header=has_header,
            separator=separator,
            quote=quote,
        )

        # Format the preview nicely for display
        message = f"✅ Previewed sample data from `{path}`:\n\n```csv\n{preview}\n```"

    except Exception as e:
        message = f"❌ Error previewing sample data from `{path}`: {str(e)}"

    return [TextContent(type="text", text=message)]
