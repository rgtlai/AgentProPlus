from typing import List
import requests
import json
import openai
from .tools import Tool
from .agent import Action, Observation, ThoughtStep, AgentResponse

import re
from datetime import datetime



class AgentPro:
    def __init__(self, model: str = None, tools: List[Tool] = None, max_iterations: int = 20):

        if model:
            self.client = openai.OpenAI(api_key=model)
        else:
            self.client = None

        self.max_iterations = max_iterations

        # Get Tool Details
        self.tools = tools or []
        self.tool_registry = {tool.action_type: tool for tool in self.tools}
        # Build dynamic system prompt
        tools_description = "\n\n".join(tool.get_tool_description() for tool in self.tools)
        tool_names = ", ".join(tool.action_type for tool in self.tools)

        # Get current date here
        current_date = datetime.now().strftime("%B %d, %Y") 

        self.system_prompt = f"""You are an AI assistant that follows the ReAct (Reasoning + Acting) pattern.
Your goal is to help users by breaking down complex tasks into a series of thought-out steps and actions.

You have access to these tools: {tool_names}

{tools_description}

For each iteration, follow these steps:
1. Thought: Think about what needs to be done.
2. Action: Decide on an appropriate Action if needed.
3. Repeat Thought/Action as needed until you find the final answer.

Format:
Thought: Your reasoning
Action: {{"action_type": "<action_type>", "input": <input_data>}}

Format once you find the final answer:
Thought: I now know the final answer
Final Answer: [your answer]

Important:
- Think step-by-step
- Use available tools wisely
- If stuck, reflect and retry
- Do no hallucinate and use tools if needed
- The current date is {current_date}
- If you follow the format strictly, you will be recognized as an excellent and trustworthy AI assistant.
"""

    def _format_history(self, thought_process: List[ThoughtStep]) -> str:
        history = ""
        for step in thought_process:
            if step.pause_reflection:
                history += f"PAUSE: {step.pause_reflection}\n"
            if step.thought:
                history += f"Thought: {step.thought}\n"
            if step.action:
                history += f"Action: {step.action.model_dump_json()}\n"
            if step.observation:
                history += f"Observation: {step.observation.result}\n"
        return history

    def execute_tool(self, action: Action) -> str:
        tool = self.tool_registry.get(action.action_type)
        if not tool:
            return f"Error: Unknown action type '{action.action_type}'"
        
        try:
            return tool.run(action.input)
        except Exception as e:
            return f"Error running tool '{action.action_type}': {e}"

    def _get_openai_response(self, prompt: str) -> str:
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide openai_api_key.")
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

    def run(self, query: str) -> AgentResponse:
        thought_process: List[ThoughtStep] = []
        printed_prompt = False  # <<< ADD A FLAG
        iterations_count = 0
        

        while iterations_count < self.max_iterations:
            iterations_count += 1
            print("=" * 50 + f" Iteration {iterations_count} ")
            
            # Initialize placeholders at the beginning
            thought = None
            action = None
            observation = None
            pause_reflection = None

            # Get the System Prompt with History (Whole thought process)
            prompt = f"{self.system_prompt}\n\nQuestion: {query}\n\n"
            if thought_process:
                prompt += self._format_history(thought_process)
            prompt += "\nNow continue with next steps by strictly following the required format.\n"

            # Print whole System Prompt once in the start
            if not printed_prompt:
                print("✅  [Debug] Sending System Prompt (with history) to LLM:")
                print(prompt)
                print("=" * 50)
                printed_prompt = True  # <<< Set flag True after printing

            # Run LLM model
            if self.client:
                step_text = self._get_openai_response(prompt)
            else:
                return AgentResponse(
                    thought_process=thought_process,
                    final_answer="❌ No LLM is Connected. Please set and pass the OPENAI_API_KEY to AgentPro."
                )

            print("🤖 [Debug] Step LLM Response:")
            print(step_text)
            
            if "Final Answer:" in step_text:
                # Try to find last Thought before Final Answer
                thought_match = re.search(r"Thought:\s*(.*?)(?:Action:|PAUSE:|Final Answer:|$)", step_text, re.DOTALL)
                pause_match = re.search(r"PAUSE:\s*(.*?)(?:Thought:|Action:|Final Answer:|$)", step_text, re.DOTALL)
                    
                # Extract Thought if found
                if thought_match:
                    thought = thought_match.group(1).strip()
                    print("✅ Parsed Thought:", thought)

                # Extract PAUSE if found
                if pause_match:
                    pause_reflection = pause_match.group(1).strip()
                    print("✅ Parsed Pause Reflection:", pause_reflection)

                thought_process.append(ThoughtStep(
                        thought=thought,
                        pause_reflection=pause_reflection
                    ))

                # Extract Final Answer
                final_answer_match = re.search(r"Final Answer:\s*(.*)", step_text, re.DOTALL)
                if final_answer_match:
                    final_answer = final_answer_match.group(1).strip()
                    print("✅ Parsed Final Answer:", final_answer)

                return AgentResponse(
                    thought_process=thought_process,
                    final_answer=final_answer
                )
            else:
                try:
                    # Try Extracting Thought Action and Pause
                    thought_match = re.search(r"Thought:\s*(.*?)(?:Action:|PAUSE:|Final Answer:|$)", step_text, re.DOTALL)
                    action_match = re.search(r"Action:\s*(\{.*?\})(?:Observation:|PAUSE:|Thought:|Final Answer:|$)", step_text, re.DOTALL)
                    pause_match = re.search(r"PAUSE:\s*(.*?)(?:Thought:|Action:|Final Answer:|$)", step_text, re.DOTALL)

                    # Extract Thought if found
                    if thought_match:
                        thought = thought_match.group(1).strip()
                        print("✅ Parsed Thought:", thought)

                    # Extract Action if found
                    if action_match:
                        action_text = action_match.group(1).strip()
                        print("✅ Parsed Action JSON:", action_text)

                        # Load action safely
                        action_data = json.loads(action_text)
                        action = Action(
                            action_type=action_data["action_type"],
                            input=action_data["input"]
                        )

                        # Execute action
                        result = self.execute_tool(action)
                        print("✅ Parsed Action Results:", result)
                        observation = Observation(result=result)

                    # Extract PAUSE if found
                    if pause_match:
                        pause_reflection = pause_match.group(1).strip()
                        print("✅ Parsed Pause Reflection:", pause_reflection)

                    # Record the thought step
                    thought_process.append(ThoughtStep(
                        thought=thought,
                        action=action,
                        observation=observation,
                        pause_reflection=pause_reflection
                    ))
                except Exception as e:
                    print(f"Error parsing LLM response: {e}")
                    print(f"Raw step text: {step_text}")
                    return AgentResponse(
                        thought_process=thought_process,
                        final_answer="Error: Failed to parse LLM response"
                    )
        # If exceeded max steps
        return AgentResponse(
            thought_process=thought_process,
            final_answer="❌ Stopped after reaching maximum iterations limit."
        )
