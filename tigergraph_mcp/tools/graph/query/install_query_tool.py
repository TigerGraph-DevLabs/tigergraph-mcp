from pydantic import BaseModel, Field
from mcp.types import Tool, TextContent
from typing import List

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class InstallQueryToolInput(BaseModel):
    """Input schema for installing a GSQL query on a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph where the query will be installed."
    )
    query_name: str = Field(..., description="The name of the query to install.")


tools = [
    Tool(
        name=TigerGraphToolName.INSTALL_QUERY,
        description="""Installs a GSQL query on a TigerGraph graph using TigerGraphX.

Examples:
```python
graph_name = "Social"
query_name = "getFriends"
````

Notes:

* The `query_name` must correspond to a query that has already been created using `create_query`.
* Returns True if the query was successfully installed; otherwise returns False.
  """,
        inputSchema=InstallQueryToolInput.model_json_schema(),
    )
]


async def install_query(graph_name: str, query_name: str) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        success = graph.install_query(query_name)
        if success:
            message = f"✅ Query '{query_name}' successfully installed on graph '{graph_name}'."
        else:
            message = f"⚠️ Query '{query_name}' installation on graph '{graph_name}' failed."
    except Exception as e:
        message = f"❌ Failed to install query '{query_name}' on graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
