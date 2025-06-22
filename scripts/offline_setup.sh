#!/usr/bin/env bash

# Lightweight offline setup script for installing Python dependencies
# from a local wheelhouse directory. It attempts to install all packages
# listed in requirements.txt and reports any that are still missing
# afterwards.

set -euo pipefail

REQ_FILE="requirements.txt"
WHEELHOUSE_DIR="wheelhouse"

if [ ! -f "$REQ_FILE" ]; then
  echo "Requirements file '$REQ_FILE' not found."
  exit 1
fi

# install dependencies from wheelhouse if available
if [ -d "$WHEELHOUSE_DIR" ]; then
  echo "Installing packages from '$WHEELHOUSE_DIR'..."
  pip install --no-index --find-links="$WHEELHOUSE_DIR" -r "$REQ_FILE" || true
else
  echo "Warning: wheelhouse directory '$WHEELHOUSE_DIR' not found."
  echo "Dependencies will not be installed automatically."
fi

readarray -t packages < <(grep -v '^#' "$REQ_FILE" | sed '/^$/d')

missing=()
for pkg in "${packages[@]}"; do
  python - "$pkg" <<'PY'
import pkg_resources, sys
try:
    pkg_resources.get_distribution(sys.argv[1])
except pkg_resources.DistributionNotFound:
    raise SystemExit(1)
PY
  if [ $? -ne 0 ]; then
    missing+=("$pkg")
  fi
done

if [ ${#missing[@]} -ne 0 ]; then
  echo "\nThe following packages could not be installed:" >&2
  for m in "${missing[@]}"; do
    echo "  - $m" >&2
  done
  echo "" >&2
  echo "Ensure wheel files for these packages exist in '$WHEELHOUSE_DIR'." >&2
  echo "Populate the directory with:" >&2
  echo "  pip download -r $REQ_FILE -d $WHEELHOUSE_DIR" >&2
  exit 1
else
  echo "All packages installed successfully." 
fi

