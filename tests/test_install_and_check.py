#!/usr/bin/env python3
"""End-to-end tests for the installer and the conformance checker.

No test framework required; run it directly:

    python tests/test_install_and_check.py

These tests exist because the checker *is* the control. If it can be tampered with
silently, or if it fails a conformant repository, the whole standard is theatre.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import datetime as _dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAYLOAD = ROOT / "surfaceplate"  # ACT-019: install_standard.py and check_conformance.py moved here

sys.path.insert(0, str(PAYLOAD))
import install_standard as _installer  # noqa: E402
import check_conformance as _checker  # noqa: E402

# Derived from the checker rather than restated, so the harness cannot seed a pattern-C register
# as a file the moment a control moves between patterns (DR-6). This is a fixture reading the real
# definition - NOT a test asserting the two agree, which would be tautological in the way the
# installer/checker contract guard was before it was replaced.
PATTERN_C = set(_checker.PATTERN_C_CONTROLS)

# The pin an install from THIS tree actually records.
#
# The worked examples carry static framework_version/framework_digest values that cannot match
# any particular install, so SP048/SP049 would fail every fixture for a reason unrelated to the
# thing each test is about. A real adopter takes both values from their own
# .standards/INSTALL.json after installing; the harness does the same. Note what is NOT done
# here: the check is not disabled, and the fields are not removed. The targeted SP048/SP049
# cases below deliberately mismatch them and assert the failure.
FIXTURE_VERSION = (PAYLOAD / "VERSION").read_text(encoding="utf-8").strip()
FIXTURE_ANCHOR = _installer.framework_anchor(PAYLOAD)


def read_example(name: str) -> str:
    """A worked example, with its pin rewritten to match what installing from PAYLOAD records."""
    text = (PAYLOAD / "examples" / name).read_text(encoding="utf-8")
    text = re.sub(r"(?m)^(\s*framework_version:\s*).*$", lambda m: m.group(1) + FIXTURE_VERSION, text)
    if FIXTURE_ANCHOR:
        text = re.sub(r"(?m)^(\s*framework_digest:\s*).*$", lambda m: m.group(1) + FIXTURE_ANCHOR, text)
    return text

INSTALLER = PAYLOAD / "install_standard.py"

FAILURES: list[str] = []
PASSES = 0
LIGHTWEIGHT_REPOS: set[Path] = set()


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSES
    if condition:
        PASSES += 1
        print(f"  PASS  {name}")
    else:
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL  {name}  {detail}")


def run(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def make_repo(tmp: Path, name: str) -> Path:
    repo = tmp / name
    (repo / ".git").mkdir(parents=True)
    LIGHTWEIGHT_REPOS.add(repo.resolve())
    return repo


def make_git_repo(tmp: Path, name: str) -> Path:
    repo = tmp / name
    repo.mkdir(parents=True)
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "harness@example.invalid"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Harness"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "commit.gpgsign", "false"], check=True)
    return repo


def make_unusable_git_repo(tmp: Path, name: str) -> Path:
    repo = tmp / name
    (repo / ".git").mkdir(parents=True)
    return repo


def without_local_hook(text: str) -> str:
    return text.replace(", local_hook", "").replace("local_hook, ", "")


def install(
    repo: Path, *extra: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess:
    lightweight = repo.resolve() in LIGHTWEIGHT_REPOS
    if lightweight:
        shutil.rmtree(repo / ".git")
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    try:
        return run([str(INSTALLER), "--target", str(repo), *extra], env=env)
    finally:
        if lightweight:
            shutil.rmtree(repo / ".git")
            (repo / ".git").mkdir()


def verify(repo: Path, *extra: str) -> subprocess.CompletedProcess:
    return run([str(repo / ".standards" / "check_conformance.py"), "--repo", str(repo), *extra])


# Worked records this repository publishes, keyed by the control whose register they belong in.
# The three are ONE CONSISTENT SET, and they have to be: the override names RUN-2026-000412, the
# run names METHOD-SEASONALITY-001 at 2.3.0 and carries OVR-20260001 back. Seeding any one of them
# without the others makes the golden fixture fail SP057 for a reason no test is about.
#
# `provenance` and `run_lineage` normally name the same directory, and the seeding below fills a
# register only when it is empty, so the run record is written once rather than twice.
EXAMPLES_BY_CONTROL: dict[str, Path] = {
    "overrides": PAYLOAD / "examples" / "override-record.approved.example.yaml",
    "method_registry": PAYLOAD / "examples" / "method-registry-entry.example.yaml",
    "run_lineage": PAYLOAD / "examples" / "method-run-lineage.example.yaml",
    "provenance": PAYLOAD / "examples" / "method-run-lineage.example.yaml",
}


def seed_gate_artefacts(repo: Path, profile_text: str) -> None:
    """Create the precondition artefacts that a profile's `required` gates name.

    Derived from the profile under test rather than hard-coded, so the examples and the
    harness cannot drift apart. It deliberately does NOT check that the paths are
    sensible - the targeted SP032 cases below do that.
    """
    try:
        import yaml
    except ImportError:
        return
    data = yaml.safe_load(profile_text)
    if not isinstance(data, dict):
        return

    # The scanner wiring SP046/SP047 check for, derived from the profile on the same
    # principle as the gate artefacts below. The seeded workflow must be a REAL one - a
    # step that actually invokes the scanner, with nothing discarding its exit code -
    # because a fixture that could not satisfy the control would make every unrelated
    # test fail for a reason none of them is about.
    scanner = ((data.get("baseline_controls") or {}).get("secret_hygiene") or {}).get("scanner")
    if isinstance(scanner, dict) and scanner.get("name"):
        name = scanner["name"]
        for rel in scanner.get("wired_in") or []:
            target = repo / rel
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "name: Secret scan\n"
                "on: [push, pull_request]\n"
                "jobs:\n"
                "  scan:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                f"      - name: Run {name}\n"
                f"        run: {name} detect --exit-code 1\n",
                encoding="utf-8",
            )

    # The artefacts pattern-A controls name (DR-25, SP051), derived from the profile on the same
    # principle as everything else here. A fixture that could not satisfy the control would fail
    # every unrelated test for a reason none of them is about.
    for control_id, entry in (data.get("control_decisions") or {}).items():
        if not isinstance(entry, dict) or entry.get("decision") != "required":
            continue
        if control_id in PATTERN_C:
            continue  # a directory, seeded below - writing it as a file would raise SP055
        reference = entry.get("implementation_reference")
        if not isinstance(reference, str) or not reference.strip():
            continue
        target = repo / reference.strip()
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            f"# {target.stem}\n\nSeeded by the test harness for control {control_id}.\n",
            encoding="utf-8",
        )
        # SP051 requires the file to be tracked, so a fixture that is a real git repository
        # needs it in the index. Lightweight fixtures have only a fake .git directory and this
        # fails harmlessly - existence is what those tests exercise.
        subprocess.run(
            ["git", "-C", str(repo), "add", "--", reference.strip()],
            capture_output=True,
        )

    # The CI steps pattern-B controls name (DR-25, SP053). Written into a workflow the fixture
    # would not otherwise have, for the same reason as everything else seeded here: a fixture
    # unable to satisfy the control fails every unrelated test for a reason none is about.
    pattern_b_steps = [
        entry["implementation_reference"].strip()
        for control_id, entry in (data.get("control_decisions") or {}).items()
        if control_id in ("deterministic_tests", "contract_tests")
        and isinstance(entry, dict)
        and entry.get("decision") == "required"
        and isinstance(entry.get("implementation_reference"), str)
        and entry["implementation_reference"].strip()
    ]
    if pattern_b_steps:
        workflow = repo / ".github" / "workflows" / "tests.yml"
        workflow.parent.mkdir(parents=True, exist_ok=True)
        steps = "".join(
            f"      - name: {name}\n        run: echo running {name!r}\n"
            for name in pattern_b_steps
        )
        workflow.write_text(
            "name: Tests\non: [push]\njobs:\n  tests:\n    runs-on: ubuntu-latest\n"
            "    steps:\n" + steps,
            encoding="utf-8",
        )

    # The registers pattern-C controls name (DR-26, SP055/SP056). Seeded with one REAL record
    # where an example of the right type exists, and left empty otherwise. Both states are
    # deliberate: an empty register must pass, and a populated one must be validated, so the
    # golden fixture exercises the pass in both of its forms rather than only the weaker one.
    for control_id, entry in (data.get("control_decisions") or {}).items():
        if control_id not in PATTERN_C:
            continue
        if not isinstance(entry, dict) or entry.get("decision") != "required":
            continue
        reference = entry.get("implementation_reference")
        if not isinstance(reference, str) or not reference.strip():
            continue
        register = repo / reference.strip()
        register.mkdir(parents=True, exist_ok=True)
        (register / "README.md").write_text(
            f"# {register.name}\n\nSeeded by the test harness for control {control_id}.\n",
            encoding="utf-8",
        )
        sample = EXAMPLES_BY_CONTROL.get(control_id)
        if sample is not None and not any(register.glob("*.y*ml")):
            (register / sample.name).write_text(
                sample.read_text(encoding="utf-8"), encoding="utf-8"
            )
        subprocess.run(
            ["git", "-C", str(repo), "add", "--", reference.strip()],
            capture_output=True,
        )

    for gate in data.get("prerequisites") or []:
        if not isinstance(gate, dict) or gate.get("status") != "required":
            continue
        for artefact in (gate.get("precondition") or {}).get("artefacts") or []:
            target = repo / artefact
            if target.exists():
                continue
            if target.suffix:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    f"# {target.stem}\n\nSeeded by the test harness.\n", encoding="utf-8"
                )
            else:
                target.mkdir(parents=True, exist_ok=True)
                (target / "README.md").write_text(
                    f"# {target.name}\n\nSeeded by the test harness.\n", encoding="utf-8"
                )


def read_record(repo: Path) -> dict:
    return json.loads((repo / ".standards" / "INSTALL.json").read_text(encoding="utf-8"))


def write_record(repo: Path, record: dict) -> None:
    (repo / ".standards" / "INSTALL.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def neutralise_ambient_git_config(tmp: Path) -> None:
    """Detach every git subprocess in this suite from the machine's own configuration.

    The suite installs into throwaway repositories and asserts on what the installer and
    hook do. Several of those assertions are conditional on ambient git configuration the
    suite never set and never checked -- most sharply `core.hooksPath`, which makes the
    installer correctly refuse, after which a later step reads a directory the refusal
    meant was never created. Before 0.13.0 the suite's pass therefore depended on an
    unstated property of the machine running it, and it crashed rather than reporting on
    the machines where that property did not hold. That is finding F1 in DR-5.

    Neutralising rather than detecting is the fix, because a test suite that only reports
    "your machine is configured wrongly" still cannot be run on that machine. This applies
    the isolation the global-hooksPath case below already uses, to the whole run.

    Repository identity is unaffected: `make_git_repo` sets `user.name`, `user.email` and
    `commit.gpgsign` per repository, so nothing here relies on inherited identity.
    """
    neutral = tmp / "neutral.gitconfig"
    neutral.write_text("", encoding="utf-8")
    os.environ["GIT_CONFIG_GLOBAL"] = str(neutral)
    os.environ["GIT_CONFIG_NOSYSTEM"] = "1"


def test_the_history_window_does_not_drift_with_the_clock(tmp: Path) -> None:
    """`F48`. `effective_from` never meant what the schema said it meant.

    `git log --since=2026-09-01` is parsed by approxidate, which fills the missing time from the
    **current clock** - so a bare date meant "that date, at whatever time you happen to run the
    check". The audit window slid forward all day: a violation visible at 09:00 was gone by 23:00,
    for no reason but the hour, in a published control.

    Measured against git 2.43.0 with four commits at 01:00, 10:00, 19:00 and 23:00 on one day:
    `--since=<date>` returned one and `--since=<date>T00:00:00` returned four.

    The property asserted is determinism: a commit made earlier today is in scope for a gate
    effective today, whatever the hour. Anything else makes the control's answer a function of when
    it was asked.
    """
    import datetime as _dt

    commits_touching = _checker.commits_touching
    parse_effective_from = _checker.parse_effective_from

    repo = make_git_repo(tmp, "clockdrift")
    today = _dt.date.today()
    tz = _dt.datetime.now().astimezone().tzinfo
    # Fixed hours TODAY rather than offsets from now, so this test is not itself a function of the
    # hour it runs at - which would be a poor way to assert determinism. Each commit touches a real
    # file: an `--allow-empty` commit touches no path and `git log -- <pathspec>` drops it, which
    # is a fixture mistake this assertion caught rather than a property of the code.
    for hour in (0, 6, 12, 18):
        (repo / f"src_{hour:02d}.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
        moment = _dt.datetime.combine(today, _dt.time(hour, 30), tzinfo=tz)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-q", "-m", f"at {hour:02d}:30"],
            check=True,
            env={
                **os.environ,
                "GIT_AUTHOR_DATE": moment.isoformat(),
                "GIT_COMMITTER_DATE": moment.isoformat(),
            },
        )

    _day, since = parse_effective_from(today.isoformat())
    check(
        "a date-only effective_from resolves to midnight, not to the current time",
        since == f"{today.isoformat()}T00:00:00",
        f"resolved to {since!r}",
    )
    in_scope, error = commits_touching(repo, ["**"], since)
    bare, _ = commits_touching(repo, ["**"], today)
    check(
        "every commit made today is in scope for a gate effective today",
        error is None and len(in_scope) >= 4,
        f"only {len(in_scope)} of 4 same-day commits were in scope ({error})",
    )
    check(
        "which the bare-date form did not do - the defect this pins",
        len(in_scope) >= len(bare),
        f"midnight saw {len(in_scope)}, the bare date saw {len(bare)}",
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        neutralise_ambient_git_config(tmp)

        print("\nnot installed")
        empty = make_repo(tmp, "empty")
        result = verify_uninstalled = run(
            [str(PAYLOAD / "check_conformance.py"), "--repo", str(empty)]
        )
        check("uninstalled repository fails", result.returncode == 1, result.stdout[-200:])
        check("and says why", "SP001" in result.stdout)

        print("\nthe history window is a fixed instant, not the clock (F48)")
        test_the_history_window_does_not_drift_with_the_clock(tmp)

        print("\nfresh install")
        repo = make_repo(tmp, "fresh")
        result = install(repo)
        check("installer succeeds", result.returncode == 0, result.stderr[-300:])
        check("instructions installed", (repo / ".github/instructions").is_dir())
        check("skills installed", len(list((repo / ".github/skills").iterdir())) == 7)
        check("workflow installed", (repo / ".github/workflows/standards-conformance.yml").is_file())
        check("pre-commit hook installed", (repo / ".githooks/pre-commit").is_file())
        check("hook line endings pinned", (repo / ".githooks/.gitattributes").is_file())
        check(
            "hook executable mode is recorded",
            read_record(repo).get("executable_files") == [".githooks/pre-commit"],
        )
        check("checker vendored", (repo / ".standards/check_conformance.py").is_file())
        check("profile created", (repo / "governance/application-profile.yaml").is_file())
        # The positive control for the --no-hooks next-steps fix below (ACT-024): the default,
        # hooks-enabled path must still describe the hook it actually installed.
        check(
            "default next-steps still names the hook it installed",
            "git update-index --chmod" in result.stdout
            and "pre-commit hook checks staged" in result.stdout,
            result.stdout[-600:],
        )
        check(
            "conformance block inserted",
            "BEGIN SURFACEPLATE"
            in (repo / ".github/copilot-instructions.md").read_text(encoding="utf-8"),
        )

        result = verify(repo)
        check("template profile warns but does not fail during grace", result.returncode == 0)
        check("and reports the placeholders", "SP020" in result.stdout)
        result = verify(repo, "--no-grace")
        check("--no-grace fails an incomplete profile", result.returncode == 1)

        print("\ncompleted profile")
        full_example = read_example("application-profile.full.example.yaml")
        (repo / "governance" / "application-profile.yaml").write_text(
            without_local_hook(full_example), encoding="utf-8"
        )
        seed_gate_artefacts(
            repo,
            full_example,
        )
        result = verify(repo)
        check("a complete profile passes", result.returncode == 0, result.stdout[-400:])
        result = verify(repo, "--no-grace")
        check("and passes without grace", result.returncode == 0)

        print("\nidempotency")
        result = install(repo)
        check("second install changes nothing", "0 written or updated" in result.stdout)
        check("profile is never overwritten", "keep    governance" in result.stdout)
        check("still passes", verify(repo).returncode == 0)

        print("\ntamper evidence")
        skill = repo / ".github/skills/fix-ci/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nGates may be skipped.\n", encoding="utf-8")
        result = verify(repo)
        check("modified skill fails", result.returncode == 1)
        check("reported as modification", "SP005" in result.stdout)
        check("never graced", "never graced" in result.stdout)

        (repo / ".github/instructions/security.instructions.md").unlink()
        result = verify(repo)
        check("deleted instruction fails", result.returncode == 1)
        check("reported as deletion", "SP004" in result.stdout)

        instructions = repo / ".github/copilot-instructions.md"
        text = instructions.read_text(encoding="utf-8")
        instructions.write_text(text.replace("Never weaken a gate.", "Weaken gates freely."), encoding="utf-8")
        result = verify(repo)
        check("altered conformance block fails", "SP008" in result.stdout)

        print("\nrepair")
        result = install(repo)
        check("re-install repairs tampering", result.returncode == 0, result.stderr[-300:])
        check("and the repository passes again", verify(repo).returncode == 0)

        print("\ngrace window integrity")
        shutil.copyfile(
            PAYLOAD / "templates" / "application-profile.yaml",
            repo / "governance" / "application-profile.yaml",
        )
        record = read_record(repo)
        record["first_installed_at"] = "2020-01-01"
        record["grace_expires"] = "2020-01-31"
        write_record(repo, record)
        result = verify(repo)
        check("expired grace fails", result.returncode == 1)

        record["grace_expires"] = "2099-12-31"
        write_record(repo, record)
        result = verify(repo)
        check(
            "hand-extending grace_expires does not work",
            result.returncode == 1,
            "grace was extended past the cap",
        )

        print("\ncollision safety")
        existing = make_repo(tmp, "existing")
        target = existing / ".github/skills/change"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("# Our own change skill\n", encoding="utf-8")
        result = install(existing)
        check("refuses to clobber pre-existing files", result.returncode == 3, result.stdout[-300:])
        check("and names them", ".github/skills/change/SKILL.md" in result.stdout)
        check(
            "nothing was written",
            not (existing / ".standards").exists(),
            "the installer wrote files despite stopping",
        )
        check(
            "adopter file untouched",
            (target / "SKILL.md").read_text(encoding="utf-8") == "# Our own change skill\n",
        )
        result = install(existing, "--replace-existing")
        check("--replace-existing proceeds", result.returncode == 0, result.stderr[-300:])
        check("and replaces the file", "Our own" not in (target / "SKILL.md").read_text(encoding="utf-8"))

        print("\nhook configuration collision safety")
        hooked_elsewhere = make_git_repo(tmp, "hooked-elsewhere")
        subprocess.run(
            ["git", "-C", str(hooked_elsewhere), "config", "core.hooksPath", ".husky/_"],
            check=True,
        )
        result = install(hooked_elsewhere)
        check("refuses to replace an existing hooks path", result.returncode == 4, result.stdout[-400:])
        check("and writes nothing", not (hooked_elsewhere / ".standards").exists())
        # ACT-025 / F35: the message must name the correct scope and give a real command, not a
        # description - the maintainer's own complaint, running this against a real repository.
        check(
            "a --local conflict is reported as --local, not misattributed to --worktree",
            "--local" in result.stdout and "--worktree" not in result.stdout,
            result.stdout[-800:],
        )
        check(
            "and the remove route is a real, scope-correct command",
            "git config --local --unset core.hooksPath" in result.stdout,
            result.stdout[-800:],
        )

        enclosing = make_repo(tmp, "enclosing")
        nested = enclosing / "nested"
        nested.mkdir()
        result = install(nested)
        check(
            "refuses a subdirectory of an enclosing repository",
            result.returncode == 2 and "not the root" in result.stderr,
            result.stderr[-300:],
        )
        check("and does not reconfigure the enclosing repository", not (nested / ".standards").exists())

        global_hooked = make_git_repo(tmp, "global-hooked")
        global_config = tmp / "global.gitconfig"
        global_config.write_text("[core]\n\thooksPath = .global-hooks\n", encoding="utf-8")
        isolated_env = {
            **os.environ,
            "GIT_CONFIG_GLOBAL": str(global_config),
            "GIT_CONFIG_NOSYSTEM": "1",
        }
        result = install(global_hooked, env=isolated_env)
        check(
            "refuses to override an effective global hooks path",
            result.returncode == 4,
            result.stdout[-400:],
        )
        check(
            "a --global conflict names its actual blast radius, not just its scope",
            "--global" in result.stdout and "every repository on this machine" in result.stdout,
            result.stdout[-800:],
        )
        check(
            "and the remove route is a real, scope-correct command",
            "git config --global --unset core.hooksPath" in result.stdout,
            result.stdout[-800:],
        )

        default_hooked = make_git_repo(tmp, "default-hooked")
        commit_msg_hook = default_hooked / ".git" / "hooks" / "commit-msg"
        commit_msg_hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        result = install(default_hooked)
        check(
            "refuses to disable a non-pre-commit default hook",
            result.returncode == 4,
            result.stdout[-400:],
        )
        check(
            "names the actual conflicting file and a real remove command for it",
            "commit-msg" in result.stdout and "rm $(git rev-parse --git-path hooks)/commit-msg" in result.stdout,
            result.stdout[-800:],
        )

        print("\nadditive layering")
        layered = make_repo(tmp, "layered")
        own = "# Our repository\n\nOur own guidance that must survive.\n"
        (layered / ".github").mkdir(parents=True)
        (layered / ".github/copilot-instructions.md").write_text(own, encoding="utf-8")
        install(layered)
        merged = (layered / ".github/copilot-instructions.md").read_text(encoding="utf-8")
        check("adopter instructions preserved verbatim", own.strip() in merged)
        check("standard block appended", merged.rstrip().endswith("END SURFACEPLATE -->"))

        print("\nconformance levels")
        levels = make_repo(tmp, "levels")
        install(levels)
        profile_path = levels / "governance" / "application-profile.yaml"
        essential_src = read_example("application-profile.essential.example.yaml")
        full_src = without_local_hook(
            read_example("application-profile.full.example.yaml")
        )

        # Each level's own worked example must pass at its own level.
        profile_path.write_text(essential_src, encoding="utf-8")
        seed_gate_artefacts(levels, essential_src)
        check("essential example passes at essential", verify(levels, "--no-grace").returncode == 0)
        profile_path.write_text(full_src, encoding="utf-8")
        seed_gate_artefacts(levels, full_src)
        check("full example passes at full", verify(levels, "--no-grace").returncode == 0)

        # Overclaiming must fail: an essential profile relabelled as a higher level has
        # not acquired the controls that level demands.
        for claimed, missing in (("standard", "deterministic_tests"), ("full", "provenance")):
            profile_path.write_text(
                essential_src.replace(
                    "conformance_level: essential", f"conformance_level: {claimed}"
                ),
                encoding="utf-8",
            )
            result = verify(levels, "--no-grace")
            check(
                f"essential profile claiming '{claimed}' is rejected",
                result.returncode == 1,
                result.stdout[-300:],
            )
            check(
                f"and names the missing control for '{claimed}'",
                missing in result.stdout and "SP021" in result.stdout,
            )

        # Underclaiming must be allowed: a level is a floor, not a ceiling.
        profile_path.write_text(
            full_src.replace("conformance_level: full", "conformance_level: essential"),
            encoding="utf-8",
        )
        check(
            "a full profile may declare a lower level (a level is a floor)",
            verify(levels, "--no-grace").returncode == 0,
        )

        # Present but not `required` is still an overclaim.
        downgraded = full_src.replace("conformance_level: full", "conformance_level: standard")
        downgraded = downgraded.replace(
            "  contract_tests:\n    decision: required", "  contract_tests:\n    decision: excluded"
        )
        profile_path.write_text(downgraded, encoding="utf-8")
        result = verify(levels, "--no-grace")
        check(
            "a required control decided otherwise is rejected",
            result.returncode == 1 and "SP022" in result.stdout,
            result.stdout[-300:],
        )

        # An unrecognised level must not silently pass.
        profile_path.write_text(
            essential_src.replace("conformance_level: essential", "conformance_level: gold"),
            encoding="utf-8",
        )
        result = verify(levels, "--no-grace")
        check("an unrecognised level is rejected", result.returncode == 1 and "SP017" in result.stdout)

        print("\nprofile review date")
        today = _dt.date.today()
        review = make_repo(tmp, "review")
        install(review)
        seed_gate_artefacts(review, essential_src)
        review_profile = review / "governance" / "application-profile.yaml"

        def set_review(value: str | None) -> None:
            if value is None:
                text = "\n".join(
                    line for line in essential_src.splitlines() if "review_by:" not in line
                ) + "\n"
            else:
                text = essential_src.replace('review_by: "2027-02-23"', f'review_by: "{value}"')
            review_profile.write_text(text, encoding="utf-8")

        set_review(None)
        result = verify(review, "--no-grace")
        check(
            "a profile with no review date is rejected",
            result.returncode == 1 and "SP024" in result.stdout,
            result.stdout[-300:],
        )

        set_review("23-02-2027")
        result = verify(review, "--no-grace")
        check(
            "an unreadable review date is rejected",
            result.returncode == 1 and "SP024" in result.stdout,
            result.stdout[-300:],
        )

        set_review((today - _dt.timedelta(days=1)).isoformat())
        result = verify(review, "--no-grace")
        check(
            "an overdue review date is rejected",
            result.returncode == 1 and "SP025" in result.stdout,
            result.stdout[-300:],
        )

        # The horizon cap is anti-gaming, so like the grace cap it is never graced:
        # this repository was installed today and is inside its grace window.
        set_review((today + _dt.timedelta(days=3650)).isoformat())
        result = verify(review)
        check(
            "a review date beyond the horizon is rejected even inside the grace window",
            result.returncode == 1 and "SP026" in result.stdout,
            result.stdout[-300:],
        )

        set_review((today + _dt.timedelta(days=10)).isoformat())
        result = verify(review, "--no-grace")
        check(
            "a review falling due soon warns without failing",
            result.returncode == 0 and "due for review" in result.stdout,
            result.stdout[-300:],
        )

        set_review((today + _dt.timedelta(days=180)).isoformat())
        result = verify(review, "--no-grace")
        check(
            "a live review date raises no review advisory",
            result.returncode == 0 and "due for review" not in result.stdout,
            result.stdout[-300:],
        )

        print("\nprerequisite gates - declaration")
        gates = make_repo(tmp, "gates")
        install(gates)
        gate_profile = gates / "governance" / "application-profile.yaml"
        seed_gate_artefacts(gates, essential_src)

        def gate_check(text: str) -> subprocess.CompletedProcess:
            gate_profile.write_text(text, encoding="utf-8")
            return verify(gates, "--no-grace")

        # The block itself is not optional. A repository that needs no gates must say so.
        without_block = essential_src[: essential_src.index("prerequisites:")] + "\n".join(
            essential_src[essential_src.index("human_roles:"):].splitlines()
        ) + "\n"
        result = gate_check(without_block)
        check(
            "a profile with no prerequisites block is rejected",
            result.returncode == 1 and "SP027" in result.stdout,
            result.stdout[-300:],
        )

        result = gate_check(essential_src.replace("- id: work_registration", "- id: invented_gate"))
        check(
            "a gate outside the catalogue is rejected",
            result.returncode == 1 and "SP028" in result.stdout,
            result.stdout[-300:],
        )
        check(
            "and the missing level-required gate is named",
            "SP029" in result.stdout and "work_registration" in result.stdout,
            result.stdout[-300:],
        )

        result = gate_check(
            essential_src.replace("- id: invented_gate", "- id: invented_gate")
            .replace("- id: work_registration", "- id: invented_gate\n    catalogue_id: custom")
        )
        check(
            "a custom gate is accepted when declared as custom",
            "SP028" not in result.stdout,
            result.stdout[-300:],
        )

        # A level is a floor. Demoting a gate the level requires is the same overclaim
        # as demoting a control the level requires.
        demoted = essential_src.replace(
            '- id: work_registration\n    status: required\n    effective_from: "2026-08-27"',
            "- id: work_registration\n    status: not_applicable\n    rationale: we would rather not",
        )
        result = gate_check(demoted)
        check(
            "a level-required gate decided otherwise is rejected",
            result.returncode == 1 and "SP030" in result.stdout,
            result.stdout[-300:],
        )

        result = gate_check(
            essential_src.replace(
                "    owner: Named Owner\n    revisit_by: \"2027-03-31\"", ""
            )
        )
        check(
            "a deferred gate with no owner or revisit date is rejected",
            result.returncode == 1 and "SP031" in result.stdout,
            result.stdout[-300:],
        )

        result = gate_check(
            essential_src.replace("artefacts: [docs/DEVELOPMENT_REGISTER.md]", "artefacts: [docs/NOWHERE.md]")
        )
        check(
            "a gate naming a missing precondition artefact is rejected",
            result.returncode == 1 and "SP032" in result.stdout,
            result.stdout[-300:],
        )

        # An empty or still-templated artefact satisfies a path check and no one else.
        #
        # F14 / DR-17 pin BOTH directions here. DR-17 removed a shape-based branch from
        # PLACEHOLDER_PATTERN that matched any `<lowercase-token>`, because it could not
        # separate an unfilled slot from a metavariable and failed on this framework's own
        # normative documents. Removing a branch is only safe if what remains still fires, so
        # the positive cases below are the guard on that, and the negative case is the guard
        # against the branch being reinstated without evidence.
        for label, body in (
            ("a replace-me token", "# Register\n\nowner: replace-me\n"),
            ("a TODO marker", "# Register\n\nowner: A. Person\n\nTODO: name the deputy\n"),
            ("a TBD marker", "# Register\n\nowner: TBD\n"),
            ("a TBC marker", "# Register\n\nowner: A. Person\n\nreviewer: TBC\n"),
        ):
            (gates / "docs" / "DEVELOPMENT_REGISTER.md").write_text(body, encoding="utf-8")
            result = gate_check(essential_src)
            check(
                f"a precondition artefact carrying {label} is rejected",
                result.returncode == 1 and "SP032" in result.stdout,
                result.stdout[-300:],
            )

        # The negative direction. Every line below is a real occurrence taken from this
        # repository's own documents, each of which SP032 used to fail on: a numbering
        # convention, a CLI usage line, and a command template from core/PREREQUISITE_GATES.md
        # itself. A complete artefact that documents syntax is not an unfinished one.
        (gates / "docs" / "DEVELOPMENT_REGISTER.md").write_text(
            "# Register\n\n"
            "Records are numbered `DR-<n>`, sequential, never reused.\n\n"
            "Usage: python scripts/verify_release.py <path-to-zip>\n\n"
            "The audit runs `git log --since=<effective_from>` over the gated paths.\n",
            encoding="utf-8",
        )
        result = gate_check(essential_src)
        check(
            "a precondition artefact using angle-bracket notation is NOT rejected",
            "SP032" not in result.stdout,
            result.stdout[-400:],
        )

        (gates / "docs" / "DEVELOPMENT_REGISTER.md").write_text(
            "# Register\n\nReal content.\n", encoding="utf-8"
        )

        # ---- SP051 / SP052: pattern A and pattern D (DR-25) ----
        #
        # Both directions for each. A control that names a file is only verified if the file is
        # really there - the four failure modes below are the ways "really there" can be false
        # while the declaration looks identical.
        for label, mutate in (
            ("names nothing to check",
             lambda s: s.replace("    implementation_reference: requirements.txt\n", "")),
            ("names a file that does not exist",
             lambda s: s.replace("implementation_reference: requirements.txt",
                                 "implementation_reference: docs/NOWHERE.txt")),
        ):
            result = gate_check(mutate(essential_src))
            check(
                f"a required control that {label} is rejected",
                result.returncode == 1 and "SP051" in result.stdout,
                result.stdout[-300:],
            )

        (gates / "requirements.txt").write_text("", encoding="utf-8")
        result = gate_check(essential_src)
        check(
            "a required control naming an empty file is rejected",
            result.returncode == 1 and "SP051" in result.stdout,
            result.stdout[-300:],
        )
        (gates / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(gates), "add", "--", "requirements.txt"],
                       capture_output=True)

        # Pattern D: the control is verified BY the gate, so requiring it without the gate
        # leaves it verified by nothing - the seam a level being a floor rather than a ceiling
        # opens up.
        with_control = essential_src.replace(
            "control_decisions:\n",
            "control_decisions:\n  documentation_authority:\n    decision: required\n"
            "    rationale: Probe.\n", 1)
        result = gate_check(with_control)
        check(
            "documentation_authority required without its gate is rejected",
            result.returncode == 1 and "SP052" in result.stdout,
            result.stdout[-300:],
        )

        # The negative direction for both, without which the four assertions above would be
        # equally consistent with a check that fires on everything.
        result = gate_check(essential_src)
        check(
            "a correctly referenced control raises neither SP051 nor SP052",
            "SP051" not in result.stdout and "SP052" not in result.stdout,
            result.stdout[-400:],
        )

        # ---- SP054: a deferral expires on the date its author gave it (F22) ----
        #
        # The negative case is the one that matters. A check firing on every deferral would pass
        # the "expired date fails" test identically, so the future-dated case is what separates
        # a working check from one that simply always fires.
        deferred_src = essential_src.replace(
            "  work_contract:\n    status: deferred",
            "  work_contract:\n    status: deferred", 1)
        for label, date, expect in (
            ("expired", "2020-01-01", True),
            ("unreadable", "not-a-date", True),
            ("far future", "2099-01-01", False),
        ):
            probe = re.sub(r'revisit_by: "?[^"\n]+"?', f'revisit_by: "{date}"', deferred_src)
            result = gate_check(probe)
            check(
                f"a deferral dated {label} {'raises' if expect else 'does not raise'} SP054",
                ("SP054" in result.stdout) is expect,
                result.stdout[-300:],
            )

        # ---- SP053: pattern B (DR-25, amended to step granularity) ----
        #
        # A test step that cannot fail is the failure this mechanism exists for: a suite can run,
        # report success and leave the job green while it failed, if the exit code is discarded.
        # Observed in this project's own history with a scanner, not a hypothesis.
        # Seeded for the FULL profile, which declares gates and steps the essential fixture does
        # not have. Without this the probes below fail on missing gate artefacts rather than on
        # the thing they are testing.
        full_b = read_example("application-profile.full.example.yaml")
        seed_gate_artefacts(gates, full_b)

        for label, mutate in (
            ("names no CI step",
             lambda s: s.replace("    implementation_reference: Run the contract tests\n", "")),
            ("names a step that does not exist",
             lambda s: s.replace("implementation_reference: Run the contract tests",
                                 "implementation_reference: No Such Step")),
        ):
            result = gate_check(mutate(full_b))
            check(
                f"a pattern B control that {label} is rejected",
                "SP053" in result.stdout,
                result.stdout[-300:],
            )

        # The negative direction, without which the two above are consistent with a check that
        # fires on every profile.
        result = gate_check(full_b)
        check(
            "a correctly referenced CI step raises no SP053",
            "SP053" not in result.stdout,
            result.stdout[-400:],
        )

        # ---- SP055 / SP056: pattern C, the record registers (DR-26, closes F20) ----
        #
        # The full example declares all four record-based controls, and seed_gate_artefacts has
        # already created their registers - one holding a real override record, the rest empty.
        # Both states must pass, and that pair is the whole point: an empty register passing is a
        # DECISION, because a validator that demanded records would reward inventing them.
        overrides_dir = gates / "governance" / "overrides"
        runs_dir = gates / "governance" / "run-lineage"

        result = gate_check(full_b)
        check(
            "a populated register passes and reports its record count",
            "SP055" not in result.stdout and "SP056" not in result.stdout
            and "overrides: verified against governance/overrides (1 record(s)" in result.stdout,
            result.stdout[-500:],
        )
        # The empty register, proved in ISOLATION rather than inside the full example - every
        # register there now holds a worked record, and one control declared alone is the only
        # arrangement in which "empty" cannot be confused with "its cross-references resolved".
        (gates / "governance" / "empty-register").mkdir(parents=True, exist_ok=True)
        lone_register = essential_src.replace(
            "control_decisions:\n",
            "control_decisions:\n  method_registry:\n    decision: required\n"
            "    implementation_reference: governance/empty-register\n"
            "    rationale: Probe.\n", 1)
        empty_result = gate_check(lone_register)
        check(
            "an EMPTY register passes, and says what that does and does not establish",
            "SP055" not in empty_result.stdout and "SP056" not in empty_result.stdout
            and "method_registry: verified against governance/empty-register (register is empty"
            in empty_result.stdout,
            empty_result.stdout[-500:],
        )
        check(
            "a README beside a record is not read as a malformed record",
            (overrides_dir / "README.md").is_file() and "SP056" not in result.stdout,
            result.stdout[-300:],
        )

        for label, mutate in (
            ("names no register",
             lambda s: s.replace(
                 "    implementation_reference: governance/method-registry\n", "")),
            ("names a register that does not exist",
             lambda s: s.replace("implementation_reference: governance/method-registry",
                                 "implementation_reference: governance/no-such-register")),
            ("names a file where a register belongs",
             lambda s: s.replace("implementation_reference: governance/method-registry",
                                 "implementation_reference: README.md")),
        ):
            result = gate_check(mutate(full_b))
            check(
                f"a pattern C control that {label} is rejected",
                "SP055" in result.stdout,
                result.stdout[-300:],
            )

        # The untracked-record case cannot be probed here: this fixture has only a fake .git
        # directory, so git_available() is false and the tracking branch never runs. It is
        # exercised against a real repository further down, beside the full worked example.

        for label, name, body in (
            ("unreadable", "broken.yaml", "a: [1\n"),
            ("invalid against its schema", "thin.yaml", "schema_version: '1.0'\n"),
        ):
            probe = overrides_dir / name
            probe.write_text(body, encoding="utf-8")
            subprocess.run(["git", "-C", str(gates), "add", "--",
                            f"governance/overrides/{name}"], capture_output=True)
            result = gate_check(full_b)
            check(
                f"a record that is {label} is rejected",
                "SP056" in result.stdout,
                result.stdout[-300:],
            )
            subprocess.run(["git", "-C", str(gates), "rm", "-q", "--cached", "--",
                            f"governance/overrides/{name}"], capture_output=True)
            probe.unlink()

        # A VALID record of the WRONG type. This is the case that distinguishes pattern C from a
        # check that merely counts files: the record below is a perfectly good override record,
        # and it is a defect because it is filed in the run-lineage register.
        misfiled = runs_dir / "misfiled.yaml"
        misfiled.write_text(
            read_example("override-record.approved.example.yaml"), encoding="utf-8")
        subprocess.run(["git", "-C", str(gates), "add", "--",
                        "governance/run-lineage/misfiled.yaml"], capture_output=True)
        result = gate_check(full_b)
        check(
            "a valid record filed in the wrong register is rejected",
            "SP056" in result.stdout and "run_lineage" in result.stdout,
            result.stdout[-400:],
        )
        subprocess.run(["git", "-C", str(gates), "rm", "-q", "--cached", "--",
                        "governance/run-lineage/misfiled.yaml"], capture_output=True)
        misfiled.unlink()

        # ---- SP057 / SP058: pattern C2, records must reference what they describe (DR-27) ----
        #
        # A schema sees one record at a time, so a run naming a method nobody registered and an
        # override naming a run that never happened both validate perfectly. These are the checks
        # that read the register as a whole.
        #
        # The three seeded records are ONE CONSISTENT SET - the override names RUN-2026-000412,
        # the run names METHOD-SEASONALITY-001 at 2.3.0 and carries OVR-20260001 back - so each
        # probe below breaks exactly one edge and restores it.
        run_record = gates / "governance" / "run-lineage" / "method-run-lineage.example.yaml"
        method_record = (
            gates / "governance" / "method-registry" / "method-registry-entry.example.yaml"
        )
        override_record = (
            gates / "governance" / "overrides" / "override-record.approved.example.yaml"
        )
        run_src = run_record.read_text(encoding="utf-8")
        method_src = method_record.read_text(encoding="utf-8")
        override_src = override_record.read_text(encoding="utf-8")

        result = gate_check(full_b)
        check(
            "the three worked records reference each other and pass",
            "SP057" not in result.stdout and "SP058" not in result.stdout
            and "record cross-references: 3 resolved" in result.stdout,
            result.stdout[-500:],
        )

        for label, target, before, after in (
            ("a method that is not registered at all", run_record,
             "method_id: METHOD-SEASONALITY-001", "method_id: METHOD-NEVER-REGISTERED"),
            ("a registered method at an unregistered version", run_record,
             'method_version: "2.3.0"', 'method_version: "9.9.9"'),
            ("an override nobody recorded", run_record,
             "  - OVR-20260001", "  - OVR-99999999"),
            ("a run that never happened", override_record,
             "method_run_id: RUN-2026-000412", "method_run_id: RUN-2026-999999"),
        ):
            target.write_text(
                (run_src if target is run_record else override_src).replace(before, after, 1),
                encoding="utf-8")
            result = gate_check(full_b)
            check(
                f"a record referencing {label} is rejected",
                "SP057" in result.stdout,
                result.stdout[-400:],
            )
            target.write_text(
                run_src if target is run_record else override_src, encoding="utf-8")

        # The version half of the method reference, asserted separately because matching on the
        # id alone would have passed the second probe above and looked identical here.
        result = gate_check(full_b)
        check(
            "and the restored set resolves again",
            "SP057" not in result.stdout,
            result.stdout[-300:],
        )

        # SP058: two records under one identity means every reference to it resolves to whichever
        # was read last - the reference checks above become meaningless rather than wrong.
        twin = gates / "governance" / "overrides" / "twin.yaml"
        twin.write_text(override_src, encoding="utf-8")
        subprocess.run(["git", "-C", str(gates), "add", "--",
                        "governance/overrides/twin.yaml"], capture_output=True)
        result = gate_check(full_b)
        check(
            "two records claiming one identity are rejected",
            "SP058" in result.stdout,
            result.stdout[-400:],
        )
        twin.write_text(
            override_src.replace("application_id: example-forecast-service",
                                 "application_id: some-other-application", 1)
            .replace("override_id: OVR-20260001", "override_id: OVR-20260002", 1),
            encoding="utf-8")
        result = gate_check(full_b)
        check(
            "a record belonging to another application is rejected",
            "SP058" in result.stdout,
            result.stdout[-400:],
        )
        subprocess.run(["git", "-C", str(gates), "rm", "-q", "--cached", "--",
                        "governance/overrides/twin.yaml"], capture_output=True)
        twin.unlink()

        # NEGATIVE CONTROL 1 - the conditionality. The same dangling reference must raise nothing
        # when the register it points into is not declared, because obliging otherwise would make
        # declaring one control silently require another.
        run_record.write_text(
            run_src.replace("method_id: METHOD-SEASONALITY-001",
                            "method_id: METHOD-NEVER-REGISTERED", 1), encoding="utf-8")
        undeclared = full_b.replace(
            "  method_registry:\n    decision: required\n"
            "    implementation_reference: governance/method-registry\n", "")
        result = gate_check(undeclared)
        check(
            "a dangling reference into an undeclared register raises nothing",
            "SP057" not in result.stdout,
            result.stdout[-400:],
        )
        check(
            "and the run says its references were not checked rather than staying silent",
            "were not checked" in result.stdout,
            result.stdout[-500:],
        )
        run_record.write_text(run_src, encoding="utf-8")

        # NEGATIVE CONTROL 2 - no cascade. A record that failed its schema is excluded from the
        # index, so one SP056 does not become a spray of SP057s about references that nothing was
        # ever in a position to resolve.
        method_record.write_text("schema_version: '1.0'\n", encoding="utf-8")
        result = gate_check(full_b)
        check(
            "a schema-invalid record raises SP056 without an SP057 cascade",
            "SP056" in result.stdout and "SP057" not in result.stdout,
            result.stdout[-500:],
        )
        method_record.write_text(method_src, encoding="utf-8")

        # ---- F20 / DR-25: a pass must not read as verification ----
        #
        # The checker reports which of a level's required controls are declared rather than
        # checked. Both directions are pinned: the warning must appear while controls are
        # unverified, and must NOT name a control that is genuinely checked - otherwise it
        # would still be reporting after the verification exists, which is the same defect
        # pointed the other way.
        # At `essential` the only required control is dependency_lock, which pattern A now
        # verifies - so the banner must NOT print. That is the negative direction, and it only
        # became testable once a control was genuinely checked.
        result = gate_check(essential_src)
        check(
            "no declared-not-checked banner when every required control is verified",
            "DECLARED, not checked" not in result.stdout,
            result.stdout[:400],
        )

        # The assertion that USED to sit here - "a level with unverified controls still reports
        # them" - was deleted when pattern C landed (ACT-014), and deleted rather than relocated
        # because there is no level left for it to be true of. Every control at every level is
        # now verified, so the banner cannot fire.
        #
        # Recorded here rather than silently dropped, because that leaves the banner as LATENT
        # code: a mechanism that claims to warn, which nothing now proves still works. It is kept
        # for the next control added ahead of its validator, and DR-26 records it as an open
        # limitation. Restoring an assertion for it would mean manufacturing a fake unverified
        # level, which tests the fixture rather than the framework.
        #
        # The positive direction below stays, and is now the stronger claim: at `full` - every
        # control this framework defines - the banner is silent because all of them are checked.
        result = gate_check(essential_src.replace(
            "conformance_level: essential", "conformance_level: full"))
        check(
            "no declared-not-checked banner at full: every control is now verified",
            "DECLARED, not checked" not in result.stdout,
            result.stdout[:400],
        )

        # ---- placeholder-scan exemptions: F16 / DR-22, and SP050 ----
        #
        # The exemption must be NARROW. Three of the four cases below exist to prove what it
        # does not suppress; only one proves what it does. An exemption that quietly disabled
        # the existence or non-emptiness checks would be the hole SP032 exists to close.
        (gates / "docs" / "DEVELOPMENT_REGISTER.md").write_text(
            "# Register\n\nowner: replace-me\n", encoding="utf-8"
        )
        exempted = essential_src.rstrip("\n") + (
            "\nplaceholder_scan_exemptions:\n"
            "  - artefact: docs/DEVELOPMENT_REGISTER.md\n"
            "    rationale: Documents the placeholder tokens themselves.\n"
        )
        result = gate_check(exempted)
        check(
            "a declared exemption suppresses the placeholder finding",
            "SP032" not in result.stdout,
            result.stdout[-400:],
        )
        check(
            "and the run says the control was narrowed, rather than staying silent",
            "exempt from the placeholder scan" in result.stdout,
            result.stdout[-400:],
        )

        (gates / "docs" / "DEVELOPMENT_REGISTER.md").write_text("", encoding="utf-8")
        result = gate_check(exempted)
        check(
            "an exemption does NOT suppress the empty-artefact finding",
            result.returncode == 1 and "SP032" in result.stdout,
            result.stdout[-300:],
        )
        (gates / "docs" / "DEVELOPMENT_REGISTER.md").write_text(
            "# Register\n\nReal content.\n", encoding="utf-8"
        )

        stale = essential_src.rstrip("\n") + (
            "\nplaceholder_scan_exemptions:\n"
            "  - artefact: docs/NEVER_EXISTED.md\n"
            "    rationale: Probe.\n"
        )
        result = gate_check(stale)
        check(
            "an exemption naming an artefact that does not exist is rejected",
            result.returncode == 1 and "SP050" in result.stdout,
            result.stdout[-300:],
        )

        # ---- F25: the exemption's own rationale may quote what it describes ----
        #
        # An exemption must state WHY an artefact legitimately carries a placeholder token, which
        # means quoting it - and SP020 scanned every string in the profile, so declaring the
        # exemption failed the profile. The remedy for the defect could not be used without
        # causing it. Found in Plyego, unreachable from here: this repository's own exemptions
        # describe the tokens without reproducing them, so the trap was invisible from inside.
        (gates / "docs" / "DEVELOPMENT_REGISTER.md").write_text(
            "# Register\n\n| ACT-395 | field was always 'tbd' - RESOLVED | Closed |\n",
            encoding="utf-8",
        )
        quoting = essential_src.rstrip("\n") + (
            "\nplaceholder_scan_exemptions:\n"
            "  - artefact: docs/DEVELOPMENT_REGISTER.md\n"
            "    rationale: >-\n"
            "      ACT-395's title quotes the string 'tbd' because the defect it records WAS a\n"
            "      field containing that literal. The register is live work items, not a template.\n"
        )
        result = gate_check(quoting)
        check(
            "an exemption whose rationale quotes the token does not fail the profile",
            "SP020" not in result.stdout and "SP032" not in result.stdout,
            result.stdout[-500:],
        )

        # The three negative controls. An exclusion that swallowed the whole profile - or any
        # rationale anywhere in it - would pass the case above identically.
        for label, mutate in (
            ("a top-level field", lambda s: s.replace("owner: Named Owner", "owner: TODO")),
            ("a string inside a gate",
             lambda s: s.replace(
                 "description: Implementation work in the application source tree.",
                 "description: Implementation work in the application source tree. Scope TBD.")),
            ("a deferral's rationale",
             lambda s: s.replace("      rationale: >-\n", "      rationale: TODO - decide later\n",
                                 1)),
        ):
            probe = mutate(quoting)
            if probe == quoting:
                continue  # the fixture did not contain the shape; the other two still bind
            result = gate_check(probe)
            check(
                f"the profile scan still fires on {label}",
                "SP020" in result.stdout,
                result.stdout[-400:],
            )

        # ---- F26: SP032's remedy names the route out ----
        #
        # It read "A template is not a design policy" for every one of the nineteen gates, and
        # named no remedy at all - so an adopter meeting a legitimate mention had nothing to act
        # on, which is exactly what happened in Plyego.
        result = gate_check(essential_src)
        check(
            "SP032's placeholder remedy names the exemption route",
            "SP032" in result.stdout
            and "placeholder_scan_exemptions" in result.stdout
            and "design policy" not in result.stdout,
            result.stdout[-500:],
        )
        (gates / "docs" / "DEVELOPMENT_REGISTER.md").write_text(
            "# Register\n\nReal content.\n", encoding="utf-8"
        )

        # ---- the declared pin: SP048 and SP049 (DR-14, closing F7) ----
        #
        # Before these, adoption.framework_digest was shape-checked against 64 hex characters
        # and nothing else, while its name and description made it read as a verified pin. The
        # finding was not that a check was missing but that its absence was invisible.
        result = gate_check(
            essential_src.replace(f"framework_version: {FIXTURE_VERSION}", "framework_version: 0.0.1")
        )
        check(
            "a profile naming a version it was not installed from is rejected",
            result.returncode == 1 and "SP048" in result.stdout,
            result.stdout[-300:],
        )

        # Deliberately starts with a letter: a 64-character run of digits is parsed by YAML as
        # the integer 0, which fails the schema (SP016) before this check is ever reached.
        wrong_digest = "a" * 64
        result = gate_check(
            essential_src.replace(f"framework_digest: {FIXTURE_ANCHOR}", f"framework_digest: {wrong_digest}")
        )
        check(
            "a profile whose framework digest does not match the install record is rejected",
            result.returncode == 1 and "SP049" in result.stdout,
            result.stdout[-300:],
        )

        # An install record with no anchor must not read the same as one that matched. This is
        # the case an adopter hits after upgrading from an installer that predates DR-14.
        gate_record_path = gates / ".standards" / "INSTALL.json"
        gate_record = json.loads(gate_record_path.read_text(encoding="utf-8"))
        saved_anchor = gate_record.pop("framework_digest", None)
        gate_record_path.write_text(json.dumps(gate_record, indent=2), encoding="utf-8")
        result = gate_check(essential_src)
        check(
            "a declared digest with nothing to compare against is reported, not passed over",
            result.returncode == 1 and "SP049" in result.stdout,
            result.stdout[-300:],
        )
        gate_record["framework_digest"] = saved_anchor
        gate_record_path.write_text(json.dumps(gate_record, indent=2), encoding="utf-8")

        # The negative direction. Without it, three passing assertions would be equally
        # consistent with a check that fires on every profile.
        result = gate_check(essential_src)
        check(
            "a profile whose pin matches the install record raises neither SP048 nor SP049",
            "SP048" not in result.stdout and "SP049" not in result.stdout,
            result.stdout[-400:],
        )

        # ---- secret_hygiene: SP046 and SP047 (DR-18) ----
        #
        # Both directions pinned. This control is unusually good at looking fine while doing
        # nothing: in every failing case below the workflow is valid YAML, the scanner is
        # installed, and the job is green. That is the whole point of it, so a test suite
        # that only ever showed it passing would establish nothing.
        import yaml as _yaml

        scan_workflow = gates / ".github" / "workflows" / "secret-scan.yml"
        wired_workflow = scan_workflow.read_text(encoding="utf-8")

        def profile_with(mutate) -> str:
            data = _yaml.safe_load(essential_src)
            mutate(data["baseline_controls"]["secret_hygiene"])
            return _yaml.safe_dump(data, sort_keys=False)

        result = gate_check(profile_with(lambda h: h.pop("scanner", None)))
        check(
            "secret_hygiene declared with no scanner is rejected",
            result.returncode == 1 and "SP046" in result.stdout,
            result.stdout[-300:],
        )

        result = gate_check(
            profile_with(lambda h: h["scanner"].update({"wired_in": [".github/workflows/absent.yml"]}))
        )
        check(
            "a scanner wired to a file that does not exist is rejected",
            result.returncode == 1 and "SP046" in result.stdout,
            result.stdout[-300:],
        )

        # Present, valid, and mentions the scanner - but no step runs it. A mention in a
        # comment is not an invocation, and this is the case a naive grep would pass.
        scan_workflow.write_text(
            "name: Secret scan\n"
            "# TODO one day: wire gitleaks in here\n"
            "on: [push]\n"
            "jobs:\n"
            "  noop:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - run: echo nothing\n",
            encoding="utf-8",
        )
        result = gate_check(essential_src)
        check(
            "a workflow that names the scanner but never runs it is rejected",
            result.returncode == 1 and "SP046" in result.stdout,
            result.stdout[-300:],
        )

        scan_workflow.write_text(
            wired_workflow.replace(
                "      - name: Run gitleaks\n",
                "      - name: Run gitleaks\n        continue-on-error: true\n",
            ),
            encoding="utf-8",
        )
        result = gate_check(essential_src)
        check(
            "a scan step with continue-on-error is rejected",
            result.returncode == 1 and "SP047" in result.stdout,
            result.stdout[-300:],
        )

        # The observed failure this control exists for: the scanner runs, the report says
        # findings, and the exit code never reaches the job.
        scan_workflow.write_text(
            wired_workflow.replace(
                "        run: gitleaks detect --exit-code 1\n",
                "        run: gitleaks detect --exit-code 1 || true\n",
            ),
            encoding="utf-8",
        )
        result = gate_check(essential_src)
        check(
            "a scan command that discards its exit code is rejected",
            result.returncode == 1 and "SP047" in result.stdout,
            result.stdout[-300:],
        )

        # The negative direction: a correctly wired scanner raises neither code. Without
        # this, every assertion above would still pass if the control fired unconditionally.
        scan_workflow.write_text(wired_workflow, encoding="utf-8")
        result = gate_check(essential_src)
        check(
            "a correctly wired scanner raises neither SP046 nor SP047",
            "SP046" not in result.stdout and "SP047" not in result.stdout,
            result.stdout[-400:],
        )

        result = gate_check(
            essential_src.replace(
                '- id: work_registration\n    status: required\n    effective_from: "2026-08-27"',
                "- id: work_registration\n    status: required",
            )
        )
        check(
            "a required gate with no effective date is rejected",
            result.returncode == 1 and "SP033" in result.stdout,
            result.stdout[-300:],
        )

        future = (today + _dt.timedelta(days=30)).isoformat()
        result = gate_check(
            essential_src.replace('effective_from: "2026-08-27"', f'effective_from: "{future}"', 1)
        )
        check(
            "a gate dated in the future is rejected as a disguised deferral",
            result.returncode == 1 and "SP033" in result.stdout,
            result.stdout[-300:],
        )

        # `standard` and `full` demand a decision on every catalogue gate.
        result = gate_check(
            essential_src.replace("conformance_level: essential", "conformance_level: standard")
        )
        check(
            "an incompletely declared catalogue is rejected at 'standard'",
            result.returncode == 1 and "SP029" in result.stdout,
            result.stdout[-300:],
        )

        # Where history cannot be read the check must say so rather than imply a pass.
        no_history = make_unusable_git_repo(tmp, "no-history")
        result = run(
            [str(PAYLOAD / "check_conformance.py"), "--repo", str(no_history)]
        )
        check(
            "an unusable Git directory is reported as not installed",
            result.returncode == 1 and "SP001" in result.stdout,
            result.stdout[-300:],
        )
        # Enumerated rather than derived, and it drifted the moment the installer gained new
        # destinations (DR-30 added .claude/rules/ and AGENTS.md). Kept explicit because this
        # fixture is deliberately NOT an install - it reconstructs one in a tree git cannot read -
        # but the list has to track what an install actually produces.
        shutil.copytree(repo / ".standards", no_history / ".standards")
        shutil.copytree(repo / ".github", no_history / ".github")
        shutil.copytree(repo / ".githooks", no_history / ".githooks")
        shutil.copytree(repo / ".claude", no_history / ".claude")
        shutil.copyfile(repo / "AGENTS.md", no_history / "AGENTS.md")
        (no_history / "governance").mkdir(parents=True)
        no_history_profile = no_history / "governance" / "application-profile.yaml"
        no_history_profile.write_text(essential_src, encoding="utf-8")
        seed_gate_artefacts(no_history, essential_src)
        result = verify(no_history, "--no-grace")
        check(
            "a passing repository without git history says the audit did not run",
            result.returncode == 0 and "absence of evidence" in result.stdout,
            result.stdout[-400:],
        )

        print("\nprerequisite gates - the interface floor")
        # A repository that builds screens cannot defer deciding how it builds them.
        standard_ui = essential_src.replace(
            "conformance_level: essential", "conformance_level: standard"
        )
        result = gate_check(standard_ui)
        check(
            "a UI repository at 'standard' must have the interface gates required",
            result.returncode == 1
            and "SP029" in result.stdout
            and "component_library" in result.stdout,
            result.stdout[-500:],
        )

        result = gate_check(
            standard_ui.replace("builds_user_interface: true", "builds_user_interface: false")
        )
        check(
            "declaring no UI while requiring an interface gate is contradictory",
            result.returncode == 1 and "SP037" in result.stdout,
            result.stdout[-500:],
        )

        result = gate_check(
            standard_ui.replace(
                "builds_user_interface: true\n", ""
            )
        )
        check(
            "a 'standard' profile that does not answer the UI question is rejected",
            result.returncode == 1 and "SP037" in result.stdout,
            result.stdout[-500:],
        )

        # not_applicable is the escape hatch, and it must not be available to a UI repo.
        result = gate_check(
            essential_src.replace(
                '  - id: design_authority\n    status: required\n    effective_from: "2026-08-27"',
                "  - id: design_authority\n    status: not_applicable\n"
                "    rationale: we would rather not think about it",
            )
        )
        check(
            "an interface gate cannot be not_applicable in a repository that builds a UI",
            result.returncode == 1 and "SP037" in result.stdout,
            result.stdout[-500:],
        )

        # The full example is the opposite case and must stay clean.
        result = gate_check(full_src)
        check(
            "a headless repository may decide all four interface gates not_applicable",
            "SP037" not in result.stdout,
            result.stdout[-500:],
        )

        print("\nprerequisite gates - pre-commit hook")
        pre_commit = make_git_repo(tmp, "pre-commit")
        install(pre_commit)
        hook_path = subprocess.run(
            ["git", "-C", str(pre_commit), "config", "--local", "--get", "core.hooksPath"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        check("the installer activates core.hooksPath", hook_path == ".githooks", hook_path)
        hook_src = essential_src.replace(
            "enforcement: [history_audit, review]",
            "enforcement: [history_audit, local_hook, review]",
            1,
        ).replace('paths: ["src/**"]', 'paths: ["src"]', 1)
        (pre_commit / "governance" / "application-profile.yaml").write_text(
            hook_src, encoding="utf-8"
        )
        seed_gate_artefacts(pre_commit, hook_src)
        subprocess.run(["git", "-C", str(pre_commit), "add", "-A"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(pre_commit),
                "update-index",
                "--chmod=+x",
                ".githooks/pre-commit",
            ],
            check=True,
        )
        hook_mode = subprocess.run(
            ["git", "-C", str(pre_commit), "ls-files", "--stage", "--", ".githooks/pre-commit"],
            capture_output=True,
            text=True,
        ).stdout.split()[0]
        check("the hook is staged as executable for portable clones", hook_mode == "100755", hook_mode)
        result = subprocess.run(
            ["git", "-C", str(pre_commit), "commit", "-m", "adopt with local hook"],
            capture_output=True,
            text=True,
        )
        check("a conformant staged snapshot passes the hook", result.returncode == 0, result.stdout[-500:])

        register = pre_commit / "docs" / "DEVELOPMENT_REGISTER.md"
        register.unlink()
        (pre_commit / "src").mkdir(exist_ok=True)
        (pre_commit / "src" / "blocked.py").write_text("# gated work\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(pre_commit), "add", "-A"], check=True)
        result = subprocess.run(
            ["git", "-C", str(pre_commit), "commit", "-m", "cross gate"],
            capture_output=True,
            text=True,
        )
        hook_output = result.stdout + result.stderr
        check(
            "the hook blocks a staged gate crossing without its precondition",
            result.returncode != 0 and "SP039" in hook_output,
            hook_output[-700:],
        )
        check(
            "the hook uses Git pathspec semantics for directory paths",
            "src/blocked.py" in hook_output,
            hook_output[-700:],
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(pre_commit),
                "restore",
                "--staged",
                "docs/DEVELOPMENT_REGISTER.md",
                "src/blocked.py",
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(pre_commit), "restore", "docs/DEVELOPMENT_REGISTER.md"],
            check=True,
        )
        (pre_commit / "src" / "blocked.py").unlink()

        checker = pre_commit / ".standards" / "check_conformance.py"
        checker_text = checker.read_text(encoding="utf-8")
        checker.write_text(checker_text + "\n# staged tamper\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(pre_commit), "add", ".standards/check_conformance.py"],
            check=True,
        )
        checker.write_text(checker_text, encoding="utf-8")
        result = subprocess.run(
            ["git", "-C", str(pre_commit), "commit", "-m", "stage tampered checker"],
            capture_output=True,
            text=True,
        )
        hook_output = result.stdout + result.stderr
        check(
            "the hook rejects staged control tampering hidden by a valid working tree",
            result.returncode != 0 and "SP040" in hook_output,
            hook_output[-700:],
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(pre_commit),
                "restore",
                "--staged",
                ".standards/check_conformance.py",
            ],
            check=True,
        )

        profile = pre_commit / "governance" / "application-profile.yaml"
        profile_text = profile.read_text(encoding="utf-8")
        profile.write_text("not: [valid\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(pre_commit), "add", "governance/application-profile.yaml"],
            check=True,
        )
        profile.write_text(profile_text, encoding="utf-8")
        result = subprocess.run(
            ["git", "-C", str(pre_commit), "commit", "-m", "stage malformed profile"],
            capture_output=True,
            text=True,
        )
        hook_output = result.stdout + result.stderr
        check(
            "the hook rejects a malformed staged profile instead of using the working tree",
            result.returncode != 0 and "SP041" in hook_output,
            hook_output[-700:],
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(pre_commit),
                "restore",
                "--staged",
                "governance/application-profile.yaml",
            ],
            check=True,
        )

        subprocess.run(
            [
                "git",
                "-C",
                str(pre_commit),
                "rm",
                "--cached",
                "docs/DEVELOPMENT_REGISTER.md",
            ],
            check=True,
            capture_output=True,
        )
        result = subprocess.run(
            ["git", "-C", str(pre_commit), "commit", "-m", "remove staged prerequisite"],
            capture_output=True,
            text=True,
        )
        hook_output = result.stdout + result.stderr
        check(
            "the hook sees a staged prerequisite deletion hidden by a working copy",
            result.returncode != 0 and "SP032" in hook_output,
            hook_output[-700:],
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(pre_commit),
                "restore",
                "--staged",
                "docs/DEVELOPMENT_REGISTER.md",
            ],
            check=True,
        )

        profile.write_text("not: [valid\n", encoding="utf-8")
        (pre_commit / "docs" / "staged-profile-test.md").write_text(
            "# Valid staged snapshot\n", encoding="utf-8"
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(pre_commit),
                "add",
                "docs/staged-profile-test.md",
            ],
            check=True,
        )
        result = subprocess.run(
            ["git", "-C", str(pre_commit), "commit", "-m", "commit valid staged snapshot"],
            capture_output=True,
            text=True,
        )
        hook_output = result.stdout + result.stderr
        check(
            "an invalid unstaged profile does not reject a valid staged snapshot",
            result.returncode == 0,
            hook_output[-700:],
        )
        profile.write_text(profile_text, encoding="utf-8")

        invalid_pathspec_profile = profile_text.replace(
            'paths: ["src"]',
            'paths: ["../outside"]',
            1,
        )
        profile.write_text(invalid_pathspec_profile, encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(pre_commit), "add", "governance/application-profile.yaml"],
            check=True,
        )
        result = subprocess.run(
            ["git", "-C", str(pre_commit), "commit", "-m", "stage invalid pathspec"],
            capture_output=True,
            text=True,
        )
        hook_output = result.stdout + result.stderr
        check(
            "an invalid Git pathspec fails closed",
            result.returncode != 0 and "SP042" in hook_output,
            hook_output[-900:],
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(pre_commit),
                "restore",
                "--staged",
                "governance/application-profile.yaml",
            ],
            check=True,
        )
        profile.write_text(profile_text, encoding="utf-8")

        register.unlink()
        (pre_commit / "src" / "bypassed.py").write_text("# bypassed gate\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(pre_commit), "add", "-A"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(pre_commit),
                "commit",
                "--no-verify",
                "-m",
                "bypass local gate",
            ],
            check=True,
            capture_output=True,
        )
        offender = subprocess.run(
            ["git", "-C", str(pre_commit), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        register.write_text("# Register\n\nRestored after bypass.\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(pre_commit), "add", "docs/DEVELOPMENT_REGISTER.md"],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(pre_commit),
                "commit",
                "--no-verify",
                "-m",
                "restore prerequisite",
            ],
            check=True,
            capture_output=True,
        )
        untracked_exception = pre_commit / "governance" / "exceptions" / "GX-untracked.yaml"
        untracked_exception.parent.mkdir(parents=True, exist_ok=True)
        untracked_exception.write_text(
            "gate_id: work_registration\n"
            f"commits: [{offender}]\n"
            "owner: Named Owner\n"
            "rationale: This record is deliberately not staged.\n",
            encoding="utf-8",
        )
        (pre_commit / "docs" / "exception-probe.md").write_text(
            "# Probe\n", encoding="utf-8"
        )
        subprocess.run(
            ["git", "-C", str(pre_commit), "add", "docs/exception-probe.md"],
            check=True,
        )
        result = subprocess.run(
            ["git", "-C", str(pre_commit), "commit", "-m", "probe unstaged exception"],
            capture_output=True,
            text=True,
        )
        hook_output = result.stdout + result.stderr
        check(
            "an unstaged exception cannot suppress a historical gate finding",
            "SP035" in hook_output and "PASS - all conformance checks satisfied." not in hook_output,
            hook_output[-900:],
        )

        untracked_exception.write_text(
            untracked_exception.read_text(encoding="utf-8") + "unexpected: true\n",
            encoding="utf-8",
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(pre_commit),
                "add",
                "governance/exceptions/GX-untracked.yaml",
            ],
            check=True,
        )
        result = subprocess.run(
            ["git", "-C", str(pre_commit), "commit", "-m", "stage invalid exception"],
            capture_output=True,
            text=True,
        )
        hook_output = result.stdout + result.stderr
        check(
            "a schema-invalid staged exception provides no coverage",
            result.returncode != 0 and "SP043" in hook_output and "SP035" in hook_output,
            hook_output[-1100:],
        )

        full_hook = make_git_repo(tmp, "full-hook")
        install(full_hook)
        full_hook_profile = read_example("application-profile.full.example.yaml")
        (full_hook / "governance" / "application-profile.yaml").write_text(
            full_hook_profile, encoding="utf-8"
        )
        seed_gate_artefacts(full_hook, full_hook_profile)
        result = verify(full_hook, "--no-grace")
        check(
            "the full worked example passes with the installed hook active",
            result.returncode == 0 and "SP038" not in result.stdout,
            result.stdout[-700:],
        )

        # ---- F29 / DR-30: the instructions must land where each agent actually reads them ----
        #
        # They were emitted only as .github/instructions/*.instructions.md - GitHub Copilot's
        # format. Claude Code loads CLAUDE.md, .claude/CLAUDE.md and .claude/rules/*.md, and
        # nothing under .github/. So every adopter using Claude Code received 501 lines of
        # governance instruction that were never loaded, and so did THIS repository, which had no
        # CLAUDE.md at all for its entire development.
        emitted = make_git_repo(tmp, "emitters")
        install(emitted)
        rules = sorted((emitted / ".claude" / "rules").glob("surfaceplate-*.md"))
        copilot = sorted((emitted / ".github" / "instructions").glob("*.instructions.md"))
        check(
            "the instructions are emitted for Claude Code as well as Copilot",
            len(rules) == 6 and len(copilot) == 6,
            f"{len(rules)} rules, {len(copilot)} copilot files",
        )

        def body_of(path: Path) -> str:
            text = path.read_text(encoding="utf-8")
            return text.split("---", 2)[2] if text.startswith("---") else text

        check(
            "and both forms carry the identical body from one canonical source",
            all(
                body_of(rule) == body_of(emitted / ".github" / "instructions"
                                         / f"{rule.stem.removeprefix('surfaceplate-')}"
                                           ".instructions.md")
                for rule in rules
            ),
            str([r.name for r in rules]),
        )

        # The regression guard. An emitter that changed Copilot's form while adding Claude's
        # would break every existing adopter on upgrade, and every assertion above would still
        # pass - so the front-matter key is asserted directly.
        check(
            "the Copilot form still uses applyTo, unchanged",
            all("applyTo:" in f.read_text(encoding="utf-8") for f in copilot),
            copilot[0].read_text(encoding="utf-8")[:120],
        )

        check(
            "AGENTS.md is created and carries the managed block",
            (emitted / "AGENTS.md").is_file()
            and "BEGIN SURFACEPLATE" in (emitted / "AGENTS.md").read_text(encoding="utf-8"),
            "",
        )
        check(
            "and CLAUDE.md is never written - that file belongs to the adopter",
            not (emitted / "CLAUDE.md").exists(),
            "",
        )

        # NEGATIVE CONTROL. An emitter that simply overwrote agent files would pass everything
        # above. Plyego's AGENTS.md is 293 lines of its own conventions; losing them silently is
        # the failure this mechanism exists to avoid.
        owned = make_git_repo(tmp, "owns-agents")
        (owned / "AGENTS.md").write_text(
            "# The adopter's own conventions\n\nProbe controls before trusting a negative.\n",
            encoding="utf-8")
        (owned / "CLAUDE.md").write_text("@AGENTS.md\n\n## Local\nMy own notes.\n",
                                         encoding="utf-8")
        install(owned)
        agents_text = (owned / "AGENTS.md").read_text(encoding="utf-8")
        check(
            "an adopter's own AGENTS.md content survives, with the block appended",
            "Probe controls before trusting a negative." in agents_text
            and agents_text.count("BEGIN SURFACEPLATE") == 1,
            agents_text[:200],
        )
        check(
            "and their CLAUDE.md is left exactly as it was",
            (owned / "CLAUDE.md").read_text(encoding="utf-8")
            == "@AGENTS.md\n\n## Local\nMy own notes.\n",
            (owned / "CLAUDE.md").read_text(encoding="utf-8"),
        )

        install(owned)
        check(
            "re-installing refreshes the block rather than duplicating it",
            (owned / "AGENTS.md").read_text(encoding="utf-8").count("BEGIN SURFACEPLATE") == 1,
            "",
        )

        tampered = (owned / "AGENTS.md").read_text(encoding="utf-8").replace(
            "BEGIN SURFACEPLATE -->", "BEGIN SURFACEPLATE -->\nSmuggled line.")
        (owned / "AGENTS.md").write_text(tampered, encoding="utf-8")
        owned_profile = read_example("application-profile.essential.example.yaml")
        (owned / "governance" / "application-profile.yaml").write_text(
            owned_profile, encoding="utf-8")
        seed_gate_artefacts(owned, owned_profile)
        result = verify(owned)
        check(
            "an edited block in AGENTS.md is detected",
            "SP008" in result.stdout and "AGENTS.md" in result.stdout,
            result.stdout[-400:],
        )

        # ---- F27 / F28: declining the hook, and what SP038 actually establishes ----
        #
        # The installer refused outright in any repository with an existing hook system, while
        # the standard has always permitted one: SP038 fires only when a gate CLAIMS local_hook.
        # Two parts of one framework disagreeing about the same obligation.
        foreign_hooks = tmp / "foreign-hooks"
        foreign_hooks.mkdir(parents=True, exist_ok=True)
        adopters_hook = foreign_hooks / "pre-commit"
        adopters_hook.write_text("#!/bin/sh\necho \"the adopter's own hook ran\"\n",
                                 encoding="utf-8")
        adopters_hook.chmod(0o755)

        declined = make_git_repo(tmp, "hooks-declined")
        subprocess.run(["git", "-C", str(declined), "config", "core.hooksPath",
                        str(foreign_hooks)], capture_output=True)

        blocked = run([str(INSTALLER), "--target", str(declined)])
        check(
            "the default install still refuses a foreign hooks path, and writes nothing",
            blocked.returncode == 4
            and not (declined / ".standards").exists()
            and not (declined / ".githooks").exists(),
            (blocked.stdout + blocked.stderr)[-400:],
        )
        check(
            "and the refusal now names the third route",
            "--no-hooks" in blocked.stdout,
            blocked.stdout[-500:],
        )

        allowed = run([str(INSTALLER), "--target", str(declined), "--no-hooks"])
        hooks_path = subprocess.run(
            ["git", "-C", str(declined), "config", "--get", "core.hooksPath"],
            capture_output=True, text=True).stdout.strip()
        record = read_record(declined)
        check(
            "--no-hooks installs, leaves core.hooksPath alone, and ships no .githooks",
            allowed.returncode == 0
            and hooks_path == str(foreign_hooks)
            and not (declined / ".githooks").exists()
            and not any("githooks" in rel for rel in record["files"])
            and record.get("executable_files") == [],
            (allowed.stdout + allowed.stderr)[-500:],
        )
        check(
            "and the declination is recorded rather than silent",
            record.get("hooks") == "declined",
            str(sorted(record))[:300],
        )
        # Found exercising --no-hooks against a real repository for the first time (ACT-024):
        # the "Next steps" block told every install to activate and rely on a hook, even when
        # none was written - unreachable from surfaceplate's own self-check, which never
        # installs with --no-hooks on itself.
        check(
            "--no-hooks next-steps names history_audit and review, not a hook to activate",
            "history_audit and review" in allowed.stdout
            and "git update-index --chmod" not in allowed.stdout
            and "pre-commit hook checks staged" not in allowed.stdout,
            allowed.stdout[-600:],
        )

        # The essential example claims no local_hook, which is what a repository relying on
        # history_audit and review looks like. Used as-is.
        declined_profile = read_example("application-profile.essential.example.yaml")
        (declined / "governance" / "application-profile.yaml").write_text(
            declined_profile, encoding="utf-8")
        seed_gate_artefacts(declined, declined_profile)
        result = verify(declined, "--no-grace")
        check(
            "a repository that declined the hook passes, and the run says so",
            # The advisory NAMES SP038, so the finding marker is what must be absent - matching
            # the bare code here would fail against the very line being asserted present.
            "declined at install" in result.stdout and "[SP038]" not in result.stdout,
            result.stdout[-600:],
        )

        # F28. SP038 asked only whether SOME executable pre-commit existed in the active hooks
        # directory - so the adopter's own unrelated hook satisfied a local_hook claim, and the
        # finding's negative result established "a hook exists" rather than "the conformance
        # check runs before commit". Both remaining failure modes are asserted here.
        claiming = declined_profile.replace(
            "enforcement: [history_audit, review]",
            "enforcement: [history_audit, local_hook, review]", 1)
        (declined / "governance" / "application-profile.yaml").write_text(
            claiming, encoding="utf-8")
        result = verify(declined, "--no-grace")
        check(
            "claiming local_hook after declining is caught, though a hook is present",
            "[SP038]" in result.stdout and "declined at install" in result.stdout,
            result.stdout[-600:],
        )

        foreign = make_git_repo(tmp, "foreign-hook")
        install(foreign)
        subprocess.run(["git", "-C", str(foreign), "config", "core.hooksPath",
                        str(foreign_hooks)], capture_output=True)
        foreign_profile = claiming
        (foreign / "governance" / "application-profile.yaml").write_text(
            foreign_profile, encoding="utf-8")
        seed_gate_artefacts(foreign, foreign_profile)
        result = verify(foreign, "--no-grace")
        check(
            "an unrelated pre-commit hook does not satisfy a local_hook claim",
            "[SP038]" in result.stdout
            and "is not the hook this standard installed" in result.stdout,
            result.stdout[-700:],
        )

        # SP055's tracking branch, which needs a REAL repository - the gates fixture above has
        # only a fake .git directory, so git_available() is false there and this path is dead.
        # The pass above is therefore also pattern C's strongest negative control: four registers,
        # one of them holding a genuine record, all tracked, on a repository git can actually read.
        #
        # Asked per record rather than of the directory, because git does not track empty
        # directories: demanding the directory itself would make an empty register impossible and
        # force exactly the fabrication this control refuses to incentivise.
        untracked = full_hook / "governance" / "overrides" / "untracked.yaml"
        untracked.write_text(
            read_example("override-record.approved.example.yaml"), encoding="utf-8")
        result = verify(full_hook, "--no-grace")
        check(
            "a register holding an untracked record is rejected",
            "SP055" in result.stdout,
            result.stdout[-400:],
        )
        untracked.unlink()

        print("\nprerequisite gates - history audit")

        def git_repo(name: str) -> Path | None:
            path = tmp / name
            path.mkdir(parents=True)
            for args in (
                ["init", "-q"],
                ["config", "user.email", "harness@example.invalid"],
                ["config", "user.name", "Harness"],
                ["config", "commit.gpgsign", "false"],
            ):
                if subprocess.run(
                    ["git", "-C", str(path), *args], capture_output=True, text=True
                ).returncode != 0:
                    return None
            return path

        def commit(path: Path, message: str) -> None:
            subprocess.run(["git", "-C", str(path), "add", "-A"], capture_output=True)
            subprocess.run(
                ["git", "-C", str(path), "commit", "--no-verify", "-q", "-m", message],
                capture_output=True,
            )

        history = git_repo("history")
        if history is None:
            check("git is available for the history audit", False, "git init failed")
        else:
            install(history)
            gate_src = essential_src.replace(
                'effective_from: "2026-08-27"',
                f'effective_from: "{(today - _dt.timedelta(days=30)).isoformat()}"',
            )
            (history / "governance" / "application-profile.yaml").write_text(
                gate_src, encoding="utf-8"
            )
            seed_gate_artefacts(history, gate_src)
            commit(history, "adopt the standard with its gates")

            # A commit that crosses the gate while its precondition exists is compliant.
            (history / "src").mkdir(exist_ok=True)
            (history / "src" / "ok.py").write_text("# registered work\n", encoding="utf-8")
            commit(history, "implement registered work")
            result = verify(history, "--no-grace")
            check(
                "a gated change made after the precondition existed passes",
                result.returncode == 0,
                result.stdout[-400:],
            )

            # Remove the precondition, then cross the gate anyway. The commit is permanent
            # evidence, so no later repair can make this state pass.
            register = history / "docs" / "DEVELOPMENT_REGISTER.md"
            register.unlink()
            (history / "src" / "unregistered.py").write_text("# unregistered\n", encoding="utf-8")
            commit(history, "implement unregistered work")
            register.parent.mkdir(parents=True, exist_ok=True)
            register.write_text("# Register\n\nRestored after the fact.\n", encoding="utf-8")
            commit(history, "restore the register")
            result = verify(history, "--no-grace")
            check(
                "a gated change made while the precondition was absent is caught",
                result.returncode == 1 and "SP035" in result.stdout,
                result.stdout[-400:],
            )
            check(
                "and the offending commit is named",
                "unregistered work" in result.stdout,
                result.stdout[-400:],
            )

            # An exception record is the legitimate escape hatch, and leaves a mark.
            offender = subprocess.run(
                ["git", "-C", str(history), "log", "--format=%H", "-1", "--grep", "implement unregistered work"],
                capture_output=True, text=True,
            ).stdout.strip()
            exceptions_dir = history / "governance" / "exceptions"
            exceptions_dir.mkdir(parents=True, exist_ok=True)
            # Quoted (F33): an abbreviated SHA that happens to be all digits - no a-f - parses
            # as a YAML integer unquoted, and schema validation correctly rejects it as not a
            # string. Unquoted here, this test intermittently (~1 run in 40) drew exactly such
            # a SHA and failed for a reason that had nothing to do with what it was testing -
            # the same trap governance/exceptions/GX-0001.yaml's own comment already documented,
            # which never reached this file. Quoting tests the mechanism as the template now
            # teaches it, rather than occasionally testing an unrelated failure mode by chance.
            (exceptions_dir / "GX-0001.yaml").write_text(
                "gate_id: work_registration\n"
                f'commits: ["{offender[:7]}"]\n'
                "owner: Named Owner\n"
                "rationale: >-\n"
                "  Emergency production fix made before the register entry was raised.\n"
                "  The entry was raised retrospectively and the sequence is recorded here.\n",
                encoding="utf-8",
            )
            commit(history, "record gate exception GX-0001")
            result = verify(history, "--no-grace")
            check(
                "a recorded seven-character exception SHA resolves and clears the violation",
                result.returncode == 0,
                result.stdout[-400:],
            )

            # F33, deterministic: an exception naming an unquoted, all-digit commit is invalid
            # for a reason a bare jsonschema message does not explain. Independent of git's own
            # SHA randomness, unlike the probe above - this writes the failure mode directly.
            digit_repo = git_repo("digit-only-sha")
            if digit_repo is not None:
                install(digit_repo)
                (digit_repo / "governance" / "exceptions").mkdir(parents=True, exist_ok=True)
                (digit_repo / "governance" / "exceptions" / "GX-DIGIT.yaml").write_text(
                    "gate_id: work_registration\n"
                    "commits: [1234567]\n"
                    "owner: Named Owner\n"
                    "rationale: >-\n"
                    "  Deliberately unquoted to exercise the digit-only-SHA hint (F33).\n",
                    encoding="utf-8",
                )
                commit(digit_repo, "add an unquoted digit-only exception")
                result = verify(digit_repo)
                check(
                    "an unquoted all-digit commit is caught by SP043",
                    "SP043" in result.stdout and "not of type" in result.stdout,
                    result.stdout[-500:],
                )
                check(
                    "and the fix explains why, not just that it failed",
                    "parses as a YAML number unless quoted" in result.stdout,
                    result.stdout[-500:],
                )

            # Moving effective_from forward would erase the violation silently. It is the
            # one way this control could be gamed from inside, so it is never graced.
            moved = git_repo("moved")
            if moved is not None:
                install(moved)
                original = essential_src.replace(
                    'effective_from: "2026-08-27"',
                    f'effective_from: "{(today - _dt.timedelta(days=60)).isoformat()}"',
                )
                (moved / "governance" / "application-profile.yaml").write_text(
                    original, encoding="utf-8"
                )
                seed_gate_artefacts(moved, original)
                commit(moved, "adopt with gates effective 60 days ago")
                (moved / "governance" / "application-profile.yaml").write_text(
                    essential_src.replace(
                        'effective_from: "2026-08-27"',
                        f'effective_from: "{(today - _dt.timedelta(days=1)).isoformat()}"',
                    ),
                    encoding="utf-8",
                )
                commit(moved, "quietly move the gate forward")
                result = verify(moved)
                check(
                    "moving effective_from forward is rejected even inside grace",
                    result.returncode == 1 and "SP034" in result.stdout,
                    result.stdout[-400:],
                )

        # --- F30: a renamed precondition artefact ---------------------------------------------
        # The audit resolved the artefact at its CURRENT path and asked whether that path existed
        # in each historical commit, so renaming a file - without changing a word of it -
        # retroactively reported every earlier commit as having crossed the gate uncovered. It
        # fired twice in this repository, on renames it chose for its own good reasons.
        renamed = git_repo("renamed-artefact")
        if renamed is None:
            check("git is available for the rename audit", False, "git init failed")
        else:
            install(renamed)
            gate_src = essential_src.replace(
                'effective_from: "2026-08-27"',
                f'effective_from: "{(today - _dt.timedelta(days=30)).isoformat()}"',
            )
            (renamed / "governance" / "application-profile.yaml").write_text(gate_src, encoding="utf-8")
            seed_gate_artefacts(renamed, gate_src)
            commit(renamed, "adopt the standard")

            (renamed / "src").mkdir(exist_ok=True)
            (renamed / "src" / "work.py").write_text("# registered work\n", encoding="utf-8")
            commit(renamed, "implement registered work, precondition in place")

            # The rename. Nothing about the gate's substance changes; only the path does.
            subprocess.run(
                ["git", "-C", str(renamed), "mv",
                 "docs/DEVELOPMENT_REGISTER.md", "docs/ACTIVITY_REGISTER.md"],
                capture_output=True,
            )
            moved_src = gate_src.replace(
                "docs/DEVELOPMENT_REGISTER.md", "docs/ACTIVITY_REGISTER.md"
            )
            (renamed / "governance" / "application-profile.yaml").write_text(moved_src, encoding="utf-8")
            commit(renamed, "rename the register, changing nothing about the gate")

            result = verify(renamed, "--no-grace")
            check(
                "renaming a precondition artefact does not retroactively fail its own history",
                result.returncode == 0,
                result.stdout[-700:],
            )
            check(
                "and the rename it followed is stated on the run, not silently trusted",
                "ACTIVITY_REGISTER" in result.stdout and "DEVELOPMENT_REGISTER" in result.stdout,
                result.stdout[-700:],
            )

            # Negative control: a real violation after the rename is still caught. Following a
            # rename must remove false positives only - never hide a commit that genuinely
            # crossed the gate with nothing in place.
            (renamed / "docs" / "ACTIVITY_REGISTER.md").unlink()
            (renamed / "src" / "sneaky.py").write_text("# unregistered\n", encoding="utf-8")
            commit(renamed, "implement unregistered work after the rename")
            (renamed / "docs" / "ACTIVITY_REGISTER.md").write_text("# Register\n", encoding="utf-8")
            commit(renamed, "restore the register")
            result = verify(renamed, "--no-grace")
            check(
                "a genuine violation after a rename is still caught",
                result.returncode == 1 and "SP035" in result.stdout,
                result.stdout[-500:],
            )
            check(
                "and it names the commit that actually crossed the gate",
                "unregistered work after the rename" in result.stdout,
                result.stdout[-500:],
            )

        print("\nstale control removal")
        stale = make_repo(tmp, "stale")
        install(stale)
        record = read_record(stale)
        ghost = ".github/skills/retired-skill/SKILL.md"
        (stale / ".github/skills/retired-skill").mkdir(parents=True)
        (stale / ghost).write_text("# retired\n", encoding="utf-8")
        record["files"][ghost] = "0" * 64
        write_record(stale, record)
        result = install(stale)
        check("a control dropped from the standard is removed", not (stale / ghost).is_file())
        check("and the removal is reported", "no longer part of the standard" in result.stdout)

    print()
    if FAILURES:
        print(f"INSTALL_CONFORMANCE=FAIL  ({len(FAILURES)} failed, {PASSES} passed)")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"INSTALL_CONFORMANCE=PASS  ({PASSES} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
