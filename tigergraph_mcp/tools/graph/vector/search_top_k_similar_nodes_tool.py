from typing import List, Optional
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class SearchTopKSimilarNodesInput(BaseModel):
    """Input schema for top-k similar node search using a reference node's vector."""

    graph_name: str = Field(..., description="The name of the graph to search in.")
    node_id: str = Field(..., description="The ID of the source node to compare against.")
    vector_attribute_name: str = Field(
        ...,
        description="The name of the vector attribute used for similarity comparison.",
    )
    node_type: Optional[str] = Field(
        None, description="The type of the node (optional, defaults to all node types)."
    )
    limit: int = Field(5, description="Number of most similar nodes to return (default is 5).")
    return_attributes: Optional[List[str]] = Field(
        None, description="List of attributes to include in the results (optional)."
    )


tools = [
    Tool(
        name=TigerGraphToolName.SEARCH_TOP_K_SIMILAR_NODES,
        description="""
Retrieves the top-k nodes most similar to a given node in a TigerGraph database based on the
specified vector attribute.

Example input:
```python
graph_name = "SocialGraph"
node_id = "Alice"
vector_attribute_name = "emb_1"
node_type = "Person"  # Optional
limit = 5
return_attributes = ["name", "gender"]
```
This tool compares the query node's vector with others and returns the most similar ones.
""",
        inputSchema=SearchTopKSimilarNodesInput.model_json_schema(),
    )
]


async def search_top_k_similar_nodes(
    graph_name: str,
    node_id: str,
    vector_attribute_name: str,
    node_type: Optional[str] = None,
    limit: int = 5,
    return_attributes: Optional[List[str]] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        results = graph.search_top_k_similar_nodes(
            node_id=node_id,
            vector_attribute_name=vector_attribute_name,
            node_type=node_type,
            limit=limit,
            return_attributes=return_attributes,
        )
        if not results:
            message = f"⚠️ No similar nodes found for node '{node_id}' in graph '{graph_name}'."
        else:
            formatted = "\n".join(str(entry) for entry in results)
            message = f"🔍 Top-k similar nodes for '{node_id}':\n{formatted}"
    except Exception as e:
        message = (
            f"❌ Failed to search similar nodes for '{node_id}' in graph '{graph_name}': {str(e)}"
        )

    return [TextContent(type="text", text=message)]
