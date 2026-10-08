#!/usr/bin/env bash
# Same task, same workspace, several models: compare gate results side by side.
#   pi/compare_models.sh "<task>" <asof> <sources.json> <provider/model> [<provider/model> ...]
set -uo pipefail

if [[ $# -lt 4 ]]; then
  echo "usage: pi/compare_models.sh \"<task>\" <asof> <sources.json> <model> [<model> ...]" >&2
  exit 2
fi
task="$1"
asof="$2"
sources="$3"
shift 3

stamp="$(date +%Y%m%d-%H%M%S)"
for model in "$@"; do
  echo "=== ${model}"
  irh run "$task" --asof "$asof" --sources "$sources" --model "$model" \
    --out "runs/compare-${stamp}/${model//\//_}" | tail -n 12
done
