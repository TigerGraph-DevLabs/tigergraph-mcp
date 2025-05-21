# Changelog

---
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
