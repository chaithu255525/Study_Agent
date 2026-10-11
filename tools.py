"""
Tools Module for SmartStudy Agent

Defines the two concrete Python tool functions:
1. add_task(name, due, memory)
2. build_schedule(memory)

Also provides OpenAI-compatible function calling schemas for LLM tool integration.
"""

from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta
from config import TODAY_DATE
from memory import StudyAgentMemory


def parse_date(date_str: str, reference_date_str: str = TODAY_DATE) -> Optional[date]:
    """
    Parses ISO date string (YYYY-MM-DD) or relative date strings
    (e.g., 'tomorrow', 'in 5 days', 'today') relative to reference_date_str.
    Returns datetime.date object or None if invalid.
    """
    if not date_str or not isinstance(date_str, str):
        return None

    cleaned_str = date_str.strip().lower()
    
    try:
        ref_date = date.fromisoformat(reference_date_str)
    except ValueError:
        ref_date = date.today()

    # Handle ISO YYYY-MM-DD format
    try:
        return date.fromisoformat(cleaned_str)
    except ValueError:
        pass

    # Handle relative date strings
    if cleaned_str == "today":
        return ref_date
    elif cleaned_str == "tomorrow":
        return ref_date + timedelta(days=1)
    
    # Extract number of days from strings like 'in 3 days', '3 days', '3 days from now'
    if "day" in cleaned_str:
        words = cleaned_str.split()
        for w in words:
            if w.isdigit():
                return ref_date + timedelta(days=int(w))

    return None


def add_task(name: str, due: str, memory: StudyAgentMemory) -> Dict[str, Any]:
    """
    Tool 1: Adds a task to session memory after performing validation.

    Validation Rules:
    - Task name must be a non-empty string.
    - Due date must be valid YYYY-MM-DD or relative date string.
    - Due date must not be in the past relative to TODAY_DATE.

    Args:
        name: Name of the assignment or exam.
        due: Deadline date (e.g. '2026-08-26', 'tomorrow', 'in 5 days').
        memory: StudyAgentMemory instance.

    Returns:
        Structured result dictionary.
    """
    # 1. Validate task name
    if not name or not isinstance(name, str) or not name.strip():
        return {
            "success": False,
            "message": "Error: Task name cannot be empty.",
            "task": None
        }
    
    clean_name = name.strip()

    # 2. Validate due date format
    parsed_due = parse_date(due, TODAY_DATE)
    if parsed_due is None:
        return {
            "success": False,
            "message": f"Error: Invalid date format '{due}'. Please provide date as YYYY-MM-DD (e.g., '2026-08-26').",
            "task": None
        }

    ref_date = date.fromisoformat(TODAY_DATE)
    days_left = (parsed_due - ref_date).days

    # 3. Check for past deadline
    if days_left < 0:
        return {
            "success": False,
            "message": f"Error: Due date '{parsed_due.isoformat()}' has already passed.",
            "task": None
        }

    # 4. Create structured task record
    task_record = {
        "name": clean_name,
        "due": parsed_due.isoformat(),
        "days_left": days_left
    }

    # 5. Store in memory
    memory.add_task(task_record)

    return {
        "success": True,
        "message": f"Task '{clean_name}' successfully added to memory (due {parsed_due.isoformat()}, {days_left} days left).",
        "task": task_record
    }


def build_schedule(memory: StudyAgentMemory) -> Dict[str, Any]:
    """
    Tool 2: Generates a prioritized study schedule from memory tasks.

    Logic:
    1. Reads tasks from memory.
    2. If no tasks, returns failure result (Honest Edge Case).
    3. Categorizes tasks by urgency based on days_left:
       - HIGH PRIORITY: <= 2 days
       - MEDIUM PRIORITY: 3 to 5 days
       - LOWER PRIORITY: > 5 days
    4. Generates structured study blocks.

    Args:
        memory: StudyAgentMemory instance.

    Returns:
        Structured schedule dictionary.
    """
    tasks = memory.get_tasks()

    # Handle empty task list failure case
    if not tasks:
        return {
            "success": False,
            "message": "Cannot build schedule: There are currently no tasks stored in memory. Please add tasks first using add_task().",
            "schedule": None
        }

    ref_date = date.fromisoformat(TODAY_DATE)

    # Recalculate days left relative to current reference date
    updated_tasks = []
    for t in tasks:
        parsed_due = parse_date(t["due"], TODAY_DATE)
        days = (parsed_due - ref_date).days if parsed_due else t.get("days_left", 0)
        t_copy = dict(t)
        t_copy["days_left"] = max(0, days)
        updated_tasks.append(t_copy)

    # Sort tasks by deadline (nearest first)
    sorted_tasks = sorted(updated_tasks, key=lambda x: x["days_left"])

    high_priority = []
    medium_priority = []
    lower_priority = []

    study_blocks = []

    for task in sorted_tasks:
        days = task["days_left"]
        name = task["name"]
        due = task["due"]

        if days <= 2:
            priority = "HIGH PRIORITY"
            hours_per_day = 3.0
            high_priority.append(task)
        elif days <= 5:
            priority = "MEDIUM PRIORITY"
            hours_per_day = 2.0
            medium_priority.append(task)
        else:
            priority = "LOWER PRIORITY"
            hours_per_day = 1.0
            lower_priority.append(task)

        study_blocks.append({
            "task_name": name,
            "due_date": due,
            "days_left": days,
            "priority": priority,
            "recommended_daily_hours": hours_per_day,
            "focus_area": f"Core concepts and practice for {name}"
        })

    schedule_data = {
        "success": True,
        "total_tasks": len(sorted_tasks),
        "priorities": {
            "high": [t["name"] for t in high_priority],
            "medium": [t["name"] for t in medium_priority],
            "lower": [t["name"] for t in lower_priority]
        },
        "study_blocks": study_blocks,
        "message": f"Successfully generated schedule for {len(sorted_tasks)} task(s)."
    }

    return schedule_data


# OpenAI Function Calling Schemas for LLM Tool Binding
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Adds an academic task or exam with its due date to the student's memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the task or exam (e.g. 'Python Assignment', 'DBMS Exam')."
                    },
                    "due": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format or relative date ('tomorrow', 'in 5 days')."
                    }
                },
                "required": ["name", "due"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "build_schedule",
            "description": "Generates a prioritized study schedule based on tasks currently stored in memory.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]
