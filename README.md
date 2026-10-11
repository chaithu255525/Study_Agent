# SmartStudy Agent — An Agentic AI Study Planner

> **Course:** CSE476 Agentic AI and Intelligent Automation  
> **Project:** CA1 Project 1 — Build a Real Agent  
> **Topic:** T24 — Study Planner Agent  
> **Project Name:** SmartStudy Agent  

---

## 1. Project Overview

**SmartStudy Agent** is a real agentic AI study planner that helps university students organize deadlines and build prioritized study schedules. Unlike generic chatbots, SmartStudy Agent runs a **multi-step Plan-Act-Observe loop**: it dynamically decides which tools to call, executes real Python functions to update session memory, observes tool execution outputs, and replans until the user's goal is met.

---

## 2. Official CA1 3-Paragraph Summary

**The Two Tools:** The agent uses `add_task(name, due)` and `build_schedule()`. The `add_task` tool validates assignment names, parses ISO and relative dates (e.g. `tomorrow`, `in 5 days`), rejects expired deadlines, and saves structured task objects to memory. The `build_schedule` tool reads stored tasks, calculates remaining days relative to the reference date, sorts tasks by deadline urgency, and allocates daily study hours ($\le 2$ days = 3.0 hrs/day High Priority, $3–5$ days = 2.0 hrs/day Medium Priority, $> 5$ days = 1.0 hr/day Lower Priority).

**What the Memory Does:** The `StudyAgentMemory` class persists state across multiple turns in the same conversation session, storing task records, study preferences, and conversation history. This enables the agent to remember tasks added in earlier turns and immediately answer follow-up queries (such as *"What should I prioritize today?"*) without asking the user to repeat deadline information.

**One Honest Failure and How We Handled It:** A real edge-case failure occurred when a user asked the agent to *"Make my study schedule"* before adding any tasks to memory. Instead of crashing or hallucinating a fake schedule, `build_schedule()` checks for empty memory and returns a structured failure dictionary (`{"success": False, "message": "Cannot build schedule: There are currently no tasks stored in memory..."}`). The agent observes this result and politely instructs the student to add tasks first.

**Group of 3 Contribution Note:** Student 1 implemented the Plan-Act-Observe agent loop and tool-calling integration in `agent.py`; Student 2 developed `add_task()`, `build_schedule()`, deadline arithmetic, and dynamic replanning in `tools.py`; Student 3 built `StudyAgentMemory` in `memory.py`, unit test suite (`tests/test_tools.py`), CLI `main.py`, and demo notebook (`SmartStudyAgent.ipynb`).

---

## 3. The Two Tools (Detailed Specification)

SmartStudy Agent is equipped with two real Python tools defined in `tools.py`:

1. **`add_task(name, due)`**
   - **Purpose:** Validates and stores academic assignments or exams in session memory.
   - **Validation:** Ensures task name is non-empty, due date is valid (ISO `YYYY-MM-DD` or relative like `tomorrow`, `in 5 days`), and deadline has not already passed.
   - **Return Value:** Structured JSON containing success status, task details, and calculated days left.

2. **`build_schedule()`**
   - **Purpose:** Reads stored tasks from memory, calculates deadline urgency, sorts tasks, and generates prioritized daily study blocks.
   - **Urgency Levels:**
     - 🔴 **HIGH PRIORITY**: Due in $\le 2$ days (3.0 hrs/day)
     - 🟡 **MEDIUM PRIORITY**: Due in $3–5$ days (2.0 hrs/day)
     - 🟢 **LOWER PRIORITY**: Due in $> 5$ days (1.0 hr/day)
   - **Return Value:** Structured schedule dictionary containing task priorities and daily focus blocks.

---

## 4. Session Memory Design

Implemented in `memory.py`, **`StudyAgentMemory`** persists state across multiple turns in the same execution session:
- **`tasks`**: List of dictionaries storing task names, deadlines, and urgency metadata.
- **`preferences`**: User study preferences (e.g., maximum daily study hours).
- **`conversation_history`**: Multi-turn dialogue history.

### Memory Retrieval Example:
- **Turn 1:** User says *"I have an AI assignment due tomorrow."* $\rightarrow$ Tool `add_task` saves it to memory.
- **Turn 2:** User asks *"What should I prioritize today?"* $\rightarrow$ The agent reads `AI Assignment` directly from session memory without asking the user to re-enter details.

---

## 5. Agentic Behavior & Plan-Act Loop

The agent follows an explicit **Plan-Act-Observe loop** in `agent.py`:

```text
          +-------------------------------------------------+
          |                    USER GOAL                    |
          +-------------------------------------------------+
                                   |
                                   v
          +-------------------------------------------------+
          |              SMARTSTUDY AGENT LOOP              |
          |  (Reads System Prompt + History + Memory State) |
          +-------------------------------------------------+
                                   |
                                   v
          +-------------------------------------------------+
          |              1. AGENT DECISION                  |
          |  (Selects Tool to call or gives Final Answer)   |
          +-------------------------------------------------+
                     /                           \
       [Tool Call]  /                             \  [Final Answer]
                   v                               v
    +------------------------------+     +-------------------+
    |      2. TOOL CALL            |     |   FINAL RESPONSE  |
    | (add_task / build_schedule)  |     +-------------------+
    +------------------------------+
                   |
                   v
    +------------------------------+
    |      3. TOOL RESULT          |
    | (Executes Real Python Code)  |
    +------------------------------+
                   |
                   v
    +------------------------------+
    |   4. UPDATE SESSION MEMORY   |
    |  (tasks, deadlines, urgency) |
    +------------------------------+
                   |
                   +---> (Loop Back to AGENT DECISION for Step 2)
```

1. **Goal Understanding:** Agent reads user prompt, conversation history, and current memory summary.
2. **Action Decision:** LLM (via OpenAI tool calling) selects tool to call or decides on final answer.
3. **Tool Execution:** Agent executes real Python functions (`add_task` / `build_schedule`).
4. **Observation:** Tool result is returned to the agent context.
5. **Re-evaluation:** Agent re-evaluates state and takes further tool steps if required.
6. **Final Response:** Once all tool steps are complete, agent provides structured response to user.

---

## 6. Example Agent Trace

```text
============================================================
                      AGENT TRACE                       
============================================================

[USER INPUT]: I have a Python assignment due tomorrow and a DBMS exam in five days. Make a study plan.

[STEP 1: AGENT DECISION]
  Decision: Decided to execute tool 'add_task' for Python assignment.
  Tool Executed: add_task
  Arguments Passed: {"name": "Python Assignment", "due": "2026-08-26"}

[STEP 1: TOOL RESULT]
  Tool Name: add_task
  Output: { "success": true, "message": "Task 'Python Assignment' successfully added..." }
  [MEMORY SNAPSHOT AFTER TOOL]:
    1. Python Assignment (Due: 2026-08-26, Days Left: 1)

[STEP 2: AGENT DECISION]
  Decision: Decided to execute tool 'add_task' for DBMS exam.
  Tool Executed: add_task
  Arguments Passed: {"name": "DBMS Exam", "due": "in 5 days"}

[STEP 2: TOOL RESULT]
  Tool Name: add_task
  Output: { "success": true, "message": "Task 'DBMS Exam' successfully added..." }
  [MEMORY SNAPSHOT AFTER TOOL]:
    1. Python Assignment (Due: 2026-08-26, Days Left: 1)
    2. DBMS Exam (Due: 2026-08-30, Days Left: 5)

[STEP 3: AGENT DECISION]
  Decision: Decided to execute tool 'build_schedule'.
  Tool Executed: build_schedule
  Arguments Passed: {}

[STEP 3: TOOL RESULT]
  Tool Name: build_schedule
  Output: { "success": true, "total_tasks": 2, "priorities": { "high": ["Python Assignment"], "medium": ["DBMS Exam"] } }

[STEP 4: FINAL RESPONSE]
  Here is your study plan...
============================================================
```

---

## 7. Honest Failure & Edge Case Handling

- **Failure Scenario:** User asks *"Make my study schedule"* when **NO tasks exist** in memory.
- **Handling:** `build_schedule()` detects zero tasks and returns `{"success": False, "message": "Cannot build schedule: There are currently no tasks stored in memory..."}`.
- **Agent Response:** The agent gracefully informs the user to add tasks first, preventing crashes or hallucinated schedules.

---

## 8. Group of 3 Add-On: Dynamic Re-planning

- **Requirement:** When a new urgent task arrives, the agent must dynamically re-plan study blocks before each due date.
- **Implementation:** When an urgent task (e.g. assignment due tomorrow) is added after existing medium/low priority tasks, the agent invokes `add_task` to insert the new record and immediately re-invokes `build_schedule()`. The scheduler recalculates days remaining, elevates the urgent task to **HIGH PRIORITY** ($3.0$ hrs/day), and moves it to the top of daily focus blocks ahead of longer-term deadlines.
- **Demonstration:** Shown in Demo 3 of `SmartStudyAgent.ipynb` and verified in unit test `test_replanning_with_new_urgent_task`.

---

## 9. Group Submission Note (Who-Did-What)

- **Student 1:** Designed agent architecture, multi-step Plan-Act-Observe loop, and OpenAI function calling integration in `agent.py`.
- **Student 2:** Implemented `add_task()`, `build_schedule()`, deadline arithmetic, priority sorting, and dynamic replanning in `tools.py`.
- **Student 3:** Built `StudyAgentMemory` in `memory.py`, unit test suite (`tests/test_tools.py`), CLI `main.py`, and interactive Jupyter Notebook demo (`SmartStudyAgent.ipynb`).

---

## 10. Installation & Setup

### Prerequisites
- Python 3.10+

### Quick Start Commands
```bash
# 1. Clone/Navigate to repository
cd Study_Agent-

# 2. (Optional) Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure API Credentials
cp .env.example .env
# Edit .env and add GROQ_API_KEY, GROK_API_KEY, or GITHUB_TOKEN if using live API
```

> **Note:** If no API key is set, SmartStudy Agent automatically uses its built-in deterministic offline fallback driver for grading and offline evaluation out of the box!

---

## 11. Running Interactive CLI, Tests & Notebook

### 1. Interactive Terminal CLI (Ask User Input Live)
Run `main.py` to open an interactive terminal session where you can chat live with the agent:

```bash
python main.py
```

Features inside `main.py`:
- Type any assignment or exam deadline (e.g. `I have an AI Project due in 4 days. Make a schedule.`).
- Type `memory` to view all tasks stored in session memory.
- Type `clear` to reset memory.
- Type `exit` to quit.

---

### 2. Run Unit Tests
```bash
python -m unittest tests/test_tools.py
```

---

### 3. Launch Jupyter Notebook
```bash
jupyter notebook SmartStudyAgent.ipynb
```

---

### 4. Generate Publication-Ready PDF Report
```bash
python generate_pdf.py
```
This automatically compiles `PROJECT_REPORT.md` into `SmartStudyAgent_Project_Report.pdf` with publication styling.

---

## 12. Viva Explanation Cheat Sheet

- **Why is this an agent and not a chatbot?**  
  A chatbot produces single-turn text responses. SmartStudy Agent has an autonomous Plan-Act-Observe loop: it evaluates state, selects tools, executes Python code, observes output, and takes multiple steps per turn.
- **Where are the tools?** Defined in `tools.py` as `add_task()` and `build_schedule()`.
- **Where is memory?** Managed in `memory.py` via `StudyAgentMemory`.
- **Where is the Plan-Act loop?** Implemented in `agent.py` inside `SmartStudyAgent.run()`.
- **Where is the Group of 3 Add-on?** Dynamic replanning triggered in `SmartStudyAgent.run()` calling `build_schedule()` whenever new urgent deadlines are added.

---

## 13. Additional Project Documentation
- Generated PDF Report: [`SmartStudyAgent_Project_Report.pdf`](SmartStudyAgent_Project_Report.pdf)
- Detailed Technical Markdown Report: [`PROJECT_REPORT.md`](PROJECT_REPORT.md)
- Complete Viva Preparation Q&A (19 Questions): [`VIVA_NOTES.md`](VIVA_NOTES.md)
- Interactive Jupyter Demo: [`SmartStudyAgent.ipynb`](SmartStudyAgent.ipynb)
