#!/usr/bin/env bash
# Creates a Python venv and installs all dependencies for varstar_exp.py.
# Run once:  bash setup.sh
# Then use:  source .venv/bin/activate

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "Creating virtual environment at $VENV_DIR ..."
python3 -m venv "$VENV_DIR"

echo "Installing dependencies ..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "Done.  Activate with:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "Then run:"
echo "  python3 varstar_exp.py \"R Leo\""
