#!/usr/bin/env sh
# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/scripts/shell/debug_app.sh

set -euo pipefail

exec docker compose exec api \
  python -Xfrozen_modules=off -m debugpy \
  --listen 0.0.0.0:5678 \
  --wait-for-client \
  -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
