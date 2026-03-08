#!/usr/bin/env bash
# Usage: ./run.sh <filename> [extra colorcraft flags...]
# Self-bootstrapping wrapper — automatically manages venv and dependencies.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/.venv"
PYTHON="$VENV/bin/python3"
PIP="$VENV/bin/pip"
COLORCRAFT="$VENV/bin/colorcraft"

# 1. Ensure venv exists and has a working Python
if ! "$PYTHON" --version &>/dev/null; then
    echo "Setting up environment..." >&2
    rm -rf "$VENV"
    if ! python3 -m venv "$VENV" 2>/dev/null; then
        echo "Error: Failed to create virtual environment." >&2
        exit 1
    fi
fi

# 2. Ensure colorcraft is installed
if ! "$PYTHON" -c "import colorcraft" &>/dev/null; then
    echo "Installing dependencies..." >&2
    if ! "$PIP" install -e "$SCRIPT_DIR[stability]" --quiet 2>/dev/null; then
        echo "Error: Failed to install colorcraft." >&2
        exit 1
    fi
fi

# 3. Show help if no arguments
if [ $# -eq 0 ]; then
    exec "$COLORCRAFT" --help
fi

# 4. Resolve input file — try as-is, then in input/
INPUT="$1"
shift
if [ ! -f "$INPUT" ]; then
    CANDIDATE="$SCRIPT_DIR/input/$INPUT"
    if [ -f "$CANDIDATE" ]; then
        INPUT="$CANDIDATE"
    fi
fi

exec "$COLORCRAFT" "$INPUT" "$@"
