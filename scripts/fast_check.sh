#!/usr/bin/env bash
set -euo pipefail
CHANGED=$(git diff --name-only --diff-filter=ACM HEAD | grep -E '\.py$' || true)
if [ -n "$CHANGED" ]; then
  black $CHANGED
  ruff $CHANGED
  pyright $CHANGED
else
  echo "No Python files changed."
fi
pytest
