#!/bin/sh
# Every command the front door documents, run as a stranger would: a clean interpreter, the
# package installed from git (here: from the checkout under test), and a GLOBAL core.hooksPath -
# the case that stopped the review's stranger install at its first command (F70). Run by
# .github/workflows/front-door.yml in a container, and by hand with the same file - and running it
# by hand does not touch the operator's own git configuration (F164, below).
#
#   sh scripts/front_door.sh <checkout>      # installs from <checkout>; needs pip, git, python3
set -eu
checkout=${1:-.}
work=$(mktemp -d)
target="$work/target"
mkdir -p "$target"

# `F164`. The three settings below are GLOBAL ON PURPOSE: `F70`'s stranger met a machine with a
# global `core.hooksPath`, and reproducing that is this script's job. What was wrong was WHERE they
# were written - straight into the invoking user's `~/.gitconfig`. In the container this script was
# built for that is harmless, and the header above also invites running it by hand, where it is not:
# it rewrote the operator's git identity, so later commits in any repository without a local
# identity were authored by "A stranger", and it pointed every repository's hooks at a directory
# this script then deleted. `core.hooksPath` REPLACES `.git/hooks` rather than adding to it, so
# every hook on the machine was skipped afterwards with no error and no diff to show for it.
#
# `GIT_CONFIG_GLOBAL` moves the global scope itself into `$work`. Git still reads and writes it as
# the global scope, so `F70`'s condition is reproduced exactly rather than approximated, and
# `~/.gitconfig` is never opened. This is the isolation
# `tests/test_install_and_check.py:neutralise_ambient_git_config` has applied since 0.13.0; this
# script was the second site that never got it.
#
# The system scope (`/etc/gitconfig`) is deliberately left alone. `GIT_CONFIG_NOSYSTEM=1` would
# isolate it too and the test suite does set it, but this script never wrote there, so disabling it
# would be an untested change to the container this runs in rather than part of the fix.
export GIT_CONFIG_GLOBAL="$work/gitconfig"

# A git older than 2.32 does not know `GIT_CONFIG_GLOBAL`. It would ignore it and write to
# `~/.gitconfig` exactly as before - silently, which is how this defect survived unnoticed. So
# establish that the redirection took BEFORE writing anything, by a read rather than a write:
# plant a key in the sandbox file and ask git, at global scope, to read it back.
printf '[front-door]\n\tprobe = redirected\n' > "$GIT_CONFIG_GLOBAL"
[ "$(git config --global --get front-door.probe 2>/dev/null || true)" = "redirected" ] || {
    echo "front_door: this git ignores GIT_CONFIG_GLOBAL (2.32+ required), so the settings below"
    echo "front_door: would be written to your real ~/.gitconfig. Refusing to run. $(git --version)"
    exit 1
}

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
# `ACT-100`: the prompt is an instruction someone will follow, so it is run here rather than
# trusted - `S3`, and `F57`'s lesson. Piped through grep so a prompt that renders empty, or that
# silently loses its contract, fails the front door rather than an adopter's agent.
surfaceplate agent-prompt --target "$target" | grep -q "MUST NOT" \
  || { echo "agent-prompt produced no contract"; exit 1; }
surfaceplate agent-prompt --target "$target" --register advanced >/dev/null
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
