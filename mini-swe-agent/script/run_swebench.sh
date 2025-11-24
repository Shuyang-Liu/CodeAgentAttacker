ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_BASE="$ROOT_DIR/outputs/swebench/devstral-small"
CONFIG_PATH="$ROOT_DIR/src/minisweagent/config/extra/swebench_devstral_small.yaml"

mini-extra swebench-single \
  --model mistralai/devstral-small \
  --model-class openrouter \
  --subset verified \
  --split test \
  --config "$CONFIG_PATH" \
  --output "$OUT_BASE" \
  --slice 0:1 \
  --workers 4 \
