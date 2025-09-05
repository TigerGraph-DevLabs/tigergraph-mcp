# Changelog

---
### 0.2.3
- feat: add MCP tool to check if a query is installed on a TigerGraph graph

### 0.2.2
- feat: add support for numeric column indices in load data tool

### 0.2.1
- doc: fix broken links and update command usage examples
- feat: add automatic retry logic for schema creation on failure
- feat: fetch latest schema before executing data load
- chore: upgrade TigerGraphX to 0.2.13 to fix column name spacing issue

### 0.2.0
- doc: add LangGraph chatbot usage examples
- feat: format code to comply with ruff lint rules (E, W, F, N, R)
- feat: upgrade TigerGraph to 0.2.12 to enable reserved keyword validation in schema
- feat: enforce use of 's3a' protocol for S3 files in preview sample data tool
- feat: add more confirmation keywords and helper method for detection
- feat: skip empty user input in single-line mode during assistant interaction
- feat: enhance RUN_LOADING_JOB_PROMPT to improve data loading stability
- chore: suppress httpx INFO logs to reduce console noise during LLM calls
- feat: ensure tools are re-executed for repeated user commands to fetch latest results
- fix: update metadata listing tool description for accuracy and clarity
- doc: update README.md

### 0.1.6
feat: add MCP tool to create schema and load data into TigerGraph

### 0.1.5
- feat: add example using LangGraph LLM and agents to call TigerGraph-MCP
- feat: upgrade TigerGraphX to v0.2.9 with new TigerGraphDatabase class integration
- feat: add run algorithm subgraph to onboarding workflow
- feat: add MCP tools for update data source, get/drop all data sources, run gsql, and list metadata

### 0.1.4
- feat: enable multi-turn human-in-the-loop schema confirmation for iterative refinement
- feat: enable multi-turn human-in-the-loop loading job confirmation for iterative refinement
- feat: support onboarding in chat flow
- feat: split schema drafting into modular tasks for column classification and schema generation

### 0.1.3
- feat: ensure MCP tools are VS Code and JSON schema compatible
- refactor: organize tools into separate graph and database categories
- feat: add MCP tools for data source management and previewing sample data, with integration tests
- feat: support multi-step task execution with sequential tool orchestration
- feat: support anonymous S3 access, enhance schema agent output, and improve multi-file schema creation and agent prompts
- docs: add README instructions for installation and usage with CrewAI and Copilot Chat

## 0.1.2
- feat: add example tigergraph_chat to demonstrate use CrewAI to call MCP tools
- feat: add MCP tools for edge, statistics, and vector operations and corresponding integration test cases
- feat: add MCP tools for query operations and corresponding integration test cases
- feat: add agents, tasks and crews for node operations
- feat: add agents, tasks and crews for edge, query, and vector operations
- feat: support connecting to TigerGraph via .env-based environment variables
- feat: add MCP tools for creating/installing/running/dropping queries and corresponding integration test cases
- feat: add agents, tasks and crews for creating/installing/running/dropping queries

## 0.1.1
- fix: normalize nodes_for_adding to handle tuple-to-list conversion from JSON in add_nodes tool

## 0.1.0
- feat: add MCP tools for schema operations
- feat: add MCP tools for data operations
- feat: add MCP tools for node operations
