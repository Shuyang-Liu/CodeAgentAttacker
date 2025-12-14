import json
from pathlib import Path

TRAJ_DIR = Path(__file__).parent.parent.parent/"outputs"/"swebench"/"gpt-5-mini"
# max: 66 for gpt-5-mini on swebench

max_api_iterations = 0
for traj_file in TRAJ_DIR.glob("**/*.traj.json"):
    with open(traj_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    api_calls = data.get("info", {}).get("model_stats", {}).get("api_calls", 0)
    if api_calls > max_api_iterations:
        max_api_iterations = api_calls

print(f"Maximum API iterations across all trajectories: {max_api_iterations}")