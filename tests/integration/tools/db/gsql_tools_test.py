import pytest

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from tests.integration.base_graph_fixture import BaseFixture
from tigergraph_mcp import TigerGraphToolName


class TestGSQLTool(BaseFixture):
    @pytest.mark.asyncio
    async def test_gsql_tool(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    TigerGraphToolName.GSQL,
                    arguments={"command": "LS"},
                )

                result_text = str(result)
                assert "✅ GSQL Response" in result_text
                assert "Graphs" in result_text or "Vertex Types" in result_text

    @pytest.mark.asyncio
    async def test_list_metadata_tool(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Test global metadata listing (no graph_name)
                result = await session.call_tool(
                    TigerGraphToolName.LIST_METADATA,
                    arguments={},
                )
                result_text = str(result)
                assert "✅ Successfully listed metadata" in result_text
                assert "Graphs" in result_text or "Vertex Types" in result_text
