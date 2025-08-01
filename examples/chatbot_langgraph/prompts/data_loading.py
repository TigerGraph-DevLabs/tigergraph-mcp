LOAD_CONFIG_FILE_PROMPT="""
## Objective
Your task is to generate the first step of a TigerGraph loading job config: define the `files` section with valid
file aliases, file paths, and CSV parsing options — but **do not** define any node or edge mappings yet.

## Instructions
Follow these best practices with examples:

- **File Reference Correctness**:  
    Every file must have a unique alias and a valid path.  
    Example:  
    ```json
    "file_alias": "f_customer",  
    "file_path": "/data/input/customer.csv"
    ```

- **S3 vs Local Paths**:  
    Use the correct format for paths:
    - Local file: starts with `/`, e.g. `"/data/files/file.csv"`
    - S3 file: use `$<data source name>:s3://...`, e.g. `"$s3_main:s3://my-bucket/data.csv"`  
    Example:  
    ```json
    "file_path": "$s3_main:s3://tg-datasets/bank/transactions.csv"
    ```

- **Single Alias per File**:  
    Do not reuse or define multiple aliases for the same file path.
    For instance, do not assign both `"f_orders"` and `"f_orders_v2"` to the same `/data/orders.csv`.

- **CSV Parsing Configuration**:  
    Always include parsing options with the following defaults unless overridden:
    - `separator`: set to `","`
    - `header`: set to `True` (first row is the header)
    - `quote`: set to `"DOUBLE"`  
    Example:
    ```json
    "csv_parsing_options": {
    "separator": ",",
    "header": True,
    "quote": "DOUBLE"
    }
    ```

## Output Format
Provide a Python code block containing only the `"files"` section of the loading job config.

Example:

```python
files = [
    {
        "file_alias": "f_customer",
        "file_path": "/data/files/customer.csv",
        "csv_parsing_options": {
            "separator": ",",
            "header": True,
            "quote": "DOUBLE",
        },
    },
    {
        "file_alias": "f_transaction",
        "file_path": "$s3data:s3://company-data/finance/transactions.csv",
        "csv_parsing_options": {
            "separator": ",",
            "header": True,
            "quote": "DOUBLE",
        },
    },
]
```
"""

LOAD_CONFIG_NODE_MAPPING_PROMPT="""
## Objective
Your task is to add **node mappings** to the loading job config based on the previously defined `files` section.
This is Step 2 in the loading job config process — do not add any edge mappings yet.

You must analyze each file’s columns and detect **all** node types it contributes to based on the schema.
This is critical for enabling correct edge mappings in the next step.

## Instructions
### File Previews

- File 1: `user_data.csv`
    ```
    user_id,name,age,account_id,email,phone
    u001,Alice,30,a123,alice@example.com,555-1111
    ```

- File 2: `account_data.csv`
    ```
    account_id,created_on
    a123,2021-06-01
    ```

### Best Practices and Examples

- **Primary Node Identification**:
    - File 1 has `user_id` which matches the schema key for `User`, so map it as a `User` node.
    - Map its attributes: `name`, `age`.

- **Map All Relevant Attributes**:
    - Also map `email`, `phone`, and `account_id` — even if some might be edge-related later, they must be included if they match node types in the schema.

- **Multi-File Support for Node Types**:
    - File 2 also defines a node type: `Account`, using `account_id` as the primary key.
    - Even though `account_id` appears in both files, define it independently in both.

- **Scan All Columns**:
    - In File 1:
    - `email` maps to an `Email` node,
    - `phone` maps to a `Phone` node,
    - `account_id` maps to an `Account` node.
    - So, File 1 defines 4 node types: `User`, `Email`, `Phone`, `Account`.

- **Correct Mapping Format**:
    ```json
    {
    "target_name": "Email",
    "attribute_column_mappings": {
        "email_id": "email"
    }
    }
    ```

- **Segment Mixed Node Files**:
    - Each of the 4 node types detected in File 1 must have its own node mapping block.

- **Validate Column Existence**:
    - Only map attributes that are present in the file’s header. Skip any schema attributes not in the file.

- **One Alias per File Path**:
    - Do not duplicate or reuse aliases for other files.

- **Respect Schema Naming**:
    - Match the `target_name` exactly to the schema node name.
    - All mapped attributes must be valid under the schema definition of the given node type.

## Output Format
Provide an updated `"files"` section with `node_mappings` added.

Example:

```python
files = [
    {
        "file_alias": "f_user_data",
        "file_path": "/data/user_data.csv",
        "csv_parsing_options": {
            "separator": ",",
            "header": True,
            "quote": "DOUBLE"
        },
        "node_mappings": [
            {
                "target_name": "User",
                "attribute_column_mappings": {
                    "id": "user_id",
                    "name": "name",
                    "age": "age"
                }
            },
            {
                "target_name": "Email",
                "attribute_column_mappings": {
                    "email_id": "email"
                }
            },
            {
                "target_name": "Phone",
                "attribute_column_mappings": {
                    "phone_id": "phone"
                }
            },
            {
                "target_name": "Account",
                "attribute_column_mappings": {
                    "account_id": "account_id"
                }
            }
        ]
    },
    {
        "file_alias": "f_account_data",
        "file_path": "/data/account_data.csv",
        "csv_parsing_options": {
            "separator": ",",
            "header": True,
            "quote": "DOUBLE"
        },
        "node_mappings": [
            {
                "target_name": "Account",
                "attribute_column_mappings": {
                    "account_id": "account_id",
                    "created_on": "created_on"
                }
            }
        ]
    }
]
```
"""

LOAD_CONFIG_EDGE_MAPPING_PROMPT = """
## Objective
Use the schema to validate edge directionality, node types, and edge attributes.
Only define edge mappings for files that include both the source and target node identifier columns.
Do not fabricate mappings that cannot be grounded in both the file contents and the schema definition.

## Instructions
Follow these best practices when adding edge mappings:

- **Interpret File Role**:
    - Each file is typically either node-oriented (describes a node and its attributes) or edge-oriented (defines a relationship between two nodes).
    - Node files may also embed foreign key references to other nodes — infer edges accordingly only if schema confirms the relationship.

- **Validate Edge Direction and Existence**:
    - Confirm the presence of an edge between two node types using the schema.
    - Ensure edge direction matches the schema: the edge must go from `from_type` → `to_type`.

- **Do Not Guess Missing Columns**:
    - Do not add an edge mapping unless both the source and target node identifier columns exist in the file.
    - Do not define edge mappings based on attribute mappings alone — they must be grounded in actual node identifiers.

- **Handle Multi-Node Columns**:
    - If a file maps multiple nodes (e.g., `Individual`, `Email`, and `Phone`), check each pair of node columns for valid edges in the schema.
    - Create separate edge mappings per valid node pair.

- **Correct Mapping Format**:
    - Every edge mapping must follow this structure:
    ```json
    {
        "target_name": "EdgeTypeName",
        "source_node_column": "source_col",
        "target_node_column": "target_col",
        "attribute_column_mappings": {
        "attr1": "file_col1",
        ...
        }
    }
    ```
    - Only include `attribute_column_mappings` keys present in the schema and backed by actual file columns.

- **Support Mixed Files**:
    - Files that contain multiple edge relationships must declare each mapping separately.
    - Never merge unrelated edges into a single mapping block.

- **Preserve File Alias and Ownership**:
    - Each edge mapping must remain within the context of the file it originated from.
    - Use the correct file alias and attach mappings under the corresponding file block.

- **Avoid Redundant or Invalid Mappings**:
    - Do not add a mapping if the same edge has already been covered elsewhere unless this file uniquely contributes to it.
    - Avoid adding mappings for node-attribute pairs that are not valid edge endpoints.

## Output Format

Provide a short introduction, followed by the complete Python code block with the final `loading_job_config`,
including node and edge mappings in each file.

Example:

Here is a draft loading job config based on your schema and file structure.

```python
graph_name = "Social"
loading_job_config = {
    "loading_job_name": "loading_job_Social",
    "files": [
        {
            "file_alias": "f_person",
            "file_path": "/data/files/person.csv",
            "csv_parsing_options": {
                "separator": ",",
                "header": True,
                "quote": "DOUBLE",
            },
            "node_mappings": [
                {
                    "target_name": "Person",
                    "attribute_column_mappings": {
                        "id": "name",
                        "age": "age",
                        "gender": "gender",
                        "city": "city",
                    },
                }
            ],
        },
        {
            "file_alias": "f_friendship",
            "file_path": "$s1:s3://bucket/path/friendship.csv",
            "csv_parsing_options": {
                "separator": ",",
                "header": True,
                "quote": "DOUBLE",
            },
            "node_mappings": [
                {
                    "target_name": "Person",
                    "attribute_column_mappings": {
                        "id": "from_name",
                    },
                },
                {
                    "target_name": "Person",
                    "attribute_column_mappings": {
                        "id": "to_name",
                    },
                }
            ],
            "edge_mappings": [
                {
                    "target_name": "Friendship",
                    "source_node_column": "from_name",
                    "target_node_column": "to_name",
                    "attribute_column_mappings": {
                        "since": "since",
                        "closeness": "closeness",
                    },
                }
            ],
        },
    ],
}
```

Please confirm if this looks good by replying with "confirmed", "approved", "go ahead", or "ok". Or tell me if you want to make any changes.
"""

EDIT_LOADING_JOB_PROMPT = """
## Objective
Refine the proposed TigerGraph loading job configuration based on a single round of user feedback.

## Instructions
- Receive the current loading job configuration draft and the user's comments or change requests.
- Apply the requested changes fully and accurately.
- Follow TigerGraph loading best practices, ensuring mappings are consistent with the graph schema and data file contents.
- Do not add speculative changes beyond what the user requested.
- This task is **single-pass only** — do not ask for clarifications or initiate iterative feedback.
- Output the revised loading job configuration in Python syntax, properly formatted and ready for review or execution.

## Output Format
Provide a clear, user-friendly message with three parts: a short update message, the revised loading job config in Python syntax, and a confirmation request. 
Only show the results — **do not include any process or reasoning!**

Follow this structure:

1. Short update message  
2. Python code block showing the revised config  
3. Clear confirmation request

Example:

I've updated the loading job config based on your feedback.

```python
graph_name = "Social"
loading_job_config = {
    "loading_job_name": "loading_job_Social",
    "files": [
        {
            "file_alias": "f_person",
            "file_path": "/data/files/person_data.csv",
            "csv_parsing_options": {
                "separator": ",",
                "header": True,
                "quote": "DOUBLE",
            },
            "node_mappings": [
                {
                    "target_name": "Person",
                    "attribute_column_mappings": {
                        "id": "name",
                        "age": "age",
                        "gender": "gender",
                        "city": "city",
                    },
                }
            ],
        },
        {
            "file_alias": "f_friendship",
            "file_path": "$s1:s3://bucket-name/path/to/friendship_data.csv",
            "csv_parsing_options": {
                "separator": ",",
                "header": True,
                "quote": "DOUBLE",
            },
            "node_mappings": [
                {
                    "target_name": "Person",
                    "attribute_column_mappings": {
                        "id": "from_name",
                    },
                },
                {
                    "target_name": "Person",
                    "attribute_column_mappings": {
                        "id": "to_name",
                    },
                }
            ],
            "edge_mappings": [
                {
                    "target_name": "Friendship",
                    "source_node_column": "from_name",
                    "target_node_column": "to_name",
                    "attribute_column_mappings": {
                        "since": "since",
                        "closeness": "closeness",
                    },
                }
            ],
        },
    ],
}
```

Let me know if this looks correct or if you'd like to make additional edits.
"""

RUN_LOADING_JOB_PROMPT = """
## Objective
Execute the finalized and confirmed TigerGraph data loading job configuration.

## Instructions
- Use the given, validated loading job config exactly as provided.
- Call the TigerGraph loading tool to ingest data according to the config.
- If the load fails, display the full error message returned by the tool.
- Allow retry with an updated config if an error occurs.
- If any warnings occur during execution, include the full warning messages in the final output.
- Do not include any suggestions, hints, or commands related to 'SHOW LOADING ERROR', even if present in the original tool response.

## Output Format
A clear confirmation message indicating that the data loading job completed successfully,  
or the full error messages if the execution fails,  
or the full warning messages if the execution completes with warnings (excluding any mention of 'SHOW LOADING ERROR').
"""
