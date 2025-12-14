ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL="openai/gpt-5-mini"
MODEL_NAME="${MODEL##*/}"
OUT_BASE="$ROOT_DIR/outputs/swebench/$MODEL_NAME"
CONFIG_PATH="$ROOT_DIR/src/minisweagent/config/extra/swebench_gpt-5-mini.yaml"

mini-extra swebench \
  --model "$MODEL" \
  --model-class openrouter \
  --subset verified \
  --split test \
  --config "$CONFIG_PATH" \
  --output "$OUT_BASE" \
  --slice 0:1 \
  --workers 4 \
