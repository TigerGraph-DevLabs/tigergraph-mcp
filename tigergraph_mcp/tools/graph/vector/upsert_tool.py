from typing import Dict, List, Optional
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class UpsertToolInput(BaseModel):
    """Input schema for upserting nodes with vector data."""

    graph_name: str = Field(
        ..., description="The name of the graph where the nodes will be upserted."
    )
    data: Dict | List[Dict] = Field(
        ..., description="Single record or list of records to upsert."
    )
    node_type: Optional[str] = Field(
        None, description="The node type for the upsert operation (optional)."
    )


tools = [
    Tool(
        name=TigerGraphToolName.UPSERT,
        description="""Upserts nodes into a TigerGraph database using TigerGraphX.

This tool supports both single and multiple node inserts with optional vector attributes.

Example input:
```python
graph_name = "SocialGraph"
data = {"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3]}
node_type = "Person"  # Optional
```

Multiple records:
```python
data = [
    {"name": "Mike", "age": 29, "gender": "Male", "emb_1": [0.4, 0.5, 0.6]},
    {"name": "Emily", "age": 28, "gender": "Female", "emb_1": [0.7, 0.8, 0.9]},
]
```
""",
        inputSchema=UpsertToolInput.model_json_schema(),
    )
]


async def upsert(
    graph_name: str,
    data: Dict | List[Dict],
    node_type: Optional[str] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        result = graph.upsert(data=data, node_type=node_type)
        message = (
            f"✅ Successfully upserted {result} node(s) into graph '{graph_name}'."
        )
    except Exception as e:
        message = f"❌ Failed to upsert data into graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
