import pytest

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from tests.integration.base_graph_fixture import BaseFixture
from tigergraph_mcp import TigerGraphToolName


class TestDataSourceTools(BaseFixture):
    @pytest.mark.asyncio
    async def test_data_source_tools_basic(self):
        SAMPLE_PATH = "s3a://tigergraph-solution-kits/connected_customer/customer_360/data/Session.csv"

        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                try:
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

                    # Get the data source
                    get_result = await session.call_tool(
                        TigerGraphToolName.GET_DATA_SOURCE,
                        arguments={"name": "data_source_1"},
                    )
                    get_result_text = str(get_result)
                    assert (
                        "✅ Successfully retrieved configuration for data source"
                        in get_result_text
                    )

                    # Update the data source
                    update_result = await session.call_tool(
                        TigerGraphToolName.UPDATE_DATA_SOURCE,
                        arguments={
                            "name": "data_source_1",
                            "data_source_type": "s3",
                            "access_key": "updated-key",
                            "secret_key": "updated-secret",
                            "extra_config": {
                                "file.reader.settings.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
                            },
                        },
                    )
                    assert "✅ Successfully updated data source" in str(update_result)

                    # Get the updated data source to verify
                    get_updated_result = await session.call_tool(
                        TigerGraphToolName.GET_DATA_SOURCE,
                        arguments={"name": "data_source_1"},
                    )
                    get_updated_text = str(get_updated_result)
                    assert (
                        "✅ Successfully retrieved configuration for data source"
                        in get_updated_text
                    )
                    assert "updated-key" in get_updated_text
                    assert "updated-secret" in get_updated_text

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

    @pytest.mark.asyncio
    async def test_data_source_list_and_drop_all(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Create two data sources
                try:
                    for i in [1, 2]:
                        result = await session.call_tool(
                            TigerGraphToolName.CREATE_DATA_SOURCE,
                            arguments={
                                "name": f"tmp_data_source_{i}",
                                "data_source_type": "s3",
                                "access_key": "",
                                "secret_key": "",
                                "extra_config": {
                                    "file.reader.settings.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.AnonymousAWSCredentialsProvider"
                                },
                            },
                        )
                        assert (
                            f"✅ Successfully created data source 'tmp_data_source_{i}'"
                            in str(result)
                        )

                    # Get all data sources
                    get_all_result = await session.call_tool(
                        TigerGraphToolName.GET_ALL_DATA_SOURCES,
                        arguments={},
                    )
                    get_all_text = str(get_all_result)
                    assert "✅ Successfully retrieved all data sources:" in get_all_text
                    assert "tmp_data_source_1" in get_all_text
                    assert "tmp_data_source_2" in get_all_text

                finally:
                    # Drop all data sources
                    drop_all_result = await session.call_tool(
                        TigerGraphToolName.DROP_ALL_DATA_SOURCES,
                        arguments={},
                    )
                    assert "✅ All data sources is dropped successfully." in str(
                        drop_all_result
                    )

                    # Get all data sources
                    get_all_result = await session.call_tool(
                        TigerGraphToolName.GET_ALL_DATA_SOURCES,
                        arguments={},
                    )
                    assert "ℹ️ No data sources found." in str(get_all_result)
