from typing import List
from pydantic import BaseModel, Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class CreateQueryToolInput(BaseModel):
    """Input schema for creating a GSQL query on a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph where the query will be installed."
    )
    gsql_query: str = Field(
        ...,
        description="A valid GSQL query string conforming to TigerGraph's GSQL syntax.",
    )


tools = [
    Tool(
        name=TigerGraphToolName.CREATE_QUERY,
        description="""Installs a GSQL query on a TigerGraph graph using TigerGraphX.

Examples:
```python
graph_name = "Social"
gsql_query = '''
CREATE QUERY getFriends(VERTEX<Person> person) FOR GRAPH Social {
  Start = {person};
  Friends = SELECT tgt FROM Start:s -(Friendship:e)->:tgt;
  PRINT Friends;
}
'''
````

Notes:

* The query must follow TigerGraph GSQL syntax.
* The target graph (`FOR GRAPH`) in the query must match `graph_name`.
* Returns True if the query was successfully created; otherwise returns False.
  """,
        inputSchema=CreateQueryToolInput.model_json_schema(),
    )
]


async def create_query(graph_name: str, gsql_query: str) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        success = graph.create_query(gsql_query)
        if success:
            message = f"✅ GSQL query successfully created on graph '{graph_name}'."
        else:
            message = (
                f"⚠️ Query creation on graph '{graph_name}' failed. "
                "Please verify the GSQL syntax and graph context."
            )
    except Exception as e:
        message = f"❌ Failed to create GSQL query on graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
