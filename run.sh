#!/usr/bin/env bash
# Usage: ./run.sh <filename> [extra colorcraft flags...]
# Self-bootstrapping wrapper — requires uv (https://docs.astral.sh/uv/).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 1. Check for uv
if ! command -v uv &>/dev/null; then
    echo "Error: uv is not installed." >&2
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi

# 2. Show help if no arguments
if [ $# -eq 0 ]; then
    exec uv run --project "$SCRIPT_DIR" --extra stability colorcraft --help
fi

# 3. Resolve input file — try as-is, then in input/
INPUT="$1"
shift
if [ ! -f "$INPUT" ]; then
    CANDIDATE="$SCRIPT_DIR/input/$INPUT"
    if [ -f "$CANDIDATE" ]; then
        INPUT="$CANDIDATE"
    fi
fi

exec uv run --project "$SCRIPT_DIR" --extra stability colorcraft "$INPUT" "$@"
