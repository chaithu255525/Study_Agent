import json
import io
from contextlib import redirect_stdout

# Load notebook
with open("SmartStudyAgent.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# Global execution scope for notebook cells
exec_globals = {}

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        code = "".join(cell["source"])
        buffer = io.StringIO()
        try:
            with redirect_stdout(buffer):
                exec(code, exec_globals)
            out_str = buffer.getvalue()
            cell["outputs"] = [{
                "name": "stdout",
                "output_type": "stream",
                "text": out_str.splitlines(keepends=True)
            }]
            cell["execution_count"] = 1
        except Exception as e:
            cell["outputs"] = [{
                "name": "stderr",
                "output_type": "stream",
                "text": [f"Execution Error: {e}\n"]
            }]
            cell["execution_count"] = 1

with open("SmartStudyAgent.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)

print("SmartStudyAgent.ipynb cells executed and outputs saved successfully!")
