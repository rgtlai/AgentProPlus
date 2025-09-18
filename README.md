# AgentPro

AgentPro is a lightweight ReAct-style agentic framework built in Python, designed for structured reasoning step-by-step using available tools, while maintaining a complete history of Thought → Action → Observation → PAUSE → Final Answer steps.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-Apache%202.0-blue" alt="License: Apache 2.0">
</p>

## 📚 Features

- 🔥 ReAct (Reasoning + Acting) agent pattern
- 🛠️ Modular tool system (easy to add your own tools)
- 📜 Clean Thought/Action/Observation/PAUSE parsing
- 📦 Local package structure for easy extension
- 🧠 Powered by any LLM! (Anthropic, Open AI or any other Open source LLMs)

## ♻️ Fork Enhancements

This fork extends the upstream AgentPro project with conversation-aware streaming:

- Persistent chat history inside `ReactAgent` so each request automatically includes recent user/assistant turns when prompting the LLM.
- `ReactAgent.run_stream` generator that emits structured events (prompt, streamed tokens, parsed steps, final answer, errors) for real-time UIs or CLIs.
- Streaming hooks on `ModelClient` so OpenAI and LiteLLM backends can surface incremental tokens without waiting for the full response.
- Graceful fallback to the original non-streaming flow when a provider does not expose streaming APIs.

## Quick Start

### Installation

Install agentpro repository using pip:

```bash
pip install git+https://github.com/traversaal-ai/AgentPro.git -q
```
<!--
### Configuration

Create a `.env` file in the root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key
TRAVERSAAL_ARES_API_KEY=your_traversaal_ares_api_key
```
Ares internet tool: Searches the internet for real-time information using the Traversaal Ares API. To get `TRAVERSAAL_ARES_API_KEY`. Follow these steps:

1. Go to the [Traversaal API platform](https://api.traversaal.ai/)
2. Log in or create an account
3. Click **"Create new secret key"**
4. Copy the generated key and paste in `.env` file :

### Running the Agent

From the command line:

```bash
python main.py
```

This starts an interactive session with the agent where you can enter queries. -->

### Basic Usage
```python
import os
from agentpro import ReactAgent
from agentpro.tools import AresInternetTool
from agentpro import create_model

# Create a model with OpenAI
model = create_model(provider="openai", model_name="gpt-4o", api_key=os.getenv("OPENAI_API_KEY", None))

# Initialize tools
tools = [AresInternetTool(os.getenv("ARES_API_KEY", None))]

# Initialize agent
agent = ReactAgent(model=model, tools=tools)

# Run a query
query = "What is the height of the Eiffel Tower?"
response = agent.run(query)

print(f"\nFinal Answer: {response.final_answer}")
```
For Ares api key, follow these steps:

1. Go to the [Traversaal API platform](https://api.traversaal.ai/)
2. Log in or create an account
3. Generate your Ares API key from the dashboard.

### Streaming Usage

Use `run_stream` to react to events as they arrive. Each yielded dict includes a `type` key so you can branch on prompts, incremental tokens, structured thought steps, or the final answer.

```python
import os
from agentpro import ReactAgent, create_model
from agentpro.tools import AresInternetTool

model = create_model(provider="openai", model_name="gpt-4o", api_key=os.environ.get("OPENAI_API_KEY"))
tools = [AresInternetTool(os.getenv("ARES_API_KEY", None))]

# Initialize agent
agent = ReactAgent(model=model, tools=tools)

for event in agent.run_stream("Summarize the Apollo program in two sentences."):
    if event["type"] == "prompt":
        print("\n--- Sending prompt ---\n")
    elif event["type"] == "llm_token":
        print(event["token"], end="", flush=True)
    elif event["type"] == "final_answer":
        print(f"\n\nFinal Answer: {event['final_answer']}")
    elif event["type"] == "error":
        print(f"\nEncountered error: {event['error']}")
```

Event stream basics:

- `prompt`: The compiled system/user prompt with history.
- `llm_token`: Incremental content from providers that support streaming.
- `llm_response`: The concatenated response once streaming finishes or when falling back to non-streaming mode.
- `thought_step`: Parsed Thought/Action/Observation blocks the agent recorded.
- `final_answer`: The agent’s concluding reply.
- `error`: Formatting or tool-execution issues surfaced as observations.

## MCP Integration (Model Context Protocol)

This fork can auto‑discover and use tools from MCP servers. It keeps the ReAct loop unchanged — MCP tools are registered like any other Tool and listed in the system prompt, so the LLM can select them with a standard Action.

### Install and Run the Example Server

```bash
pip install mcp  # optional dependency
python mcp_server.py  # starts a stdio MCP server exposing echo and add
```

### Register MCP Tools in the Agent

Pass an `mcp_config` to `ReactAgent` to connect and enumerate tools at startup:

```python
import os
from agentpro import ReactAgent, create_model
from agentpro.tools import AresInternetTool

model = create_model(provider="openai", model_name="gpt-4o", api_key=os.environ.get("OPENAI_API_KEY"))

tools = [AresInternetTool(os.getenv("ARES_API_KEY", None))]

agent = ReactAgent(
    model=model,
    tools=tools,
    mcp_config=[
        {"id": "example", "command": "python", "args": ["mcp_server.py"]}
    ],
)

response = agent.run("Use the MCP add tool to add 2 and 3, then echo the result.")
print("Final:", response.final_answer)
```

What gets registered:

- For each MCP tool, the agent creates an internal Tool with action type `mcp:<server_id>:<tool_name>` and description/schema hints.
- The tool appears in the system prompt’s tool list so the LLM can select it with an Action JSON like:

```
Action: {"action_type": "mcp:example:add", "input": {"a": 2, "b": 3}}
```

Notes:

- MCP is optional. If the `mcp` package is not installed or a server fails to start, the agent continues without MCP tools.
- Inputs should be valid JSON matching the MCP tool schema; results are returned as text when possible.
- This repo includes a minimal `mcp_server.py` you can extend with your own tools.

<!--
You can also use the [Quick Start](https://github.com/traversaal-ai/AgentPro/blob/main/cookbook/quick_start.ipynb) Jupyter Notebook to run AgentPro directly in Colab.
-->
## 🌍 Traversaal x Optimized AI Hackathon 2025

We’re teaming up with the **Optimized AI Conference 2025** to host a **global hackathon on AI Agents** — open to all developers, builders, researchers, and dreamers working on intelligent systems.

### The Challenge

**Build a real, functional AI Agent** that solves a real-world problem.

This isn’t about flashy demos. We want to see domain-specific, usable, vertical agents — like:
- 🧑‍💼 Customer Support Agents
- 🔬 Research Assistants
- 📊 Data Analyst Agents
- 💡 Or something totally original

You can use any framework, but we recommend trying **[AgentPro](https://github.com/traversaal-ai/AgentPro)** — our open-source toolkit designed for rapid prototyping and robust architecture.

### Key Dates

- **Hackathon Starts:** April 9, 2025  
- **Submission Deadline:** April 15, 2025  
- **Winners Announced:** April 15, 2025 (Live @ Optimized AI Conference)

### Prizes + Recognition

| Prize Tier         | Reward     |
|--------------------|------------|
| 🥇 Grand Prize      | $1,000     |
| 🥈 Runner-Up        | $500     |
| 🥉 Honorable Mention x2 | $250       |

Plus:
- 1:1 **Mentorship opportunities**
- Invitation to **Traversaal’s AI Fellowship Program**

### Want to be a Judge?
We’re looking for global experts in AI, product, UX, and enterprise applications to help evaluate the submissions. 👉 [Apply to be a Judge](https://forms.gle/zpC4GbEjAkD1osY68)

For more details, follow this [link](https://hackathon.traversaal.ai/)

📩 Questions? Reach us at [hackathon-oai@traversaal.ai](hackathon-oai@traversaal.ai)

## 🛠️ Creating Custom Tools

You can create your own tools by extending the `Tool` base class provided in `agentpro`.

Here’s a basic example:

```python
from agentpro.tools import Tool
from typing import Any

class MyCustomTool(Tool):
    name: str = "My Custom Tool"  # Human-readable name for the tool (used in documentation and debugging)
    description: str = "Description"  # Brief summary explaining the tool's functionality for agent
    action_type: str = "my_custom_action"  # Unique identifier for the tool; lowercase with underscores for agent; avoid spaces, digits, special characters
    input_format: str = "Description of expected input format, e.g., a string query."  # Instruction on what kind of input the tool expects with example

    def run(self, input_text: Any) -> str:
        # your tool logic
        return "Result of your custom tool."

```

After creating your custom tool, you can initialize it and pass it to AgentPro like this:

```python
import os
from agentpro import ReactAgent
from agentpro import create_model

# Create a model with OpenAI
model = create_model(provider="openai", model_name="gpt-4o", api_key=os.getenv("OPENAI_API_KEY", None))

# Instantiate your custom tools
tools = [MyCustomTool()]

# Create AgentPro React agent
myagent = ReactAgent(model=model,tools=tools)

# Run a query
query = "Use the custom tool to perform a task."
response = myagent.run(query)

print(response.final_answer)
```

## Project Structure

```
AgentPro/
├── agentpro/
│   ├── __init__.py
│   ├── react_agent.py                  # Core AgentPro class implementing react-style agent framework
│   ├── agent.py                        # Action, Observation, ThoughtStep, AgentResponse classes
│   ├── model.py                        # Model classes 
│   ├── tools/                          # folder for all tool classes
│       ├── __init__.py
│       ├── base_tool.py
│       ├── duckduckgo_tool.py
│       ├── calculator_tool.py
│       ├── userinput_tool.py
│       ├── ares_tool.py
│       ├── traversaalpro_rag_tool.py
│       ├── slide_generation_tool.py
│       └── yfinance_tool.py
├── cookbook/
│   ├── Traversaal x Optimized AI Hackathon 2025
│   ├── quick_start.ipynb
│   └── custool_tool.ipynb      
├── main.py                             # Entrypoint to run the agent
├── requirements.txt                    # Dependencies
├── README.md                           # Project overview, usage instructions, and documentation
├── setup.py       
├── pyproject.toml     
└── LICENSE.txt                         # Open-source license information (Apache License 2.0)
```

## Requirements

- Python 3.8+
- OpenAI API key
- Traversaal Ares API key for internet search (Optional)

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for more details.
