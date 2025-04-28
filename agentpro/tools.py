from typing import Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel
import math
import requests
import json
import os

# Try importing DuckDuckGo Search
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    print("Warning: duckduckgo-search not installed. Using mock search instead.")

# Base Tool class
class Tool(ABC, BaseModel):
    name: str
    description: str
    action_type: str
    input_format: str  # <<< NEW FIELD

    @abstractmethod
    def run(self, input: Any) -> str:
        pass

    def get_tool_description(self) -> str:
        return (
            f"Tool: {self.name}\n"
            f"Description: {self.description}\n"
            f"Action Type: {self.action_type}\n"
            f"Input Format: {self.input_format}\n"
        )

# DuckDuckGo search tool
class DuckDuckGoTool(Tool):
    name: str = "DuckDuckGo Search"
    description: str = "Searches internet using DuckDuckGo for a given query and returns top 5 results."
    action_type: str = "search"
    input_format: str = "A search query as a string. Example: 'Latest advancements in AI'"

    ddg: Optional[Any] = None  # Important: Declare ddg properly for Pydantic

    def __init__(self, **data):
        super().__init__(**data)
        # Set ddg safely even with BaseModel
        object.__setattr__(self, 'ddg', DDGS() if DDGS_AVAILABLE else None)

    def run(self, input: Any) -> str:
        query = input
        if not self.ddg:
            return f"Mock search results for: {query}\n1. Sample Result\n2. Another Result"

        try:
            results = list(self.ddg.text(query, max_results=5))
            if not results:
                return "No results found."
            return "\n".join(
                f"{i+1}. {r['title']}\n   {r['body']}" for i, r in enumerate(results)
            )
        except Exception as e:
            return f"Error performing search: {str(e)}"

# Calculator tool
class CalculateTool(Tool):
    name: str = "Calculator"
    description: str = "Evaluates a basic math expression and returns the result."
    action_type: str = "calculate"
    input_format: str = "A math expression as a string. Example: '2 + 3 * (5 - 1)'"

    def run(self, input: Any) -> str:
        expr = input
        try:
            # Allow only safe characters
            safe_expr = ''.join(c for c in expr if c in '0123456789+-*/(). ')
            result = eval(safe_expr)
            return str(result)
        except Exception:
            return "Error: Invalid calculation."


class UserInputTool(Tool):
    name: str = "User Input Requester"
    description: str = "Requests more information from the user to continue solving the task."
    action_type: str = "request_user_input"
    input_format: str = "A string that defines the prompt/question to ask the user. Example: 'Please provide more details about your project goals.'"

    def run(self, prompt_text: Any) -> str:  # <<< Change 'input' to 'prompt_text'
        if not isinstance(prompt_text, str):
            return "Error: Expected a prompt string to request user input."
        
        # Ask user for input properly
        user_response = input(f"\n🧠 AI assistant: {prompt_text}\n👤 User response: ")
        return user_response


class AresInternetTool(Tool):
    name: str = "Ares Internet Search"
    description: str = "Uses Ares API to search live information from the internet and returns a clean summary and related links."
    action_type: str = "ares_internet_search"
    input_format: str = "A search query as a string. Example: 'Best restaurants in San Francisco'"

    api_url: str = "https://api-ares.traversaal.ai/live/predict"
    api_key: str = os.getenv("ARES_API_KEY", None)

    def run(self, input: Any) -> str:
        if not isinstance(input, str):
            return "❌ Error: Expected a search query string."

        if not self.api_key:
            return "❌ Error: Ares API key is missing. Please set the ARES_API_KEY environment variable."

        prompt = input.strip("'\"")  # Clean up quotes if needed
        payload = {"query": [prompt]}
        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json"
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)

            if response.status_code != 200:
                return f"Error: Ares API returned {response.status_code} - {response.text}"

            result = response.json()

            response_text = result.get("data", {}).get("response_text", "").strip()
            web_urls = result.get("data", {}).get("web_url", [])

            if not response_text:
                return "No information found for this query. Please try a different search term."

            output = f"Search Summary:\n{response_text}\n\n"

            if web_urls:
                output += "Related Links:\n"
                for idx, url in enumerate(web_urls, 1):
                    output += f"{idx}. {url}\n"

            return output.strip()

        except requests.exceptions.RequestException as e:
            return f"Error: HTTP request failed - {e}"

        except Exception as e:
            return f"Error: Unexpected error - {e}"


