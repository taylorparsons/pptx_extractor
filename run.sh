#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

PYTHON=""
if command -v python3.11 >/dev/null 2>&1; then
  PYTHON="python3.11"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  echo "Error: No suitable Python found (need python3.11 or python3)." >&2
  exit 1
fi

if [[ ! -f "requirements.txt" ]]; then
  echo "Error: requirements.txt not found." >&2
  exit 1
fi

if [[ ! -d ".venv" ]]; then
  "$PYTHON" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install -r requirements.txt

if [[ $# -eq 0 ]]; then
  python main.py -h
else
  python main.py "$@"
fi
