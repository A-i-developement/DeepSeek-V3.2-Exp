from abc import ABC, abstractmethod
import json

class BaseAgent(ABC):
    """Abstract base class for all AI agents in the hierarchical system."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    @abstractmethod
    def execute_task(self, task: dict) -> dict:
        """Process a task and return the result as a dictionary."""
        pass

    def log(self, message: str):
        """Standardized logging for agent actions."""
        print(f"[{self.name} - {self.role}]: {message}")

class Task:
    """Represents a discrete unit of work within the agent system."""

    def __init__(self, task_type: str, content: str, status: str = "pending"):
        self.task_type = task_type
        self.content = content
        self.status = status
        self.result = None

    def to_dict(self) -> dict:
        return {
            "type": self.task_type,
            "content": self.content,
            "status": self.status,
            "result": self.result
        }
