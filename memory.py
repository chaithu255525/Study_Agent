"""
Memory Module for SmartStudy Agent

Provides session memory storage to persist tasks, deadlines, user preferences,
and multi-turn conversation history across agent executions.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class StudyAgentMemory:
    """
    In-memory storage for the SmartStudy Agent.
    Stores:
    - tasks: List of task records with name, due date, urgency metadata
    - preferences: Dict of user study preferences
    - conversation_history: List of conversation messages across turns
    """

    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []
        self.preferences: Dict[str, Any] = {
            "default_block_hours": 2,
            "max_daily_study_hours": 6
        }
        self.conversation_history: List[Dict[str, str]] = []

    def add_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds a new task or updates an existing task if name matches.
        """
        # Check if task already exists (case-insensitive)
        existing_index = None
        for i, t in enumerate(self.tasks):
            if t["name"].strip().lower() == task["name"].strip().lower():
                existing_index = i
                break

        if existing_index is not None:
            self.tasks[existing_index].update(task)
            return self.tasks[existing_index]
        else:
            self.tasks.append(task)
            return task

    def get_tasks(self) -> List[Dict[str, Any]]:
        """Returns all stored tasks."""
        return self.tasks

    def get_task_names(self) -> List[str]:
        """Returns a list of all stored task names."""
        return [t["name"] for t in self.tasks]

    def add_message(self, role: str, content: str):
        """Appends a message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Returns full conversation history."""
        return self.conversation_history

    def clear(self):
        """Clears all stored memory."""
        self.tasks.clear()
        self.conversation_history.clear()

    def get_memory_summary(self) -> str:
        """
        Returns a readable string summary of current memory state
        for inclusion in system prompts and trace logging.
        """
        if not self.tasks:
            return "No tasks currently stored in memory."
        
        lines = [f"Total Tasks: {len(self.tasks)}"]
        for idx, task in enumerate(self.tasks, 1):
            days_left = task.get("days_left", "N/A")
            lines.append(f"  {idx}. {task['name']} (Due: {task['due']}, Days Left: {days_left})")
        return "\n".join(lines)
