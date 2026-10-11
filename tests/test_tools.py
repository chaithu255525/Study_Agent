"""
Unit Tests for SmartStudy Agent

Tests tool validation, scheduling logic, memory persistence,
and edge/failure cases required by CA1 evaluation criteria.
Uses Python's built-in unittest framework so no external test runner is required.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import StudyAgentMemory
from tools import add_task, build_schedule
from agent import SmartStudyAgent


class TestSmartStudyTools(unittest.TestCase):

    def test_add_task_success(self):
        """1. Test that add_task successfully validates and adds a valid task."""
        mem = StudyAgentMemory()
        res = add_task("Python Assignment", "2026-08-26", mem)

        self.assertTrue(res["success"])
        self.assertIn("successfully added", res["message"])
        self.assertEqual(res["task"]["name"], "Python Assignment")
        self.assertEqual(res["task"]["due"], "2026-08-26")
        self.assertEqual(len(mem.get_tasks()), 1)

    def test_add_task_invalid_date(self):
        """2. Test that an invalid date format is rejected gracefully."""
        mem = StudyAgentMemory()
        res = add_task("Physics Quiz", "invalid-date-xyz", mem)

        self.assertFalse(res["success"])
        self.assertIn("Invalid date format", res["message"])
        self.assertEqual(len(mem.get_tasks()), 0)

    def test_add_task_empty_name(self):
        """3. Test that empty or whitespace task names are rejected."""
        mem = StudyAgentMemory()
        res = add_task("   ", "2026-08-30", mem)

        self.assertFalse(res["success"])
        self.assertIn("Task name cannot be empty", res["message"])
        self.assertEqual(len(mem.get_tasks()), 0)

    def test_build_schedule_with_tasks(self):
        """4. Test build_schedule prioritizes tasks correctly when tasks exist."""
        mem = StudyAgentMemory()
        add_task("Python Assignment", "2026-08-26", mem)  # Due in 1 day (HIGH)
        add_task("DBMS Exam", "2026-08-30", mem)          # Due in 5 days (MEDIUM)
        add_task("AI Project", "2026-09-10", mem)         # Due in 16 days (LOWER)

        res = build_schedule(mem)

        self.assertTrue(res["success"])
        self.assertEqual(res["total_tasks"], 3)
        self.assertIn("Python Assignment", res["priorities"]["high"])
        self.assertIn("DBMS Exam", res["priorities"]["medium"])
        self.assertIn("AI Project", res["priorities"]["lower"])
        self.assertEqual(len(res["study_blocks"]), 3)

    def test_build_schedule_no_tasks_failure(self):
        """5. Test build_schedule handles empty task list gracefully (Honest Failure Case)."""
        mem = StudyAgentMemory()
        res = build_schedule(mem)

        self.assertFalse(res["success"])
        self.assertIn("no tasks stored in memory", res["message"])
        self.assertIsNone(res["schedule"])

    def test_memory_persistence(self):
        """6. Test memory persists tasks across multiple calls."""
        mem = StudyAgentMemory()

        # Turn 1
        add_task("Turn 1 Task", "2026-08-27", mem)
        self.assertEqual(len(mem.get_tasks()), 1)

        # Turn 2
        add_task("Turn 2 Task", "2026-08-29", mem)
        self.assertEqual(len(mem.get_tasks()), 2)
        self.assertEqual(mem.get_task_names(), ["Turn 1 Task", "Turn 2 Task"])

    def test_replanning_with_new_urgent_task(self):
        """7. Test Group of 3 Add-on: Re-planning when a new urgent task arrives."""
        mem = StudyAgentMemory()
        # Initial state: Only DBMS exam due in 5 days (Medium priority)
        add_task("DBMS Exam", "2026-08-30", mem)
        initial_sched = build_schedule(mem)
        self.assertEqual(initial_sched["priorities"]["high"], [])
        self.assertEqual(initial_sched["priorities"]["medium"], ["DBMS Exam"])

        # New urgent task arrives: Python Assignment due in 1 day (High priority)
        add_task("Python Assignment", "2026-08-26", mem)
        replanned_sched = build_schedule(mem)

        # Dynamic replanning: Python Assignment prioritized ahead of DBMS Exam
        self.assertEqual(replanned_sched["priorities"]["high"], ["Python Assignment"])
        self.assertEqual(replanned_sched["priorities"]["medium"], ["DBMS Exam"])
        self.assertEqual(replanned_sched["study_blocks"][0]["task_name"], "Python Assignment")
        self.assertEqual(replanned_sched["study_blocks"][0]["recommended_daily_hours"], 3.0)
        self.assertEqual(replanned_sched["study_blocks"][1]["task_name"], "DBMS Exam")


if __name__ == "__main__":
    unittest.main()
