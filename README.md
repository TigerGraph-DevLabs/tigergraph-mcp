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

> ⚠️ **Minimum Required Version: TigerGraph 4.1**
> ✅ **Recommended Version: TigerGraph 4.2+** to enable **TigerVector** and advanced hybrid retrieval features.

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

## Using TigerGraph-MCP Tools with GitHub Copilot Chat in VS Code

To enable the use of TigerGraph-MCP tools via GitHub Copilot Chat in VS Code, follow these steps:

### 1. Set Up GitHub Copilot Chat

Follow the [official GitHub Copilot Chat documentation](https://code.visualstudio.com/docs/copilot/chat/copilot-chat) to set up GitHub Copilot Chat.

### 2. Enable Agent Mode

Open GitHub Copilot Chat and switch to "Agent" mode using the Mode dropdown in the Chat view.

![](https://code.visualstudio.com/assets/docs/copilot/chat/copilot-chat/chat-mode-dropdown.png)

### 3. Create the `.env` File

In the root of your project, create a `.env` file with the following content:

```
OPENAI_API_KEY=<YOUR OPENAI KEY>
TG_HOST=http://127.0.0.1
TG_USERNAME=tigergraph
TG_PASSWORD=tigergraph
```

> Replace `<YOUR OPENAI KEY>` with your actual OpenAI API key.
> This configuration assumes you're running TigerGraph locally and logging in with a username and password. See the [Alternative Connection Setup Methods](https://tigergraph-devlabs.github.io/tigergraphx/reference/01_core/graph/#tigergraphx.core.graph.Graph.__init__) for additional ways to connect to TigerGraph.

### 4. Create `.vscode/mcp.json` and Start TigerGraph-MCP

Add the following configuration to `.vscode/mcp.json` in your workspace:

```json
{
  "inputs": [],
  "servers": {
    "tigergraph-mcp-server": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": [
        "-m",
        "tigergraph_mcp.main"
      ],
      "envFile": "${workspaceFolder}/.env"
    }
  }
}
```

> Note: Adjust the path in `"command"` if your virtual environment is located elsewhere.

After creating this file, you'll see a "Start" button appear above the line containing `"tigergraph-mcp-server":`. Click it to start the TigerGraph-MCP server.

### 5. Interact with the MCP Tool

You can now interact with the MCP tool by entering instructions like:

```
Suppose I have the following CSV files, please help create a graph schema in TigerGraph:

from_name,to_name,since,closeness
Alice,Bob,2018-03-05,0.9
Bob,Charlie,2020-07-08,0.7
Charlie,Alice,2022-09-10,0.5
Alice,Diana,2021-01-02,0.8
Eve,Alice,2023-03-05,0.6
```

GitHub Copilot will automatically select the `graph__create_schema` tool and configure the parameters.

Click "See more" to expand and edit the parameters if needed, or provide another suggestion in the chat to let Copilot modify the parameters based on your needs.

Then click the "Continue" button to run the tool. It will return a message such as:

```
I have created a TigerGraph schema named "SocialGraph"
```

indicating that the graph has been created successfully.

### 6. View Available Tools in TigerGraph-MCP

Click the Tools icon to view all available tools in TigerGraph-MCP.

![](https://code.visualstudio.com/assets/docs/copilot/chat/copilot-edits/agent-mode-select-tools.png)

If you'd like to request additional tools for TigerGraph, feel free to create an issue in the repository.

> Note: TigerGraph-MCP is based on [TigerGraphX](https://github.com/tigergraph/tigergraphx), a high-level Python library that provides a unified, Python-native interface for TigerGraph. For more details about the APIs, refer to the [TigerGraphX API Reference](https://tigergraph-devlabs.github.io/tigergraphx/reference/introduction/).

## Using TigerGraph-MCP Tools with LangChain or CrewAI

TigerGraph-MCP tools are designed to work well with modern LLM-based assistants like GitHub Copilot Chat. Many tools in the MCP suite are straightforward, and LLMs often generate high-quality parameters for them automatically. However, for more complex operations—such as schema creation or data loading—the inputs often require nested Python dictionaries and adherence to best practices that may not be well captured in the model’s training data.

For these advanced use cases, or if you prefer more control over tool usage, you can define custom AI agents and workflows using open-source frameworks like **LangGraph** or **CrewAI**.

This repository includes example implementations using both frameworks:
- [chatbot_langgraph](https://github.com/TigerGraph-DevLabs/tigergraph-mcp/tree/main/examples/chatbot_langgraph)
- [chatbot_crewai](https://github.com/TigerGraph-DevLabs/tigergraph-mcp/tree/main/examples/chatbot_crewai)

### How to Run the Demo

1. Clone this repository and install the package with development dependencies.
2. Activate your virtual environment.
3. Choose one of the following interfaces to launch:

---

#### Run with LangGraph

```bash
poe chatbot_langgraph
# or
python examples/chatbot_langgraph/main.py
```

You’ll see output like this:

```
Poe => python examples/chatbot_langgraph/main.py

================================== Ai Message ==================================

**Welcome!** I'm your **TigerGraph Assistant**—here to help you design schemas, load and explore data, run queries, and more.

Type what you'd like to do, or say **'onboarding'** to get started, or **'help'** to see what I can do. 🚀

================================ Human Message =================================

User:
```

Now you can chat directly with the agent in your terminal. A web-based UI is planned for future versions—stay tuned!

---

#### Run with CrewAI (UI-Based)

```bash
poe chatbot_crewai
# or
panel serve examples/chatbot_crewai/main.py
```

You’ll see output like this:

```
Poe => panel serve examples/chatbot_crewai/main.py
2025-05-21 14:54:21,472 Starting Bokeh server version 3.7.2 (running on Tornado 6.4.2)
2025-05-21 14:54:21,473 User authentication hooks NOT provided (default user enabled)
2025-05-21 14:54:21,476 Bokeh app running at: http://localhost:5006/main
2025-05-21 14:54:21,476 Starting Bokeh server with process id: 22032
```

Then open [http://localhost:5006/main](http://localhost:5006/main) in your browser to start chatting with the AI agents via a user-friendly interface.


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
