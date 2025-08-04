from typing import List
from pydantic import BaseModel, Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class DropQueryToolInput(BaseModel):
    """Input schema for dropping a GSQL query from a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph from which the query will be dropped."
    )
    query_name: str = Field(..., description="The name of the query to drop.")


tools = [
    Tool(
        name=TigerGraphToolName.DROP_QUERY,
        description="""Drops a GSQL query from a TigerGraph graph using TigerGraphX.

Examples:
```python
graph_name = "Social"
query_name = "getFriends"
````

Notes:

* The query must already exist on the graph.
* Returns True if the query was successfully dropped, False otherwise.
  """,
        inputSchema=DropQueryToolInput.model_json_schema(),
    )
]


async def drop_query(
    graph_name: str,
    query_name: str,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        success = graph.drop_query(query_name)
        if success:
            message = f"✅ Query '{query_name}' was successfully dropped from graph '{graph_name}'."
        else:
            message = f"⚠️ Failed to drop query '{query_name}' from graph '{graph_name}'."
    except Exception as e:
        message = (
            f"❌ Error while dropping query '{query_name}' from graph '{graph_name}': {str(e)}"
        )
    return [TextContent(type="text", text=message)]
