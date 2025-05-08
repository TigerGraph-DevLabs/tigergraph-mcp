from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from mcp.types import Tool, TextContent

from tigergraphx import Graph
from tigergraph_mcp.tools import TigerGraphToolName


class RunQueryToolInput(BaseModel):
    """Input schema for running a pre-installed GSQL query on a TigerGraph graph."""

    graph_name: str = Field(
        ..., description="The name of the graph to run the query on."
    )
    query_name: str = Field(
        ..., description="The name of the pre-installed query to execute."
    )
    params: Optional[Dict] = Field(
        default_factory=dict, description="Parameters for the query, if any."
    )


tools = [
    Tool(
        name=TigerGraphToolName.RUN_QUERY,
        description="""Runs a pre-installed GSQL query on a TigerGraph graph using TigerGraphX.

Examples:
```python
graph_name = "Social"
query_name = "getFriends"
params = {"person": "Alice"}
````

Notes:

* The query must be installed on the graph.
* Parameters must match those defined in the GSQL query.
* Returns the query result as a list of dictionaries, or None if execution fails.
  """,
        inputSchema=RunQueryToolInput.model_json_schema(),
    )
]


async def run_query(
    graph_name: str,
    query_name: str,
    params: Optional[Dict] = {},
) -> List[TextContent]:
    try:
        graph = Graph.from_db(graph_name)
        result = graph.run_query(query_name, params or {})
        if result is None:
            result = f"⚠️ Query '{query_name}' on graph '{graph_name}' returned no result or failed."
        else:
            result = (
                f"✅ Query result for '{query_name}' on graph '{graph_name}':\n{result}"
            )
    except Exception as e:
        result = (
            f"❌ Failed to run query '{query_name}' on graph '{graph_name}': {str(e)}"
        )
    return [TextContent(type="text", text=result)]
