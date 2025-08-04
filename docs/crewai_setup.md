# Using TigerGraph-MCP Tools with CrewAI

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

## 4. Run the chatbot using CrewAI

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

