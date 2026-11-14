#!/usr/bin/env bash
# Checks whether sensitive or generated files are tracked by Git.

set -euo pipefail

PATTERNS=("\.env$" "\.db$" "\.pem$" "\.key$")
FOUND=0

for pattern in "${PATTERNS[@]}"; do
  matches=$(git ls-files | grep -E "$pattern" || true)
  if [ -n "$matches" ]; then
    echo "[WARNING] Tracked files matching $pattern:"
    echo "$matches"
    FOUND=1
  fi
done

if [ "$FOUND" -eq 0 ]; then
  echo "[OK] No sensitive or generated files are tracked."
fi

exit "$FOUND"
