# Viva Preparation Notes — SmartStudy Agent

> **Course:** CSE476 Agentic AI and Intelligent Automation  
> **Project:** SmartStudy Agent  

This document contains 18 comprehensive viva questions and precise, code-backed answers to help you explain every line of code during your evaluation.

---

### Q1: What is an AI agent?
**Answer:** An AI agent is an autonomous system that perceives its environment (user input & memory state), processes information using an LLM or decision brain, plans a sequence of actions, and executes concrete tools to alter its environment to achieve a goal.

### Q2: How is an agent different from a chatbot?
**Answer:** A chatbot simply generates single-turn text responses from prompt input. An AI agent runs an iterative loop: it decides *what* to do, executes real Python code (tools), observes tool outputs, updates internal state/memory, and takes multiple steps before generating a final response.

### Q3: What is the plan-act loop?
**Answer:** The Plan-Act-Observe loop is an iterative workflow:
1. **Plan:** The agent inspects user goals, context, and memory to decide the next action.
2. **Act:** The agent invokes a tool (e.g. `add_task` or `build_schedule`).
3. **Observe:** The agent receives the tool's structured output.
4. **Repeat / Respond:** If further actions are needed, it repeats the loop; otherwise, it outputs the final answer.

### Q4: Where does planning happen in this project?
**Answer:** Planning happens inside `agent.py` in the `SmartStudyAgent.run()` loop. The LLM (or offline fallback planner) analyzes system instructions, stored memory, and user requests to determine tool calls.

### Q5: Where does action happen?
**Answer:** Action happens in `agent.py` when `add_task()` or `build_schedule()` functions from `tools.py` are invoked with arguments passed by the agent.

### Q6: What are your two tools?
**Answer:**
1. `add_task(name, due, memory)`: Validates assignment/exam names and deadlines, calculates days left relative to reference date, and saves task objects into session memory.
2. `build_schedule(memory)`: Reads tasks from memory, categorizes them into High/Medium/Lower priorities based on deadline urgency, and allocates daily study hours.

### Q7: How does `add_task()` work?
**Answer:** Located in `tools.py`, it:
1. Checks that `name` is a non-empty string.
2. Converts ISO strings (`YYYY-MM-DD`) or relative text (`tomorrow`, `in 5 days`) into standard `datetime.date` objects.
3. Rejects past deadlines or invalid formats with structured error messages.
4. Appends a dictionary `{"name": ..., "due": ..., "days_left": ...}` to `memory.tasks`.

### Q8: How does `build_schedule()` work?
**Answer:** Located in `tools.py`, it:
1. Retrieves tasks from `memory.get_tasks()`.
2. Checks if tasks list is empty (returns error if 0 tasks).
3. Sorts tasks by `days_left`.
4. Categorizes tasks:
   - **HIGH PRIORITY:** $\le 2$ days left ($3.0$ hrs/day)
   - **MEDIUM PRIORITY:** $3–5$ days left ($2.0$ hrs/day)
   - **LOWER PRIORITY:** $> 5$ days left ($1.0$ hr/day)
5. Returns a structured JSON dict containing priority groups and study blocks.

### Q9: Where is memory implemented?
**Answer:** In `memory.py` under the `StudyAgentMemory` class. It manages `tasks`, `preferences`, and `conversation_history`.

### Q10: How does memory persist across turns?
**Answer:** The `SmartStudyAgent` instance maintains a single `StudyAgentMemory` object across multiple calls to `agent.run()`. When a user adds a task in Turn 1, it remains stored in `agent.memory.tasks` so Turn 2 can access it immediately.

### Q11: How does the agent decide which tool to use?
**Answer:** The agent passes `TOOLS_SCHEMA` (OpenAI JSON Schema declarations for functions) to `client.chat.completions.create()`. The LLM inspects function signatures and descriptions to return `tool_calls` specifying tool names and JSON parameters.

### Q12: What happens when a tool fails?
**Answer:** The tool returns a structured dictionary with `"success": False` and a descriptive `"message"`. The agent receives this output during the Observe phase and explains the issue to the user without crashing.

### Q13: What happens when there are no tasks?
**Answer:** When `build_schedule()` is called on empty memory, it returns `{"success": False, "message": "Cannot build schedule: There are currently no tasks stored in memory..."}`. The agent observes this result and politely prompts the user to add tasks first.

### Q14: Why did you choose this project?
**Answer:** Academic deadline planning is a real-world student problem requiring structured data validation, deadline arithmetic, priority sorting, and multi-turn conversational context—making it an ideal candidate for demonstrating agentic tool execution and session memory.

### Q15: Why is this an agent and not just a Python program?
**Answer:** A static Python program follows fixed hardcoded scripts. This agent dynamically understands natural language requests, decides which functions to call, handles unexpected input variations, and re-plans schedules dynamically based on natural language interaction.

### Q16: What part is handled by the LLM?
**Answer:** Natural language understanding, tool selection, argument extraction, tool output interpretation, and conversational final response synthesis.

### Q17: What part is deterministic Python logic?
**Answer:** Date parsing, deadline validation, urgency calculations ($\le 2$ days, $3-5$ days, $>5$ days), state mutation in `memory.py`, and error handling.

### Q18: How does the Group of 3 Add-on (Dynamic Re-planning) work?
**Answer:** When a user introduces a new urgent deadline (e.g. an assignment due tomorrow) into a conversation where older tasks already exist, the agent:
1. Calls `add_task()` to store the new deadline into `StudyAgentMemory`.
2. Calls `build_schedule()` in the same plan-act loop.
3. The scheduler computes remaining days for all stored tasks, detects that the newly added task has the shortest deadline ($\le 2$ days), elevates it to **HIGH PRIORITY** ($3.0$ hrs/day), and reshuffles the study blocks so the urgent task is tackled first.

### Q19: How would you improve this project in the future?
**Answer:**
1. Add Google Calendar / iCal API integration to export study blocks directly to digital calendars.
2. Add persistent database storage (SQLite / PostgreSQL) to save state across process restarts.
3. Implement automated reminder tools for approaching deadlines.
