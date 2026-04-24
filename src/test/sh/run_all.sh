#!/bin/bash

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <aces_dir> <is_linear_tf>"
    exit 1
fi

ACES_DIR="$1"
IS_LINEAR_TF="$2"

> out.txt

for SRC in "${ACES_DIR}"/*.exr; do
    echo "=== $(basename "$SRC") ===" | tee -a out.txt
    bash "$(dirname "$0")/find.sh" "$SRC" "$IS_LINEAR_TF" 2>&1 | tee -a out.txt
done
