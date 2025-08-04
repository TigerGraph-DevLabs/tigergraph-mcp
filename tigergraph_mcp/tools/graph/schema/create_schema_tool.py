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
from tigergraphx.core.tigergraph_api import TigerGraphAPIError

from tigergraph_mcp.tools import TigerGraphToolName


class CreateSchemaToolInput(BaseModel):
    """Input schema for creating a TigerGraph graph schema."""

    graph_schema: Dict = Field(
        ...,
        description="A complete graph schema definition including 'graph_name', 'nodes', "
        "and 'edges'.",
    )


tools = [
    Tool(
        name=TigerGraphToolName.CREATE_SCHEMA,
        description="""Creates a schema inside TigerGraph using TigerGraphX.

Provide a single JSON object called `graph_schema` with the following structure:
```python
graph_schema = {
    "graph_name": "FinancialGraph",  # Example of a graph with nodes and edges
    "nodes": {
        "Account": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING", # Must include primary key here
                "isBlocked": "BOOL",
            },
            "vector_attributes": {"emb1": 3},
        },
        "City": {
            "primary_key": "name",
            "attributes": {
                "name": "STRING", # Must include primary key here
            },
        },
        "Phone": {
            "primary_key": "number",
            "attributes": {
                "number": "STRING", # Must include primary key here
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

Notes:

* Only one top-level field `graph_schema` is expected.
* Supported data types include: "INT", "UINT", "FLOAT", "DOUBLE", "BOOL", "STRING", and "DATETIME"
* Always include the primary key in the attributes dictionary so its type is explicitly known.
```
""",
        inputSchema=CreateSchemaToolInput.model_json_schema(),
    )
]


async def create_schema(graph_schema: Dict) -> List[TextContent]:
    try:
        # Step 1: Attempt to create the graph
        graph = Graph(graph_schema)

        # Step 2: Verify that the graph exists in the database
        try:
            _ = Graph.from_db(graph.name)
        except TigerGraphAPIError as e:
            raise Exception(
                f"Graph '{graph.name}' not found in database after creation attempt: {str(e)}"
            )

        message = f"✅ Schema for graph '{graph.name}' created successfully."
    except Exception as e:
        message = f"❌ Schema creation failed: {str(e)}."

    return [TextContent(type="text", text=message)]
