"""
Main Interactive CLI for SmartStudy Agent

Allows students to interactively chat with the SmartStudy Agent in the terminal,
add tasks, generate study plans, view memory, and observe live agent traces.
"""

import sys
from agent import SmartStudyAgent, print_formatted_trace
from config import MODEL_NAME, ENDPOINT_URL, IS_OFFLINE_MODE


def main():
    print("=" * 65)
    print("        🎓 SmartStudy Agent — Interactive Terminal CLI 🎓        ")
    print("=" * 65)
    print(f"🤖 Backend Model: {MODEL_NAME}")
    print(f"🌐 Endpoint: {ENDPOINT_URL}")
    print(f"🔌 Offline Fallback Mode: {IS_OFFLINE_MODE}")
    print("-" * 65)
    print("💡 Useful Commands:")
    print("   - Type any natural language goal (e.g., 'I have an AI exam in 3 days.')")
    print("   - Type 'memory' to view stored tasks in session memory")
    print("   - Type 'clear' to reset session memory")
    print("   - Type 'exit' or 'quit' to close the program")
    print("=" * 65)

    agent = SmartStudyAgent()

    while True:
        try:
            user_input = input("\nStudent > ").strip()
            if not user_input:
                continue

            cmd_lower = user_input.lower()

            if cmd_lower in ["exit", "quit", "q", "bye"]:
                print("\nGoodbye! Good luck with your studies! 📚✨")
                break

            if cmd_lower == "memory":
                print("\n[CURRENT SESSION MEMORY]:")
                print(agent.memory.get_memory_summary())
                continue

            if cmd_lower == "clear":
                agent.memory.clear()
                print("\n[SESSION MEMORY CLEARED]")
                continue

            # Execute agent plan-act loop
            response, trace_logs = agent.run(user_input)

            # Print formatted agent trace & response
            print_formatted_trace(user_input, response, trace_logs)

        except (KeyboardInterrupt, EOFError):
            print("\n\nProgram terminated. Goodbye!")
            break


if __name__ == "__main__":
    main()
