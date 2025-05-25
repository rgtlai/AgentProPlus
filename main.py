import os
import argparse
from agentpro import ReactAgent
from agentpro.tools import QuickInternetTool, CalculateTool, UserInputTool, AresInternetTool, YFinanceTool, TraversaalProRAGTool, SlideGenerationTool
from agentpro import create_model

def main():
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Run AgentPro with a query')
        parser.add_argument('input_text', type=str, help='The query to process')
        parser.add_argument('--system_prompt', type=str, help='Custom system prompt for the agent', default=None)
        args = parser.parse_args()

        # Create a model with LiteLLM
        litellm_model = create_model(
            provider="litellm",
            model_name="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY", None),
            litellm_provider="openai",
            temperature=0.7,
            max_tokens=2048
        )
        
        # Instantiate your tools
        tools = [
            QuickInternetTool(),
            CalculateTool(),
            UserInputTool(),
            YFinanceTool(),
            SlideGenerationTool(),
            AresInternetTool(api_key=os.getenv("ARES_API_KEY", None)),
            # TraversaalProRAGTool(api_key=os.getenv("TRAVERSAAL_PRO_API_KEY", None), document_names="employee_safety_manual"),
        ]
        myagent = ReactAgent(model=litellm_model, tools=tools, custom_system_prompt=args.system_prompt, max_iterations=20)
        
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
