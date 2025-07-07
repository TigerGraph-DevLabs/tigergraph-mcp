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


class CreateSchemaAndLoadInput(BaseModel):
    """Input schema for creating a schema and loading data into TigerGraph."""

    graph_schema: Dict = Field(
        ...,
        description="A complete TigerGraph schema including 'graph_name', 'nodes', and 'edges'.",
    )
    loading_job_config: Dict = Field(
        ...,
        description="The loading job configuration used to load data into the graph.",
    )


tools = [
    Tool(
        name=TigerGraphToolName.CREATE_SCHEMA_AND_LOAD,
        description="""Creates a schema inside TigerGraph and then loads data into the graph.

Input parameters:

- graph_schema: A complete TigerGraph schema including 'graph_name', 'nodes', and 'edges'.
- loading_job_config: The loading job configuration used to load data into the graph.

Example input:
```python
graph_schema = {
    "graph_name": "FinancialGraph",
    "nodes": {
        "Account": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING",
                "isBlocked": "BOOL",
            },
            "vector_attributes": {"emb1": 3},
        },
        "City": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING",
            },
        },
        "Phone": {
            "primary_key": "number",
            "attributes": {
                "number": "STRING",
                "isBlocked": "BOOL",
            },
            "vector_attributes": {"emb1": 3},
        },
    },
    "edges": {
        "transfer": {
            "is_directed_edge": True,
            "from_node_type": "Account",
            "to_node_type": "Account",
            "discriminator": "date",
            "attributes": {
                "date": "DATETIME",
                "amount": "INT",
            },
        },
        "hasPhone": {
            "is_directed_edge": False,
            "from_node_type": "Account",
            "to_node_type": "Phone",
        },
        "isLocatedIn": {
            "is_directed_edge": True,
            "from_node_type": "Account",
            "to_node_type": "City",
        },
    },
}

loading_job_config = {
    "loading_job_name": "loading_job_FinancialGraph",
    "files": [
        {
            "file_alias": "f_account",
            "file_path": "/data/files/account.csv",
            "csv_parsing_options": {
                "separator": ",",
                "header": True,
                "quote": "DOUBLE",
            },
            "node_mappings": [
                {
                    "target_name": "Account",
                    "attribute_column_mappings": {
                        "name": "name",
                        "isBlocked": "blocked",
                    },
                }
            ],
        },
        {
            "file_alias": "f_transfer",
            "file_path": "/data/files/transfer.csv",
            "csv_parsing_options": {
                "separator": ",",
                "header": True,
                "quote": "DOUBLE",
            },
            "node_mappings": [
                {
                    "target_name": "Account",
                    "attribute_column_mappings": {
                        "name": "source",
                    },
                },
                {
                    "target_name": "Account",
                    "attribute_column_mappings": {
                        "name": "target",
                    },
                }
            ],
            "edge_mappings": [
                {
                    "target_name": "transfer",
                    "source_node_column": "source",
                    "target_node_column": "target",
                    "attribute_column_mappings": {
                        "date": "date",
                        "amount": "amount",
                    },
                }
            ],
        }
    ],
}
````

Notes:

* Schema definition
    * Supported data types for schema attributes: "INT", "UINT", "FLOAT", "DOUBLE", "BOOL", "STRING", "DATETIME".
    * Always include the primary key in the attributes dictionary so its type is explicitly known.
* Loading job config
    * Use `"file_path"` as the absolute path to a local file on the TigerGraph server, or in the form of `"$<data_source_name>:<s3_uri>"` for S3 paths.
    * Ensure the specified data source (`s1` in this case) is already created and accessible by TigerGraph.
    * The "quote" style can be either "DOUBLE" or "SINGLE", with "DOUBLE" being the most common.
    * In `"attribute_column_mappings"`, the **key** is the attribute name in the **graph schema**, and the **value** is the corresponding column name in the **data file**.
  """,
        inputSchema=CreateSchemaAndLoadInput.model_json_schema(),
    )
]


async def create_schema_and_load(
    graph_schema: Dict,
    loading_job_config: Dict,
) -> List[TextContent]:
    messages = []
    try:
        graph = Graph(graph_schema)
        messages.append(
            TextContent(
                type="text",
                text=f"✅ Schema for graph '{graph.name}' created successfully.",
            )
        )
    except Exception as e:
        error_msg = f"❌ Schema creation failed: {str(e)}."
        messages.append(TextContent(type="text", text=error_msg))
        return messages

    try:
        graph.load_data(loading_job_config)
        messages.append(
            TextContent(
                type="text",
                text=f"✅ Data loaded successfully into graph '{graph.name}'.",
            )
        )
    except Exception as e:
        error_msg = f"❌ Data loading failed: {str(e)}."
        messages.append(TextContent(type="text", text=error_msg))

    return messages
