#!/bin/bash
# backend/scripts/shell/mkdir_mounted_folders.sh

# This script must be executed outside containers with your host user.

# Solve permission denied when os.mkdir(...) try to create folders inside container.

set -euo pipefail

BACKEND_DIR="$(dirname $(dirname $(dirname $(realpath $0))))"

echo "BACKEND_DIR = $BACKEND_DIR"

ENV_PATH="$BACKEND_DIR/.env"

if [ ! -f "$ENV_PATH" ]; then
    echo "❌ .env file not found"
    exit 1
fi

set -a
source "$ENV_PATH"
set +a

cd "$BACKEND_DIR"

HOST_SAMPLE_DIR="$(dirname $SAMPLE_DIR)"
HOST_FIXTURE_DIR="$(dirname $FIXTURE_DIR)"

mkdir -p "$BACKEND_DIR/$HOST_SAMPLE_DIR"
mkdir -p "$BACKEND_DIR/$HOST_FIXTURE_DIR"

if [ $? -ne 0 ]; then
    echo "❌ last command execution failed."
    exit 1
fi

echo "✅ $SAMPLE_DIR and $FIXTURE_DIR successfully created."

# Execute this script:
# --------------------
# chmod 740 backend/scripts/shell/mkdir_mounted_folders.sh
# ./backend/scripts/shell/mkdir_mounted_folders.sh