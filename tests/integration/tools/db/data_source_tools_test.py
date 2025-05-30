import pytest

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from tests.integration.base_graph_fixture import BaseFixture
from tigergraph_mcp import TigerGraphToolName


class TestDataSourceTools(BaseFixture):
    @pytest.mark.asyncio
    async def test_data_source_tools(self):
        SAMPLE_PATH = "s3a://tigergraph-solution-kits/connected_customer/customer_360/data/Session.csv"  # Replace with actual path

        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Create the data source
                create_result = await session.call_tool(
                    TigerGraphToolName.CREATE_DATA_SOURCE,
                    arguments={
                        "name": "data_source_1",
                        "data_source_type": "s3",
                        "access_key": "",
                        "secret_key": "",
                        "extra_config": {
                            "file.reader.settings.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
                        },
                    },
                )
                assert "✅ Successfully created data source" in str(create_result)

                try:
                    # Get the data source
                    get_result = await session.call_tool(
                        TigerGraphToolName.GET_DATA_SOURCE,
                        arguments={
                            "name": "data_source_1",
                        },
                    )
                    get_result_text = str(get_result)
                    assert "✅ Successfully retrieved configuration for data source" in get_result_text

                    # Preview sample data
                    preview_result = await session.call_tool(
                        TigerGraphToolName.PREVIEW_SAMPLE_DATA,
                        arguments={
                            "path": SAMPLE_PATH,
                            "data_source_type": "s3",
                            "data_source": "data_source_1",
                            "data_format": "csv",
                            "size": 5,
                            "has_header": True,
                            "separator": ",",
                            "eol": "\\n",
                            "quote": '"',
                        },
                    )
                    preview_text = str(preview_result)
                    assert "✅ Previewed sample data from" in preview_text

                finally:
                    # Drop the data source
                    drop_result = await session.call_tool(
                        TigerGraphToolName.DROP_DATA_SOURCE,
                        arguments={"name": "data_source_1"},
                    )
                    assert "Successfully dropped data source" in str(drop_result)
