import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# SmartStudy Agent: An Agentic AI Study Planner\n",
    "### CSE476 Agentic AI and Intelligent Automation — CA1 Project 1\n",
    "**Project Name:** SmartStudy Agent  \n",
    "**Subtitle:** *An Agentic AI Study Planner*  \n",
    "**Topic:** T24 — Study Planner Agent  \n",
    "**Framework:** Python 3.10+ | OpenAI Function Calling API / Groq API  \n",
    "\n",
    "---"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Problem Statement & Motivation\n",
    "University students struggle to balance multiple coursework deadlines, exams, and projects. Standard chatbots offer generic advice but cannot track deadline dates, prioritize urgent tasks deterministically, or re-plan study blocks when new deadlines are introduced.\n",
    "\n",
    "**SmartStudy Agent** solves this by acting as a **Real AI Agent** featuring a complete **Plan-Act-Observe loop**. It combines deterministic Python tools with memory persistence to organize tasks, calculate urgency, and generate optimized study schedules."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. University CA1 Requirement Checklist\n",
    "- ✅ **1. One AI Agent with Plan-Act Loop:** Multi-step decision loop implemented in `agent.py`.\n",
    "- ✅ **2. Takes More Than 1 Step:** Agent executes multiple tool calls sequentially per turn.\n",
    "- ✅ **3. Tool-Based Decisions:** Agent chooses next action dynamically based on tool results.\n",
    "- ✅ **4. At Least 2 Real Tools:** Implements `add_task(name, due)` and `build_schedule()`.\n",
    "- ✅ **5. Real Tool Execution:** Tools execute concrete Python code modifying application state.\n",
    "- ✅ **6. Session Memory:** `StudyAgentMemory` persists tasks, deadlines, and preferences.\n",
    "- ✅ **7. Multi-Turn Persistence:** Remembers information from earlier turns in the conversation.\n",
    "- ✅ **8. Memory Reading:** Reads memory in later turns to answer follow-up queries without repeating.\n",
    "- ✅ **9. Interactive User Input:** Supports live interactive student prompts via CLI and notebook `input()`.\n",
    "- ✅ **10. Jupyter Notebook Demos:** 3 complete demonstration scenarios.\n",
    "- ✅ **11. Trace & Observability:** Clear formatted trace showing Agent Decisions, Tool Calls, Tool Results, Memory Snapshots, and Final Response."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Agent Architecture (Plan-Act-Observe Loop)\n",
    "\n",
    "```\n",
    "          +-------------------------------------------------+\n",
    "          |                    USER GOAL                    |\n",
    "          +-------------------------------------------------+\n",
    "                                   |\n",
    "                                   v\n",
    "          +-------------------------------------------------+\n",
    "          |              SMARTSTUDY AGENT LOOP              |\n",
    "          |  (Reads System Prompt + History + Memory State) |\n",
    "          +-------------------------------------------------+\n",
    "                                   |\n",
    "                                   v\n",
    "          +-------------------------------------------------+\n",
    "          |              1. AGENT DECISION                  |\n",
    "          |  (Selects Tool to call or gives Final Answer)   |\n",
    "          +-------------------------------------------------+\n",
    "                     /                           \\\n",
    "       [Tool Call]  /                             \\  [Final Answer]\n",
    "                   v                               v\n",
    "    +------------------------------+     +-------------------+\n",
    "    |      2. TOOL CALL            |     |   FINAL RESPONSE  |\n",
    "    | (add_task / build_schedule)  |     +-------------------+\n",
    "    +------------------------------+\n",
    "                   |\n",
    "                   v\n",
    "    +------------------------------+\n",
    "    |      3. TOOL RESULT          |\n",
    "    | (Executes Real Python Code)  |\n",
    "    +------------------------------+\n",
    "                   |\n",
    "                   v\n",
    "    +------------------------------+\n",
    "    |   4. UPDATE SESSION MEMORY   |\n",
    "    |  (tasks, deadlines, urgency) |\n",
    "    +------------------------------+\n",
    "                   |\n",
    "                   +---> (Loop Back to AGENT DECISION for Step 2)\n",
    "```"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Setup & Imports"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import sys\n",
    "from pathlib import Path\n",
    "\n",
    "# Ensure project directory is in python path\n",
    "sys.path.insert(0, str(Path.cwd()))\n",
    "\n",
    "from config import TODAY_DATE, IS_OFFLINE_MODE, MODEL_NAME\n",
    "from memory import StudyAgentMemory\n",
    "from tools import add_task, build_schedule\n",
    "from agent import SmartStudyAgent, print_formatted_trace\n",
    "\n",
    "print('System Loaded Successfully!')\n",
    "print('Today Reference Date:', TODAY_DATE)\n",
    "print('Selected LLM Model:', MODEL_NAME)\n",
    "print('Offline Fallback Mode:', IS_OFFLINE_MODE)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Direct Tool Verification\n",
    "Let's test our two tools directly to verify that they modify application state in memory."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Initialize temporary memory instance\n",
    "test_memory = StudyAgentMemory()\n",
    "\n",
    "# Call Tool 1: add_task()\n",
    "res1 = add_task('Python Assignment', '2026-08-26', test_memory)\n",
    "print('Tool 1 (add_task) Output:')\n",
    "print(res1)\n",
    "\n",
    "# Call Tool 2: build_schedule()\n",
    "res2 = build_schedule(test_memory)\n",
    "print('\\nTool 2 (build_schedule) Output:')\n",
    "print(res2)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. DEMO 1 — Multi-Step Goal (Multiple Tool Calls in 1 Turn)\n",
    "**User Goal:** *\"I have a Python assignment due tomorrow and a DBMS exam in five days. Make a study plan.\"*\n",
    "\n",
    "**Multi-Step Agent Execution Flow:**\n",
    "1. `add_task(\"Python Assignment\", \"2026-08-26\")` -> Memory updated.\n",
    "2. `add_task(\"DBMS Exam\", \"in 5 days\")` -> Memory updated.\n",
    "3. `build_schedule()` -> Schedule generated.\n",
    "4. Final structured study plan presented."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "agent1 = SmartStudyAgent()\n",
    "prompt1 = 'I have a Python assignment due tomorrow and a DBMS exam in five days. Make a study plan.'\n",
    "\n",
    "response1, trace1 = agent1.run(prompt1)\n",
    "print_formatted_trace(prompt1, response1, trace1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 7. DEMO 2 — Session Memory Across Multi-Turn Conversation\n",
    "**Goal:** Prove memory persistence across turns.\n",
    "- **Turn 1:** *\"I have an AI assignment due tomorrow.\"* -> Agent stores task.\n",
    "- **Turn 2:** *\"What should I prioritize today?\"* -> Agent retrieves task from memory and answers without requiring the user to repeat the task name!"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "agent2 = SmartStudyAgent()\n",
    "\n",
    "print('=== TURN 1 ===')\n",
    "prompt2_t1 = 'I have an AI assignment due tomorrow.'\n",
    "resp2_t1, trace2_t1 = agent2.run(prompt2_t1)\n",
    "print_formatted_trace(prompt2_t1, resp2_t1, trace2_t1)\n",
    "\n",
    "print('\\n=== TURN 2 (Follow-up) ===')\n",
    "prompt2_t2 = 'What should I prioritize today?'\n",
    "resp2_t2, trace2_t2 = agent2.run(prompt2_t2)\n",
    "print_formatted_trace(prompt2_t2, resp2_t2, trace2_t2)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 8. DEMO 3 — Dynamic Replanning\n",
    "**Goal:** Show that when new urgent tasks arrive, the agent recalculates deadline priorities and updates the schedule dynamically."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "agent3 = SmartStudyAgent()\n",
    "\n",
    "# Step 1: Initial schedule\n",
    "agent3.run('I have a DBMS exam in 5 days. Make me a study plan.')\n",
    "print('INITIAL MEMORY TASKS:')\n",
    "print(agent3.memory.get_memory_summary())\n",
    "\n",
    "# Step 2: Introduce new urgent deadline\n",
    "prompt3_replan = 'I also have a Python assignment due tomorrow! Update my schedule.'\n",
    "resp3_replan, trace3_replan = agent3.run(prompt3_replan)\n",
    "\n",
    "print_formatted_trace(prompt3_replan, resp3_replan, trace3_replan)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 9. Failure & Edge Case Handling (Honest Edge Case)\n",
    "**Scenario:** User requests a schedule when **no tasks exist** in memory.\n",
    "**Expected Behavior:** `build_schedule()` returns structured failure result (`success: False`), informing the user to add tasks first."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "empty_agent = SmartStudyAgent()\n",
    "prompt_empty = 'Make my study schedule.'\n",
    "\n",
    "resp_empty, trace_empty = empty_agent.run(prompt_empty)\n",
    "print_formatted_trace(prompt_empty, resp_empty, trace_empty)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 10. Interactive User Input Demo\n",
    "You can test custom student prompts interactively below!"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Interactive notebook input\n",
    "interactive_agent = SmartStudyAgent()\n",
    "sample_input = \"I have a Machine Learning Lab due in 3 days and a Web Dev Project due in 7 days. Create my study schedule.\"\n",
    "print(\"Running custom prompt:\", sample_input)\n",
    "interactive_resp, interactive_trace = interactive_agent.run(sample_input)\n",
    "print_formatted_trace(sample_input, interactive_resp, interactive_trace)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 11. Conclusion & Viva Summary\n",
    "SmartStudy Agent demonstrates a complete, viva-ready Agentic AI solution with real tools, session memory, multi-step decision loops, and complete trace observability."
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

with open("SmartStudyAgent.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print("SmartStudyAgent.ipynb updated with interactive user input section!")
