from typing import List, Optional
from pydantic import Field
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class SearchMultiVectorAttributesInput(BaseModel):
    """Input schema for searching with multiple vector attributes."""

    graph_name: str = Field(..., description="The name of the graph to search in.")
    data: List[float] = Field(..., description="The query vector to search for similar nodes.")
    vector_attribute_names: List[str] = Field(
        ...,
        description="A list of vector attribute names to use for similarity search.",
    )
    node_types: Optional[List[str]] = Field(
        None,
        description="List of node types corresponding to each vector attribute (optional).",
    )
    limit: int = Field(
        10, description="The number of most similar nodes to return (default is 10)."
    )
    return_attributes_list: Optional[List[List[str]]] = Field(
        None,
        description="List of attributes to return per node type (optional).",
    )


tools = [
    Tool(
        name=TigerGraphToolName.SEARCH_MULTI_VECTOR_ATTRIBUTES,
        description="""Searches for nodes most similar to a given query vector using multiple
vector attributes.

Single Node Type Example:
```python
G = Graph(graph_schema)
G.upsert(
    data=[
        {"name": "Alice", "age": 30, "gender": "Female",
         "emb_1": [0.1, 0.2, 0.3], "emb_2": [0.2, 0.4, 0.6]},
        {"name": "Bob", "age": 32, "gender": "Male",
         "emb_1": [0.4, 0.5, 0.6], "emb_2": [0.5, 0.6, 0.7]},
        {"name": "Eve", "age": 29, "gender": "Female",
         "emb_1": [0.3, 0.2, 0.1], "emb_2": [0.1, 0.2, 0.3]},
    ]
)

results = G.search_multi_vector_attributes(
    data=[0.1, 0.2, 0.3],
    vector_attribute_names=["emb_1", "emb_2"],
    limit=2,
    return_attributes_list=[["name", "gender"], ["name"]],
)
```

Multiple Node Types Example:
```python
G = Graph(graph_schema)
G.upsert(
    data=[
        {"name": "Alice", "age": 30, "gender": "Female",
         "emb_1": [0.1, 0.2, 0.3], "emb_2": [0.2, 0.4, 0.6]},
        {"name": "Bob", "age": 32, "gender": "Male",
         "emb_1": [0.4, 0.5, 0.6], "emb_2": [0.5, 0.6, 0.7]},
        {"name": "Eve", "age": 29, "gender": "Female",
         "emb_1": [0.3, 0.2, 0.1], "emb_2": [0.1, 0.2, 0.3]},
    ],
    node_type="Person",
)

results = G.search_multi_vector_attributes(
    data=[0.1, 0.2, 0.3],
    vector_attribute_names=["emb_1", "emb_2"],
    node_types=["Person", "Person"],
    limit=2,
    return_attributes_list=[["name", "gender"], ["name"]],
)
```
""",
        inputSchema=SearchMultiVectorAttributesInput.model_json_schema(),
    )
]


async def search_multi_vector_attributes(
    graph_name: str,
    data: List[float],
    vector_attribute_names: List[str],
    node_types: Optional[List[str]] = None,
    limit: int = 10,
    return_attributes_list: Optional[List[List[str]]] = None,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        results = graph.search_multi_vector_attributes(
            data=data,
            vector_attribute_names=vector_attribute_names,
            node_types=node_types,
            limit=limit,
            return_attributes_list=return_attributes_list,
        )
        if not results:
            message = f"⚠️ No similar nodes found in graph '{graph_name}'."
        else:
            formatted = "\n".join(str(entry) for entry in results)
            message = f"🔍 Search results using multiple vector attributes:\n{formatted}"
    except Exception as e:
        message = f"❌ Failed to perform multi-vector search on graph '{graph_name}': {str(e)}"

    return [TextContent(type="text", text=message)]
