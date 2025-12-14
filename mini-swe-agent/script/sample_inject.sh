#!/bin/bash
# Script to run attack injection on sampled instances
# Usage: ./sample_inject.sh [RUN_ID]

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL="openai/gpt-5-mini"
RUN_ID="${1:-1}"

MODEL_NAME="${MODEL##*/}"
SAMPLE_DIR="$ROOT_DIR/script/sample-data/samples/general/$RUN_ID"
SAMPLED_FILE="$SAMPLE_DIR/sampled_instances.json"

# Optionally separate runs in output dirs if you want:
OUT_BASE="$ROOT_DIR/outputs/attack/swebench/$MODEL_NAME/run-$RUN_ID"

CONFIG_PATH="$ROOT_DIR/src/minisweagent/config/extra/attack_swebench_gpt-5-mini.yaml"

# Check if sampled instances file exists
if [[ ! -f "$SAMPLED_FILE" ]]; then
    echo "Error: Sampled instances file not found: $SAMPLED_FILE" >&2
    exit 1
fi

# Extract instance IDs from JSON and build a safe regex
INSTANCE_IDS=$(python3 - <<EOF
import json, re
with open("$SAMPLED_FILE", "r") as f:
    instances = json.load(f)
ids = [re.escape(inst["instance_id"]) for inst in instances if "instance_id" in inst]
print("|".join(ids))
EOF
)

if [[ -z "$INSTANCE_IDS" ]]; then
    echo "Error: No instance IDs found in $SAMPLED_FILE" >&2
    exit 1
fi

INSTANCE_COUNT=$(printf '%s\n' "$INSTANCE_IDS" | tr '|' '\n' | wc -l)

echo "================================================================================"
echo "Attack Injection - Sampled Instances"
echo "================================================================================"
echo "Run ID:          $RUN_ID"
echo "Model:           $MODEL"
echo "Instances:       $INSTANCE_COUNT"
echo "Config:          $CONFIG_PATH"
echo "Output:          $OUT_BASE"
echo "Filter (regex):  $INSTANCE_IDS"
echo "================================================================================"

mini-extra swebench \
  --model "$MODEL" \
  --model-class openrouter \
  --subset verified \
  --split test \
  --config "$CONFIG_PATH" \
  --output "$OUT_BASE" \
  --filter "$INSTANCE_IDS" \
  --workers 4