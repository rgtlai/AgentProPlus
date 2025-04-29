import os
from agentpro import AgentPro
from agentpro.tools import DuckDuckGoTool, CalculateTool, UserInputTool, AresInternetTool, YFinanceTool


def main():
    try:
        # Instantiate your tools
        tools = [
            DuckDuckGoTool(),
            CalculateTool(),
            UserInputTool(),
            AresInternetTool(api_key=os.getenv("ARES_API_KEY", None)),
            YFinanceTool()
        ]
        myagent = AgentPro(model=os.getenv("OPENAI_API_KEY", None), tools=tools, max_iterations=20)
        
        query = input("Enter your Query : ")
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

