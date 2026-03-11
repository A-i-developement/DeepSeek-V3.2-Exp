from orchestrator import Orchestrator

def main():
    print("--- Starting Hierarchical AI Agent System Build Demo ---")

    # 1. Initialize the Orchestrator (The Manager)
    manager = Orchestrator("Master-Orchestrator")

    # 2. Define the product goal
    goal = "An AI-powered Renewable Energy Optimizer"
    print(f"\n[USER INPUT]: Create a product outline for: {goal}\n")

    # 3. Execute the hierarchical system
    result = manager.execute_task({"content": goal})

    # 4. Show the final output
    print("\n--- Final Product Output ---")
    print(result["final_product"])
    print("\n--- Build Complete ---")

if __name__ == "__main__":
    main()
