#!/usr/bin/env bash
set -e

IDX=1

# Resolve repo root (one level above this script)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

OUT_BASE="$ROOT_DIR/outputs/swebench/devstral-small"
CONFIG_PATH="$ROOT_DIR/src/minisweagent/config/extra/debug_swebench_devstral_small.yaml"

INSTANCE_ID=$(python3 - <<EOF
from datasets import load_dataset
ds = load_dataset("princeton-nlp/SWE-Bench_Verified", split="test")
print(ds[$IDX]["instance_id"])
EOF
)

OUT_FILE="$OUT_BASE/$INSTANCE_ID/$INSTANCE_ID.traj.json"
mkdir -p "$OUT_BASE/$INSTANCE_ID"

mini-extra swebench-single \
  --model mistralai/devstral-small \
  --model-class openrouter \
  --subset verified \
  --split test \
  --config "$CONFIG_PATH" \
  --output "$OUT_FILE" \
  -i $IDX
