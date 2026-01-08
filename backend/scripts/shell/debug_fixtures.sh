#!/usr/bin/env sh
# SPDX-License-Identifier: AGPL-3.0-or-later
# File: backend/scripts/shell/debug_fixtures.sh

set -euo pipefail

FIXTURE_DIR="/app/tests/debug/email_fixtures_tmp"

exec docker compose exec -e FIXTURE_DIR="$FIXTURE_DIR" \
  api \
  python3 -Xfrozen_modules=off -m debugpy \
  --listen 0.0.0.0:5679 \
  --wait-for-client \
  -m scripts.python.generate_fixtures
