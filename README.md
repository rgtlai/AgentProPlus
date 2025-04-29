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
- 🧠 Powered by OpenAI (GPT-4, GPT-3.5) via API

## Quick Start

### Installation

Clone the repository and install the required packages:

```bash
git clone https://github.com/traversaal-ai/AgentPro.git
cd AgentPro
pip install -r requirements.txt
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
from agentpro import AgentPro, DuckDuckGoTool

openai_api_key = os.getenv("OPENAI_API_KEY", None) # Make sure OpenAI key is set

# Initialize tools
tools = [DuckDuckGoTool()]

# Initialize agent
agent = AgentPro(model=openai_api_key, tools=tools)

# Run a query
query = "Search the latest advancements in artificial intelligence"
response = agent.run(query)

print(response.final_answer)

```
You can also use the [Quick Start](https://github.com/traversaal-ai/AgentPro/blob/main/agentpro/examples/quick_start.ipynb) Jupyter Notebook to run AgentPro directly in Colab.

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

<!--
## Data Science Agent
https://github.com/user-attachments/assets/aeeb91e4-134e-4a14-bbc4-2523ba236c56


## Tools Overview
The AgentPro toolkit comes with a variety of default tasks, such as:

- **Internet Research**: "What are the latest developments in quantum computing?"
- **Code Generation**: "Create a Python script to analyze stock prices and generate a chart"
- **YouTube Analysis**: "Find and summarize recent videos about machine learning"
- **Presentation Creation**: "Make a presentation about renewable energy sources"

### AresInternetTool

Searches the internet for real-time information using the Traversaal Ares API.

```python
ares_tool = AresInternetTool()
result = ares_tool.run("recent advances in AI")
```

### CodeEngine

Generates and executes Python code based on natural language descriptions.

```python
code_tool = CodeEngine()
result = code_tool.run("create a bar chart comparing FAANG stocks")
```

### YouTubeSearchTool

Searches for YouTube videos, extracts transcripts, and summarizes content.

```python
youtube_tool = YouTubeSearchTool()
result = youtube_tool.run("machine learning tutorials")
```

### SlideGenerationTool

Creates PowerPoint presentations from structured content.

```python
slide_tool = SlideGenerationTool()
slides = [
    {"slide_title": "Introduction", "content": "Overview of the topic"},
    {"slide_title": "Key Points", "content": "The main arguments and findings"}
]
result = slide_tool.run(slides)
```

### DataAnalysisTool

Analyzes data files and provides statistical insights, visualizations, and exploratory data analysis.

```python
data_tool = DataAnalysisTool()

# Basic usage with a file path
result = data_tool.run("path/to/data.csv")

# With specific analysis parameters
analysis_params = {
    "file_path": "path/to/data.csv",
    "analysis_type": "visualization",
    "viz_type": "correlation",
    "columns": ["age", "income", "education"]
}
result = data_tool.run(analysis_params)
```
-->
## 🛠️ Creating Custom Tools

You can create your own tools by extending the `Tool` base class provided in `agentpro`.

Here’s a basic example:

```python
from agentpro import Tool
from typing import Any

class MyCustomTool(Tool):
    name: str = "My Custom Tool"
    description: str = "Description of what your custom tool does."
    action_type: str = "my_custom_action"
    input_format: str = "Description of expected input format, e.g., a string query."

    def run(self, input: Any) -> str:
        # Your tool logic here
        return "Result of running your custom tool."
```

After creating your custom tool, you can initialize it and pass it to AgentPro like this:

```python
import os
from agentpro import AgentPro

# Instantiate your custom tools
tools = [MyCustomTool()]

# Create AgentPro agent
myagent = AgentPro(model=os.getenv("OPENAI_API_KEY", None),tools=tools)

# Run a query
query = "Use the custom tool to perform a task."
response = myagent.run(query)

print(response.final_answer)
```

## Project Structure
agentpro/ ├── init.py ├── tools.py # Tool definitions (search, calculator, user input, ares internet search) ├── agent.py # Action, Observation, ThoughtStep, AgentResponse classes ├── react_agent.py # Core AgentPro class implementing the agent loop main.py # Example entrypoint to run the agent requirements.txt # Python dependencies README.md # Project description

```
agentpro/
├── agentpro/
│   ├── __init__.py
│   ├── react_agent.py                  # Core AgentPro class implementing react-style agent framework
│   ├── tools.py                        # Tool definitions (search, calculator, user input, ares internet search)
│   ├── agent.py                        # Action, Observation, ThoughtStep, AgentResponse classes
│   └── examples/
│       ├── quick_start.ipynb
│       └── custool_tool_integration.ipynb        
├── main.py                             # Entrypoint to run the agent
├── requirements.txt                    # Dependencies
├── README.md                           # Project overview, usage instructions, and documentation
└── LICENSE.txt                         # Open-source license information (Apache License 2.0)
```

## Requirements

- Python 3.8+
- OpenAI API key
- Traversaal Ares API key (for internet search)

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for more details.
