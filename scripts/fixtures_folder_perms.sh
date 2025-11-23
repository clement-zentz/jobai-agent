# scripts/fixtures_folder_perms.sh

set -euo pipefail

ROOT_DIR="$(dirname $(dirname $(realpath $0)))"

cd "$ROOT_DIR"

fixture_dir="app/tests/email_fixtures"
brut_data_dir="$fixture_dir/brut_data"
net_data_dir="$fixture_dir/net_data"

mkdir -p "$brut_data_dir"
mkdir -p "$net_data_dir"

sudo chown -R 999:999 "$brut_data_dir"
sudo chown -R 999:999 "$net_data_dir"

ls -ld "$fixture_dir"
ls -ld "$brut_data_dir"
ls -ld "$net_data_dir"


# Execute this script:
# --------------------
# chmod 740 scripts/fixtures_folder_perms.sh
# ./scripts/fixtures_folder_perms.sh