# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Dict, List
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName


class LoadDataToolInput(BaseModel):
    """Input schema for loading data into a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph where data will be loaded."
    )
    loading_job_config: Dict | str = Field(
        ...,
        description=(
            "The loading job configuration used to load data into the graph.\n"
            "This can be a dictionary or a JSON file path."
        ),
    )


tools = [
    Tool(
        name=TigerGraphToolName.LOAD_DATA,
        description="""Loads data into a TigerGraph database using a defined loading job configuration.

Example input:
```python
graph_name = "Social"
loading_job_config = {
    "loading_job_name": "loading_job_Social",
    "files": [
        {
            "file_alias": "f_person",
            "file_path": "/data/files/person_data.csv",  # Local file example
            "csv_parsing_options": {
                "separator": ",",
                "header": True,
                "quote": "DOUBLE",
            },
            "node_mappings": [
                {
                    "target_name": "Person",
                    "attribute_column_mappings": {
                        "name": "name",
                        "age": "age",
                    },
                }
            ],
        },
        {
            "file_alias": "f_friendship",
            "file_path": "$s1:s3://bucket-name/path/to/friendship_data.csv",  # S3 file example with data source prefix
            "edge_mappings": [
                {
                    "target_name": "Friendship",
                    "source_node_column": "source",
                    "target_node_column": "target",
                    "attribute_column_mappings": {
                        "closeness": "closeness",
                    },
                }
            ],
        },
    ],
}
```

Notes:

* Use `"file_path"` as the absolute path to a local file on the TigerGraph server, or in the form of `"$<data_source_name>:<s3_uri>"` for S3 paths.
* Ensure the specified data source (`s1` in this case) is already created and accessible by TigerGraph.
* The "quote" style can be either "DOUBLE" or "SINGLE", with "DOUBLE" being the most common.
""",
        inputSchema=LoadDataToolInput.model_json_schema(),
    )
]


async def load_data(
    graph_name: str,
    loading_job_config: Dict,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        graph.load_data(loading_job_config)
        message = f"✅ Data loaded successfully into graph '{graph_name}'."
    except Exception as e:
        message = f"❌ Failed to load data into graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
