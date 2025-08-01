from typing import List, Optional
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class FetchNodesToolInput(BaseModel):
    """Input schema for fetching multiple nodes' embedding vectors."""

    graph_name: str = Field(
        ..., description="The name of the graph from which the nodes will be fetched."
    )
    node_ids: List[str] | List[int] = Field(
        ..., description="List of node identifiers."
    )
    vector_attribute_name: Optional[str] = Field(
        None, description="The name of the vector attribute to fetch (optional)."
    )
    node_type: Optional[str] = Field(
        None, description="The type of the nodes (optional)."
    )


tools = [
    Tool(
        name=TigerGraphToolName.FETCH_NODES,
        description="""Fetches the embedding vectors for multiple nodes in a TigerGraph database
using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
node_ids = ["Alice", "Bob"]
vector_attribute_name = "emb_1"  # Optional
node_type = "Person"  # Optional
```

If `vector_attribute_name` is not provided, no vectors will be retrieved, and a warning will
be returned.
""",
        inputSchema=FetchNodesToolInput.model_json_schema(),
    )
]


async def fetch_nodes(
    graph_name: str,
    node_ids: List[str] | List[int],
    vector_attribute_name: Optional[str] = None,
    node_type: Optional[str] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        if not vector_attribute_name:
            return [
                TextContent(
                    type="text",
                    text="⚠️ `vector_attribute_name` was not provided, so no vectors were fetched.",
                )
            ]

        vectors = graph.fetch_nodes(
            node_ids=node_ids,
            vector_attribute_name=vector_attribute_name,
            node_type=node_type,
        )
        if not vectors:
            message = f"⚠️ No vectors found for the specified node IDs in graph '{graph_name}'."
        else:
            formatted = "\n".join(
                f"{node_id}: {vec}" for node_id, vec in vectors.items()
            )
            message = f"📦 Retrieved vectors:\n{formatted}"
    except Exception as e:
        message = (
            f"❌ Failed to fetch vectors for nodes in graph '{graph_name}': {str(e)}"
        )

    return [TextContent(type="text", text=message)]
