#!/usr/bin/env bash
# Run one task through Pi with the harness.
#   pi/run.sh "<task>" <asof YYYY-MM-DD> [sources.json] [provider/model]
# The model defaults to $IRH_MODEL, then deepseek/deepseek-chat.
set -euo pipefail

task="${1:?usage: pi/run.sh \"<task>\" <asof> [sources.json] [provider/model]}"
asof="${2:?asof date (YYYY-MM-DD) required}"
sources="${3:-}"
model="${4:-${IRH_MODEL:-deepseek/deepseek-chat}}"

args=(run "$task" --asof "$asof" --model "$model")
if [[ -n "$sources" ]]; then
  args+=(--sources "$sources")
fi
exec irh "${args[@]}"
