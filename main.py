import os
import argparse
from agentpro import AgentPro
from agentpro.tools import DuckDuckGoTool, CalculateTool, UserInputTool, AresInternetTool, YFinanceTool, TraversaalProRAGTool


def main():
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Run AgentPro with a query')
        parser.add_argument('input_text', type=str, help='The query to process')
        args = parser.parse_args()
        
        # Instantiate your tools
        tools = [
            DuckDuckGoTool(),
            CalculateTool(),
            UserInputTool(),
            YFinanceTool(),
            AresInternetTool(api_key=os.getenv("ARES_API_KEY", None)),
            TraversaalProRAGTool(api_key=os.getenv("TRAVERSAAL_PRO_API_KEY", None), document_names="employee_safety_manual")
        ]
        myagent = AgentPro(model=os.getenv("OPENAI_API_KEY", None), tools=tools, max_iterations=20)
        
        query = args.input_text
        response = myagent.run(query)

        print("=" * 50 + " FINAL Thought Process:")
        for step in response.thought_process:
            if step.pause_reflection:
                print(f"✅ Pause: {step.pause_reflection}")
            if step.thought:
                print(f"✅ Thought: {step.thought}")
            if step.action:
                print(f"✅ Action: {step.action.model_dump_json()}")
            if step.observation:
                print(f"✅ Observation: {step.observation.result}")
        
        print(f"\n✅ Final Answer: {response.final_answer}")
    
    except Exception as e:
        print(f"Error running agent: {e}")

if __name__ == "__main__":
    main()
