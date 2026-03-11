from base_agent import BaseAgent
from worker_agents import ResearcherAgent, DataAnalystAgent, SynthesisAgent

class Orchestrator(BaseAgent):
    """The central manager that coordinates the agent hierarchy."""

    def __init__(self, name: str):
        super().__init__(name, role="Manager")
        self.researcher = ResearcherAgent("Agent-R", "Researcher")
        self.data_analyst = DataAnalystAgent("Agent-D", "Data Analyst")
        self.synthesis_agent = SynthesisAgent("Agent-S", "Synthesis")

    def execute_task(self, task: dict) -> dict:
        self.log(f"Received high-level goal: {task['content']}")

        # Step 1: Research Phase
        self.log("Phase 1: Starting Research gathering...")
        research_result = self.researcher.execute_task({"content": task['content']})
        theory_foundation = research_result["theory_output"]

        # Step 2: Data Validation Phase
        self.log("Phase 2: Starting Data validation...")
        data_result = self.data_analyst.execute_task({"content": task['content']})
        data_validation = data_result["data_output"]

        # Step 3: Synthesis Phase
        self.log("Phase 3: Starting Product Synthesis...")
        synthesis_input = {
            "content": task['content'],
            "theory_input": theory_foundation,
            "data_input": data_validation
        }
        product_result = self.synthesis_agent.execute_task(synthesis_input)

        self.log("Hierarchy execution complete. Aggregating final product specification.")
        return {
            "final_product": product_result["product_output"],
            "status": "success"
        }
