CLASSIFY_COLUMNS_PROMPT = """
## Role
Analyze the provided data tables and classify each column as one of: `primary_id`, `node`, or `attribute`. Also infer the data type.

> **Note:** Do not define node types or edge types at this stage. This step focuses only on per-column classification and type inference.
> The output should be structured per file and include every column except headers and null-only columns.

## Objective
1. Automatically infer the data type of each column.
2. Identify primary keys (columns with unique values) and mark them as `primary_id`.
3. For non-primary ID columns:
    - If the column is a reference to another entity or table → mark as `node`.
    - If the column contains a small number of repeated values or is not STRING/INT/UINT → mark as `attribute`.

## Instructions
- **Step 1: Infer data type**
  - Allowable types: `STRING`, `INT`, `UINT`, `FLOAT`, `DOUBLE`, `BOOL`, `DATETIME`.
  - Default to `STRING` unless clearly numeric or datetime.

- **Step 2: Detect primary_id**
  - If a column has unique values across all rows → classify as `primary_id`.

- **Step 3: For remaining columns, classify as `node` or `attribute`**

  **Heuristic-Based Rule**  
  - Use a combination of data type, value variety, row coverage, and data format characteristics to decide if a column represents a separate entity (`node`) or a property (`attribute`).

  **Type Constraint**  
  - Only consider columns with type `STRING`, `INT`, or `UINT` as potential `node` candidates.

  **Node Classification Heuristics**  
  - Classify a column as `node` if:
    - It has a moderate to high variety of values (roughly estimated ≥10% unique values based on sample or distribution),
    - It appears in most or all rows (i.e., column is not sparse or mostly null),
    - It shows consistent formatting or length patterns typical of entity identifiers (e.g., IDs),
    - And it is not already marked as a `primary_id`.

  **Attribute Defaults**  
  - If a column has:
    - Low uniqueness (many repeated values),
    - Or a data type not suitable for nodes (e.g. `FLOAT`, `DOUBLE`, `DATETIME`, `BOOL`),
    - Or sparse or inconsistent population,
    → classify it as `attribute`.

  **Avoid Bias by Column Name**  
  - Do not use column names directly to influence classification; rely only on structural and content heuristics.

  **Practical Examples**  
  - Columns like `email`, `device_id` with moderate to high uniqueness and consistent format should be classified as `node`.
  - Columns like `country`, `state`, or `department` with low uniqueness should be classified as `attribute`.

## Output Format

Provide a Markdown code block that shows:
- Each file name as a bullet entry.
- Under each file, list all data columns (except header-only or empty ones).
- For each column, provide:
  - The classification: one of `primary_id`, `node`, or `attribute`
  - The inferred data type: one of `STRING`, `INT`, `UINT`, `FLOAT`, `DOUBLE`, `BOOL`, `DATETIME`

Follow this format exactly:

```
- FileName1:
  - columnA: node, STRING
  - columnB: primary_id, STRING
  - columnC: attribute, INT
- FileName2:
  - columnD: primary_id, STRING
  - columnE: attribute, STRING
  - columnF: attribute, BOOL
```

Be thorough and conservative:
- Always include the inferred type.
- Do not guess edges or node types.
- Do not infer graph structure yet.

## Example Format
### Example Tables

**Table 1: Employee Data**

| email              | employee_id | manager_id | department | location      |
| ------------------ | ----------- | ---------- | ---------- | ------------- |
| alice@example.com  | E001        | E005       | Sales      | New York      |
| bob@example.com    | E002        | E005       | Sales      | New York      |
| carol@example.com  | E003        | E006       | Marketing  | San Francisco |

**Table 2: Employee_Project**

| employee_id | project_id | role      | start_date |
| ----------- | ---------- | --------- | ---------- |
| E001        | P100       | Developer | 2023-01-01 |
| E002        | P101       | Tester    | 2023-02-15 |
| E003        | P100       | Analyst   | 2023-03-01 |

### Example Output

```
- Employee:
  - email: node, STRING
  - employee_id: primary_id, STRING
  - manager_id: node, STRING
  - department: attribute, STRING
  - location: attribute, STRING

- Employee_Project:
  - employee_id: node, STRING
  - project_id: node, STRING
  - role: attribute, STRING
  - start_date: attribute, DATETIME
```
"""

DRAFT_SCHEMA_PROMPT = """
## Role
Using classified columns and table data, draft a complete TigerGraph schema including graph name, node types, and edge types following best practices.

## Objective
Your task is to:
1. Define node types with primary IDs and attributes based on classified columns and their originating tables.
2. Define edge types using table relationships and classified nodes.
3. Include all relationship-specific attributes.
4. Specify edge directionality.
5. Propose a graph name.
6. Output the complete schema in Markdown format.

## Instructions
### Example Tables

Assume the user previously provided the following data tables:

**Table 1: Employee**

| employee_id | email              | manager_id | department | location      |
| ----------- | ------------------ | ---------- | ---------- | ------------- |
| E001        | alice@example.com  | E005       | Sales      | New York      |
| E002        | bob@example.com    | E005       | Sales      | New York      |
| E003        | carol@example.com  | E006       | Marketing  | San Francisco |

**Table 2: Employee_Project**

| employee_id | project_id | role      | start_date |
| ----------- | ---------- | --------- | ---------- |
| E001        | P100       | Developer | 2023-01-01 |
| E002        | P101       | Tester    | 2023-02-15 |
| E003        | P100       | Analyst   | 2023-03-01 |

### Example Column Classification

Assume columns have been classified earlier as primary_id, node, or attribute with data types, for example:

- Employee:
  - employee_id: primary_id, STRING
  - email: node, STRING
  - manager_id: node, STRING
  - department: attribute, STRING
  - location: attribute, STRING

- Employee_Project:
  - employee_id: node, STRING
  - project_id: node, STRING
  - role: attribute, STRING
  - start_date: attribute, DATETIME

### Best Practices (Demonstrated with Example)

#### Node Types

- Nodes should have a unique primary ID, usually the primary_id column or inferred node column used as ID.
- Include the primary ID as part of the node’s attributes with its data type.
- Attributes come only from columns in the node’s own table (the one defining the primary ID).
- If a column is classified as a separate node, define it accordingly.

#### Edge Inference

- **Reference columns** (e.g., `manager_id` in the Employee table) imply an edge between two nodes of the same type:
  - `manages` from `Employee` → `Employee` is a **directed** edge.

- **Join tables** (e.g., `Employee_Project`) imply edges between two different node types:
  - `works_on_project` from `Employee` ↔ `Project` is an **undirected** edge with `role`, `start_date`.

- **Attribute columns linked to unique fields** (e.g., `email`) imply a connection to another node:
  - `has_email` from `Employee` ↔ `Email` is an **undirected** edge.

#### Edge Naming

- Use **snake_case** for edge names:
  - ✅ `works_on_project`
  - ✅ `has_email`
  - ❌ `WorksOnProject`

- Include FROM, TO, directionality, and attributes where applicable.

#### Directionality

- **Directed**:
  - Only apply directionality when the source and target are the **same node type** and the relationship is hierarchical or asymmetric.
  - Example: `Employee → Employee` via `manager_id` → use a **directed** edge (`manages`).

- For edges between **different node types**, do **not specify direction** unless the relationship explicitly implies a flow of control or hierarchy.
  - Example: `Employee` ↔ `Project` via `works_on_project` is **undirected**.

#### Graph Naming

- Choose a name related to the domain:
  - Example: `WorkforceGraph` for employee and project data.

- Use **PascalCase** (no spaces or underscores).


## Output Format
Provide a clear, user-friendly message with three parts: a short introduction, a Markdown schema proposal, and a confirmation request.  
Only show the results—**do not include any process or reasoning!**

Follow this structure:

1. Short introduction  
2. Markdown schema proposal (include graph name, all node types with primary IDs and attributes, and edge types)  
3. Clear confirmation request

Example:

Here is the updated schema including proposed node types, edge types, and graph name.

### Graph Name
WorkforceGraph

### Node Types
- **Employee** (primary_id: employee_id)
  - employee_id: STRING
  - department: STRING
  - location: STRING

- **Project** (primary_id: project_id)
  - project_id: STRING

- **Email** (primary_id: email)
  - email: STRING

### Edge Types
- **manages** (FROM: Employee, TO: Employee, directed)

- **works_on_project** (FROM: Employee, TO: Project, undirected)
  - role: STRING
  - start_date: DATETIME

- **has_email** (FROM: Employee, TO: Email, undirected)

Please confirm if this looks good by replying with "confirmed", "approved", "go ahead", or "ok". Or let me know if you'd like to revise anything.

"""

EDIT_SCHEMA_PROMPT = """
## Role
Refine the proposed TigerGraph schema based on a single round of user feedback.

## Instructions

- Receive the initial schema proposal along with the user's comments or change requests.
- Apply the requested changes accurately and completely.
- Use TigerGraph best practices to ensure structural consistency—for example, when adding a new node type,
    consider whether related edge types should also be introduced, if logically implied by the context.
- Avoid overreaching: only make logical inferences that enhance schema coherence, not speculative or structural overhauls.

⚠️ This task is **single-pass only** — do not ask follow-up questions or prompt the user for clarification.
Validation, iteration, and confirmation will occur in downstream steps.

- Output the revised schema in well-formatted Markdown.

## Output Format

Provide a clear, user-friendly message with three parts: a short introduction, a Markdown schema proposal, and a confirmation request. 
Only show the results—**do not include any process or reasoning!**

Follow this structure:

1. Short introduction  
2. Markdown schema proposal (include graph name, node types with primary IDs and attributes, and edge types)  
3. Clear confirmation request

Example:

Here is the schema I desgined based on your input.

### Graph Name
EmployeeGraph

### Node Types
- **employee** (primary_id: id)
    - id: STRING
    - name: STRING
    - email: STRING

- **department** (primary_id: dept_id)
    - dept_id: STRING
    - name: STRING

### Edge Types
- works_for (FROM: employee, TO: department, undirected)
    - since: DATE

- manages (FROM: employee, TO: employee, directed)
    - level: STRING

Please confirm if this looks good by replying with "confirmed", "approved", "go ahead", or "ok". Or tell me if you want to make any changes.
"""

CREATE_SCHEMA_PROMPT="""
## Role
Use the **final confirmed schema** to call the TigerGraph `CREATE_SCHEMA` tool.
Ensure the schema format is valid and matches tool expectations exactly.

## Output Format
A confirmation message indicating that the schema was successfully created or not.
"""

GET_SCHEMA_PROMPT = """
## Objective
Retrieve the schema of a graph from TigerGraph using the provided graph name.

## Instructions
Based on the provided graph name, you will retrieve and display the schema of the corresponding graph in TigerGraph. Ensure that the user has provided the correct graph name.

## Output Format
The schema of the graph, including details such as node types, edge types, and their respective attributes.

"""

