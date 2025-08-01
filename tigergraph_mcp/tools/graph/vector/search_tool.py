from typing import List, Optional, Set
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class SearchToolInput(BaseModel):
    """Input schema for vector-based node search."""

    graph_name: str = Field(..., description="The name of the graph to search in.")
    data: List[float] = Field(..., description="The query vector to search for similar nodes.")
    vector_attribute_name: str = Field(
        ..., description="The name of the vector attribute to search against."
    )
    node_type: Optional[str] = Field(
        None, description="The node type to restrict the search to (optional)."
    )
    limit: int = Field(
        10, description="The number of most similar nodes to return (default is 10)."
    )
    return_attributes: Optional[str | List[str]] = Field(
        None,
        description="Attributes to return with the result (optional, can be a single string or "
        "list of strings).",
    )
    candidate_ids: Optional[Set[str]] = Field(
        None, description="Specific node IDs to limit the search to (optional)."
    )


tools = [
    Tool(
        name=TigerGraphToolName.SEARCH,
        description="""Searches for nodes most similar to a given query vector in a TigerGraph
database using TigerGraphX.

Example input:
```python
graph_name = "SocialGraph"
data = [0.2, 0.2, 0.2]
vector_attribute_name = "emb_1"
node_type = "Person"  # Optional
limit = 2
return_attributes = ["name", "gender"]
candidate_ids = None  # Optional
```

This tool performs a vector similarity search and returns the most similar nodes based on the given
vector.
""",
        inputSchema=SearchToolInput.model_json_schema(),
    )
]


async def search(
    graph_name: str,
    data: List[float],
    vector_attribute_name: str,
    node_type: Optional[str] = None,
    limit: int = 10,
    return_attributes: Optional[str | List[str]] = None,
    candidate_ids: Optional[Set[str]] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        results = graph.search(
            data=data,
            vector_attribute_name=vector_attribute_name,
            node_type=node_type,
            limit=limit,
            return_attributes=return_attributes,
            candidate_ids=candidate_ids,
        )
        if not results:
            message = f"⚠️ No similar nodes found in graph '{graph_name}'."
        else:
            formatted = "\n".join(str(entry) for entry in results)
            message = f"🔍 Search results:\n{formatted}"
    except Exception as e:
        message = f"❌ Failed to perform vector search on graph '{graph_name}': {str(e)}"

    return [TextContent(type="text", text=message)]
