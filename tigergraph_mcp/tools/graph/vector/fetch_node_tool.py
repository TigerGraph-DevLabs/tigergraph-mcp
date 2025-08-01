from typing import List, Optional
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph

from tigergraph_mcp.tools import TigerGraphToolName


class FetchNodeToolInput(BaseModel):
    """Input schema for fetching a node's embedding vector from a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph from which the node will be fetched."
    )
    node_id: str | int = Field(..., description="The identifier of the node.")
    vector_attribute_name: Optional[str] = Field(
        None,
        description="The name of the vector attribute to fetch from the node (optional).",
    )
    node_type: Optional[str] = Field(None, description="The type of the node (optional).")


tools = [
    Tool(
        name=TigerGraphToolName.FETCH_NODE,
        description="""Fetches the embedding vector of a node in a TigerGraph database using
TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
node_id = "Alice"
vector_attribute_name = "emb_1"  # Optional
node_type = "Person"  # Optional
```

If `vector_attribute_name` is not provided, no vector will be retrieved, and
a warning will be returned.
""",
        inputSchema=FetchNodeToolInput.model_json_schema(),
    )
]


async def fetch_node(
    graph_name: str,
    node_id: str | int,
    vector_attribute_name: Optional[str] = None,
    node_type: Optional[str] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        if vector_attribute_name is None:
            return [
                TextContent(
                    type="text",
                    text="⚠️ `vector_attribute_name` was not provided, so no vector was fetched.",
                )
            ]
        vector = graph.fetch_node(node_id, vector_attribute_name, node_type)
        if vector is None:
            message = (
                f"⚠️ Vector attribute '{vector_attribute_name}' not found for "
                f"node '{node_id}' in graph '{graph_name}'."
            )
        else:
            message = (
                f"📦 Retrieved vector for node '{node_id}' "
                f"(type: {node_type or 'default'}): {vector}"
            )
    except Exception as e:
        message = (
            f"❌ Failed to fetch node vector for '{node_id}' in graph '{graph_name}': {str(e)}"
        )
    return [TextContent(type="text", text=message)]
