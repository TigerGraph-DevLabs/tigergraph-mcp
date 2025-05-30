import pytest

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from tests.integration.base_graph_fixture import BaseFixture
from tigergraph_mcp import TigerGraphToolName


class TestDataTools2(BaseFixture):
    @pytest.mark.asyncio
    async def test_load_data_tmp(self):
        loading_job_config = {
            "loading_job_name": "loading_job_Customer360Graph",
            "files": [
                {
                    "file_alias": "individual_info",
                    "file_path": "$__s3_anonymous_source:s3a://tigergraph-solution-kits/connected_customer/customer_360/data/Individual_Info.csv",
                    "csv_parsing_options": {
                        "separator": ",",
                        "header": True,
                        "quote": "DOUBLE",
                    },
                    "node_mappings": [
                        {
                            "target_name": "Individual",
                            "attribute_column_mappings": {
                                "individual_id": "individual",
                                "first_name": "first_name",
                                "last_name": "last_name",
                                "credit_score": "credit_score",
                                "added_on": "added_on",
                                "city": "city",
                                "country": "country",
                                "zip": "zip",
                                "state": "state",
                            },
                        },
                        {
                            "target_name": "Email",
                            "attribute_column_mappings": {"email_id": "email"},
                        },
                        {
                            "target_name": "Phone",
                            "attribute_column_mappings": {"phone_id": "phone"},
                        },
                    ],
                    "edge_mappings": [
                        {
                            "target_name": "has_email",
                            "source_node_column": "individual",
                            "target_node_column": "email",
                        },
                        {
                            "target_name": "has_phone",
                            "source_node_column": "individual",
                            "target_node_column": "phone",
                        },
                        {
                            "target_name": "has_account",
                            "source_node_column": "individual",
                            "target_node_column": "account_ids",
                        },
                    ],
                },
                {
                    "file_alias": "account_info",
                    "file_path": "$__s3_anonymous_source:s3a://tigergraph-solution-kits/connected_customer/customer_360/data/Account_Info.csv",
                    "csv_parsing_options": {
                        "separator": ",",
                        "header": True,
                        "quote": "DOUBLE",
                    },
                    "node_mappings": [
                        {
                            "target_name": "Account",
                            "attribute_column_mappings": {
                                "account_id": "account_ids",
                                "created_on": "created_on",
                                "CC": "CC",
                                "cardLimit": "cardLimit",
                                "card_cat": "card_cat",
                                "loan": "loan",
                                "loan_type": "loan_type",
                                "loan_terms": "loan_terms",
                                "interest_rate": "interest_rate",
                            },
                        }
                    ],
                },
            ],
        }

        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    TigerGraphToolName.LOAD_DATA,
                    arguments={
                        "graph_name": "Customer360Graph",
                        "loading_job_config": loading_job_config,
                    },
                )
                assert "Data loaded successfully into graph" in str(result)
