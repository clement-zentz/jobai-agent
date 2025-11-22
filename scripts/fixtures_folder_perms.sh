# scripts/fixtures_folder_perms.sh

set -euo pipefail

ROOT_DIR="$(dirname $(dirname $(realpath $0)))"

cd "$ROOT_DIR"

fixture_dir="app/tests/email_fixtures"

mkdir -p "$fixture_dir"
sudo chown -R 999:999 "$fixture_dir"
ls -ld "$fixture_dir"


# Execute this script:
# --------------------
# chmod 740 scripts/fixtures_folder_perms.sh
# ./scripts/fixtures_folder_perms.sh