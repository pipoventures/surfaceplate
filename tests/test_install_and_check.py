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

sys.path.insert(0, str(ROOT / "scripts"))
import install_standard as _installer  # noqa: E402

# The pin an install from THIS tree actually records.
#
# The worked examples carry static framework_version/framework_digest values that cannot match
# any particular install, so SP048/SP049 would fail every fixture for a reason unrelated to the
# thing each test is about. A real adopter takes both values from their own
# .standards/INSTALL.json after installing; the harness does the same. Note what is NOT done
# here: the check is not disabled, and the fields are not removed. The targeted SP048/SP049
# cases below deliberately mismatch them and assert the failure.
FIXTURE_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
FIXTURE_ANCHOR = _installer.framework_anchor(ROOT)


def read_example(name: str) -> str:
    """A worked example, with its pin rewritten to match what installing from ROOT records."""
    text = (ROOT / "examples" / name).read_text(encoding="utf-8")
    text = re.sub(r"(?m)^(\s*framework_version:\s*).*$", lambda m: m.group(1) + FIXTURE_VERSION, text)
    if FIXTURE_ANCHOR:
        text = re.sub(r"(?m)^(\s*framework_digest:\s*).*$", lambda m: m.group(1) + FIXTURE_ANCHOR, text)
    return text

INSTALLER = ROOT / "scripts" / "install_standard.py"

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


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        neutralise_ambient_git_config(tmp)

        print("\nnot installed")
        empty = make_repo(tmp, "empty")
        result = verify_uninstalled = run(
            [str(ROOT / "scripts" / "check_conformance.py"), "--repo", str(empty)]
        )
        check("uninstalled repository fails", result.returncode == 1, result.stdout[-200:])
        check("and says why", "SP001" in result.stdout)

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
            ROOT / "templates" / "application-profile.yaml",
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

        default_hooked = make_git_repo(tmp, "default-hooked")
        commit_msg_hook = default_hooked / ".git" / "hooks" / "commit-msg"
        commit_msg_hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        result = install(default_hooked)
        check(
            "refuses to disable a non-pre-commit default hook",
            result.returncode == 4,
            result.stdout[-400:],
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

        # A level with controls that remain unverified must still say so. As each packet lands
        # this has to move up a level: `standard` was fully verified by pattern B (ACT-012), so
        # the only level with unverified controls now is `full` - its four record-based controls
        # are pattern C, packet 4. When that lands, this assertion should be deleted rather than
        # relocated, because there will be no level left for it to be true of.
        result = gate_check(essential_src.replace(
            "conformance_level: essential", "conformance_level: full"))
        check(
            "a level with unverified controls still reports them",
            "DECLARED, not checked" in result.stdout,
            result.stdout[:400],
        )
        check(
            "and names the pattern C controls specifically",
            all(c in result.stdout for c in ("provenance", "run_lineage", "method_registry", "overrides")),
            result.stdout[:500],
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
            [str(ROOT / "scripts" / "check_conformance.py"), "--repo", str(no_history)]
        )
        check(
            "an unusable Git directory is reported as not installed",
            result.returncode == 1 and "SP001" in result.stdout,
            result.stdout[-300:],
        )
        shutil.copytree(repo / ".standards", no_history / ".standards")
        shutil.copytree(repo / ".github", no_history / ".github")
        shutil.copytree(repo / ".githooks", no_history / ".githooks")
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
            (exceptions_dir / "GX-0001.yaml").write_text(
                "gate_id: work_registration\n"
                f"commits: [{offender[:7]}]\n"
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
