# Using TigerGraph-MCP Tools with LangGraph

## 1. Clone this repository and install the package with development dependencies.

## 2. Activate your virtual environment.

## 3. Set up the `.env` file

In the root of your project, create a `.env` file with the following content:

```
OPENAI_API_KEY=<YOUR OPENAI KEY>
TG_HOST=http://127.0.0.1
TG_USERNAME=tigergraph
TG_PASSWORD=tigergraph
```

> Replace `<YOUR OPENAI KEY>` with your actual OpenAI API key.
> This configuration assumes you're running TigerGraph locally and logging in with a username and password. See the [Alternative Connection Setup Methods](https://tigergraph-devlabs.github.io/tigergraph-mcp-utils/reference/01_core/graph/#tigergraphx.core.graph.Graph.__init__) for additional ways to connect to TigerGraph.

## 4. Run the chatbot using LangGraph

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

## 5. Examples of Using the Chatbot with LangGraph

### 5.1 Onboarding
This example demonstrates how to use the onboarding feature. Onboarding is helpful when you're using the chatbot for the first time or are unfamiliar with TigerGraph. It guides you through creating a schema, loading data, and running basic algorithms. The example also includes simple instructions such as checking the number of nodes and edges in the graph, as well as dropping the graph schema and data source—which require user confirmation.

See: [`docs/chatbot_langgraph_examples/onboarding.txt`](./docs/chatbot_langgraph_examples/onboarding.txt)

### 5.2 Load data from S3 files
This example demonstrates how to create graph and load data if you have S3 file.  It walks through the full workflow—from creating a data source and previewing files, to generating a graph schema, and loading data. Similar to Onboarding example, it also includes simple instructions such as checking the number of nodes and edges in the graph, as well as dropping the graph schema and data source—which require user confirmation, also how to show everything in the db.

See: [`docs/chatbot_langgraph_examples/load_data_s3.txt`](./docs/chatbot_langgraph_examples/load_data_s3.txt)

### 5.3 Load data from local files
This example demonstrates how to create a graph and load data using local files. It guides you through the full workflow—from providing sample data for schema creation, data loading from local CSV files, and performing basic queries such as checking node and edge counts. It also shows how to safely drop the graph with user confirmation and verify the database state afterward.

See: [`docs/chatbot_langgraph_examples/load_data_local.txt`](./docs/chatbot_langgraph_examples/load_data_local.txt)

