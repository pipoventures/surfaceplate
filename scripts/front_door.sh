#!/bin/sh
# Every command the front door documents, run as a stranger would: a clean interpreter, the
# package installed from git (here: from the checkout under test), and a GLOBAL core.hooksPath -
# the case that stopped the review's stranger install at its first command (F70). Run by
# .github/workflows/front-door.yml in a container, and by hand with the same file.
#
#   sh scripts/front_door.sh <checkout>      # installs from <checkout>; needs pip, git, python3
set -eu
checkout=${1:-.}
work=$(mktemp -d)
target="$work/target"
mkdir -p "$target"
git config --global user.email stranger@example.invalid
git config --global user.name "A stranger"
git config --global core.hooksPath "$work/global-hooks"     # the machine the review met
git -C "$target" init -q
python3 -m venv "$work/venv"
. "$work/venv/bin/activate"
pip install --disable-pip-version-check -q "surfaceplate[adopt] @ file://$(cd "$checkout" && pwd)"

surfaceplate --version
surfaceplate --help >/dev/null
surfaceplate doctor --repo "$target" || true            # warnings are allowed; a failure would exit 1
surfaceplate install --target "$target" --dry-run --no-hooks
surfaceplate install --target "$target" --no-hooks
surfaceplate doctor --report --repo "$target" >/dev/null || true   # offline; must not need the network this script disabled
set +e
surfaceplate check --repo "$target"; code=$?
set -e
[ "$code" -eq 0 ] || { echo "check on a fresh install should be graced (exit 0), got $code"; exit 1; }
surfaceplate check --repo "$target" --format json | python3 -c 'import json,sys; d=json.load(sys.stdin); print("json:", d["result"], d["exit_code"], len(d["findings"]), "findings")'
surfaceplate check --repo "$target" --format sarif | python3 -c 'import json,sys; d=json.load(sys.stdin); print("sarif:", d["version"], len(d["runs"][0]["results"]), "results")'
git -C "$target" add -A && git -C "$target" commit -qm "install"
surfaceplate adopt --propose --target "$target" --level essential
test -f "$target/governance/application-profile.answers.yaml"
test -f "$target/governance/application-profile.proposed.yaml"
set +e
surfaceplate adopt --target "$target" </dev/null >/dev/null 2>"$work/tty.err"; code=$?
set -e
[ "$code" -eq 3 ] || { echo "adopt without a terminal should exit 3, got $code"; cat "$work/tty.err"; exit 1; }
grep -q -- "--propose" "$work/tty.err"
set +e
surfaceplate check --repo "$work/nowhere"; code=$?
set -e
[ "$code" -eq 3 ] || { echo "a missing directory should exit 3, got $code"; exit 1; }
set +e
surfaceplate check --repo "$work"; code=$?
set -e
[ "$code" -eq 2 ] || { echo "an uninstalled directory should exit 2, got $code"; exit 1; }
echo "FRONT_DOOR=PASS"
