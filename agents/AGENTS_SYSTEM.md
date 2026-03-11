# Hierarchical AI Agent System Architecture

## Overview
The system follows a tiered structure where an **Orchestrator** manages specialized worker agents to transform theoretical concepts and raw data into a validated product outline.

## Agent Roles

### 1. Orchestrator (The Manager)
- **Objective**: Translate high-level prompts into actionable sub-tasks.
- **Workflow**:
    1. Receive Goal.
    2. Decompose into `Research`, `Data Validation`, and `Synthesis` phases.
    3. Delegate to worker agents.
    4. Aggregate results into a final Product Specification.

### 2. Researcher Agent (Foundational Intelligence)
- **Objective**: Gather theoretical frameworks and market context.
- **Focus Areas**:
    - Academic research (theories).
    - Market trends (news & insights).
- **Output**: Theoretical Foundation Document.

### 3. Data Analyst Agent (Verification Intelligence)
- **Objective**: Validate research findings with quantitative evidence.
- **Focus Areas**:
    - Statistical datasets.
    - Historical performance data.
- **Output**: Data Validation Report.

### 4. Synthesis Agent (Creative Intelligence)
- **Objective**: Convert findings and data into a user-facing product prototype.
- **Focus Areas**:
    - Product documentation.
    - Asset generation (placeholders for images/UI).
- **Output**: Product Blueprint.

## Communication Protocol
Agents communicate via a JSON-based task-response format. Each worker agent reports status and results back to the Orchestrator.

## File Structure (Planned)
- `base_agent.py`: Abstract base class for agents.
- `worker_agents.py`: Implementations of Researcher, Data Analyst, and Synthesis agents.
- `orchestrator.py`: Implementation of the Manager agent.
- `build_hierarchy_demo.py`: Main entry point for the demo.
