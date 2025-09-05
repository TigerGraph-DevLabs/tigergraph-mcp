from typing import List
from pydantic import BaseModel, Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class IsQueryInstalledToolInput(BaseModel):
    """Input schema for checking if a GSQL query is installed on a TigerGraph graph."""

    graph_name: str = Field(..., description="The name of the graph to check against.")
    query_name: str = Field(..., description="The name of the query to check.")


tools = [
    Tool(
        name=TigerGraphToolName.IS_QUERY_INSTALLED,
        description="""Checks if a GSQL query is installed on a TigerGraph graph using TigerGraphX.

Examples:
```python
graph_name = "Social"
query_name = "getFriends"
````

Notes:

* Returns True if the query is installed, otherwise False.
* Useful before attempting to run a query.
""",
        inputSchema=IsQueryInstalledToolInput.model_json_schema(),
    )
]


async def is_query_installed(
    graph_name: str,
    query_name: str,
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        installed = graph.is_query_installed(query_name)
        if installed:
            message = f"✅ Query '{query_name}' is installed on graph '{graph_name}'."
        else:
            message = f"⚠️ Query '{query_name}' is NOT installed on graph '{graph_name}'."
    except Exception as e:
        message = f"❌ Failed to check query '{query_name}' on graph '{graph_name}': {str(e)}"
    return [TextContent(type="text", text=message)]
