# TigerGraph-MCP

TigerGraph-MCP enables AI agents to interact with TigerGraph through the **Model Context Protocol (MCP)**. It exposes TigerGraph's graph capabilities via an MCP-compliant API, allowing LLM-based agents to retrieve contextual data, perform actions, and reason with connected information.

---

## Requirements

This project requires **Python 3.10, 3.11, or 3.12** and **TigerGraph 4.1 or later**. Ensure you meet the following prerequisites before proceeding:

### **1. Python**

- Ensure Python 3.10, 3.11, or 3.12 is installed on your system.
- You can download and install it from the [official Python website](https://www.python.org/downloads/).

### **2. TigerGraph**

TigerGraph **version 4.1 or higher** is required to run TigerGraph-MCP. You can set it up using one of the following methods:

- **TigerGraph DB**: Install and configure a local instance.
- **TigerGraph Savanna**: Use a managed TigerGraph instance in the cloud.
- **TigerGraph Docker**: Run TigerGraph in a containerized environment.

> - ⚠️ **Minimum Required Version: TigerGraph 4.1**
> - ✅ **Recommended Version: TigerGraph 4.2+** to enable **TigerVector** and advanced hybrid retrieval features.

Download from the [TigerGraph Downloads page](https://dl.tigergraph.com/), and follow the [official documentation](https://docs.tigergraph.com/home/) for setup.

---

## Installation Steps

### **Option 1: Install from PyPI**

The easiest way to get started is by installing TigerGraph-MCP from PyPI. A virtual environment is recommended:

```bash
pip install tigergraph-mcp
```

#### **Verify Installation**

Run the following command to verify the installation:

```bash
python -c "import tigergraph_mcp; print('TigerGraph-MCP installed successfully!')"
```

Expected output:

```
TigerGraph-MCP installed successfully!
```

---

### **Option 2: Build from Source**

If you want to explore or modify the code, clone the repository and install it manually. TigerGraph-MCP uses **Poetry** to manage dependencies.

First, install Poetry by following the [Poetry installation guide](https://python-poetry.org/docs/#installation).

Then, clone the repo and install:

```bash
git clone https://github.com/TigerGraph-DevLabs/tigergraph-mcp.git
cd tigergraph-mcp
```

#### **Core Installation**

If you need only the core functionality of TigerGraph-MCP (without running application examples like AI Agent, unit tests, or integration tests), run:

```bash
poetry env use python3.12  # Replace with your Python version (3.10–3.12)
poetry install --without dev
```

This command will:

- Install only the dependencies required for the core features of TigerGraph-MCP.

#### **Development Installation**

If you’re contributing to the project or want to use advanced features like running the AI Agent examples or test cases, run:

```bash
poetry env use python3.12  # Replace with your Python version (3.10–3.12)
poetry install --with dev
```

This command will:

- Install all core dependencies.
- Include development dependencies defined under `[tool.poetry.group.dev.dependencies]` in `pyproject.toml`.

#### **Verify Setup**

After installing dependencies, verify your setup by listing the installed packages:

```bash
poetry show --with dev
```

This ensures all required dependencies (including optional ones) are successfully installed.

#### Activate the Virtual Environment

Activate the environment using:

```bash
eval $(poetry env activate)
```

For more information about managing virtual environments in Poetry, please refer to the official documentation: [Managing Environments](https://python-poetry.org/docs/managing-environments/).

## 🚀 Getting Started: Choose Your Interface

We recommend **LangGraph** as the preferred interface for using TigerGraph-MCP, especially for advanced workflows like schema creation, data loading, and algorithm orchestration. However, if your workflow is relatively simple or you're just getting started, **CrewAI** may be easier to adopt initially. **GitHub Copilot Chat** is also supported for lightweight use cases directly in VS Code.

TigerGraph-MCP supports three main interfaces:

### ✅ Recommended: Using TigerGraph-MCP Tools with LangGraph

LangGraph is ideal for building **stateful, agent-based workflows** that involve complex tool chaining and strict schema compliance. It offers the highest level of flexibility and control for power users and is the recommended framework going forward.

* Setup guide: [`docs/langgraph_setup.md`](./docs/langgraph_setup.md)
* Full chatbot implementation using LangGraph and TigerGraph-MCP:
  [chatbot_langgraph](./examples/chatbot_langgraph)

### Using TigerGraph-MCP Tools with CrewAI

CrewAI was the original framework used for implementing agentic workflows in TigerGraph-MCP. It provides a **simpler and more approachable starting point**, especially for basic workflows. However, as our workflows grew in complexity, CrewAI’s limitations in agent definition and orchestration became more apparent. We now recommend LangGraph for most use cases, unless your workflow remains relatively simple.

* Setup guide: [`docs/crewai_setup.md`](./docs/crewai_setup.md)
* Full chatbot implementation using CrewAI and TigerGraph-MCP:
  [chatbot_crewai](./examples/chatbot_crewai)

### Using TigerGraph-MCP Tools with GitHub Copilot Chat in VS Code

For quick tasks or straightforward tool invocations, you can use **GitHub Copilot Chat** directly in VS Code. This works well for simple tools, but may struggle with the nested parameters and best practices required by more advanced operations like data loading or schema creation.

* Setup guide: [`docs/copilot_setup.md`](./docs/copilot_setup.md)



## Core MCP Features

TigerGraph-MCP currently supports **34 MCP tools** that cover a broad spectrum of functionalities, including:

#### Graph Operations
- Manage schemas
- Handle data loading and clearing
- Manipulate nodes and edges
- Access graph data
- Execute queries such as breadth-first search and neighbor retrieval

#### Vector Operations
- Perform vector upserts and fetches
- Conduct multi-attribute similarity searches
- Retrieve top-k similar nodes

#### Database Operations
- Manage external data sources by creating, dropping, and previewing sample data

## Roadmap

We are continuously working on enhancing our features. Our upcoming improvements include:

#### Enhanced API Support
- Expand API coverage to include comprehensive database-level functionalities

#### Schema Management
- Support dynamic schema updates
- Implement keyword validation
- Enable real-time schema refresh

#### Data Loading
- Facilitate data ingestion from local files
- Offer granular control over loading job creation and execution

#### NetworkX Compatibility
- Extend node, edge, and neighbor operations to closely mirror the NetworkX interface

#### Graph Algorithms
- Integrate commonly used graph algorithms for built-in analytics
