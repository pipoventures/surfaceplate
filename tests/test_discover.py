#!/usr/bin/env python3
"""Repository discovery: what the wizard offers as candidate answers.

    python tests/test_discover.py

`DR-38`: every structural question is answered from a list read out of the repository rather than
typed into a blank box. The rule this suite exists to hold is the one `example_answers.py` set when
it refused to invent plausible artefact paths - **never offer something that isn't there** - so the
load-bearing checks here are the negative ones: an ignored file is not a candidate, an untracked
file is not a candidate, and a repository git cannot read yields nothing rather than a filesystem
walk full of `.venv` and build output.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from surfaceplate.adopt import defaults, discover  # noqa: E402

FAILURES: list[str] = []
PASSES = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSES
    if condition:
        PASSES += 1
        print(f"  PASS  {name}")
    else:
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL  {name}  {detail}")


def make_repo(tmp: Path) -> Path:
    """A small repository with the shapes discovery is meant to find - and two it must not."""
    repo = tmp / "fixture"
    (repo / "docs").mkdir(parents=True)
    (repo / "governance").mkdir()
    (repo / "src" / "app").mkdir(parents=True)
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / "build").mkdir()

    (repo / "docs" / "REGISTER.md").write_text("# register\n", encoding="utf-8")
    (repo / "governance" / "authority-map.yaml").write_text("map: {}\n", encoding="utf-8")
    (repo / "src" / "app" / "main.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
    (repo / "CHANGELOG.md").write_text("# changes\n", encoding="utf-8")
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "jobs:\n  build:\n    steps:\n"
        "      - name: Run the unit tests\n        run: pytest\n"
        "      - name: Check the contracts\n        run: make contracts\n",
        encoding="utf-8",
    )

    # Must never be offered: one ignored, one merely untracked.
    (repo / ".gitignore").write_text("build/\nsecret-notes.md\n", encoding="utf-8")
    (repo / "build" / "generated.md").write_text("# generated\n", encoding="utf-8")
    (repo / "secret-notes.md").write_text("# private\n", encoding="utf-8")
    (repo / "docs" / "untracked.md").write_text("# never added\n", encoding="utf-8")

    for args in (
        ["init", "-q"],
        ["config", "user.email", "h@example.invalid"],
        ["config", "user.name", "H"],
        ["config", "commit.gpgsign", "false"],
    ):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    # Everything except docs/untracked.md, which is left deliberately unstaged.
    subprocess.run(["git", "-C", str(repo), "add", "-A", ":!docs/untracked.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True)
    return repo


def test_finds_the_real_things(repo: Path) -> None:
    found = discover.scan(repo)

    check(
        "a governance document is offered as a precondition artefact",
        "docs/REGISTER.md" in found.artefacts and "governance/authority-map.yaml" in found.artefacts,
        str(found.artefacts),
    )
    check(
        "the adopter's own directories rank before anything else",
        found.artefacts[0].startswith("docs/"),
        str(found.artefacts[:3]),
    )
    check(
        "a source directory is offered as a gated pathspec, ahead of the rest",
        found.paths[0] == "src/**",
        str(found.paths),
    )
    check(
        "the whole repository is offered, but last",
        found.paths[-1] == "**",
        str(found.paths),
    )
    check(
        "the lock file is found",
        found.lock_files == ("requirements.txt",),
        str(found.lock_files),
    )
    check(
        "real CI step names are read out of the workflow",
        set(found.ci_steps) == {"Run the unit tests", "Check the contracts"},
        str(found.ci_steps),
    )
    check(
        "a directory of YAML records is offered as a register",
        "governance" in found.register_dirs,
        str(found.register_dirs),
    )


def test_never_offers_what_is_not_really_there(repo: Path) -> None:
    """The load-bearing half. An offered path that does not exist, or that git does not consider
    part of the repository, would be exactly the "plausible-looking example" `example_answers.py`
    refused to produce - only worse, because it would look discovered."""
    found = discover.scan(repo)
    every = set(found.artefacts) | set(found.paths) | set(found.lock_files) | set(found.register_dirs)

    check(
        "a gitignored file is never offered",
        "build/generated.md" not in every and "secret-notes.md" not in every,
        str(sorted(every)),
    )
    check(
        "an untracked file is never offered",
        "docs/untracked.md" not in found.artefacts,
        str(found.artefacts),
    )
    check(
        "an ignored directory is never offered as a gated path",
        "build/**" not in found.paths,
        str(found.paths),
    )
    missing = [
        p for p in list(found.artefacts) + list(found.lock_files) if not (repo / p).exists()
    ]
    check("every offered file actually exists on disk", not missing, f"missing: {missing}")
    absent_dirs = [d for d in found.register_dirs if not (repo / d).is_dir()]
    check("every offered register directory actually exists", not absent_dirs, str(absent_dirs))


def test_a_repository_git_cannot_read_yields_nothing(tmp: Path) -> None:
    """Not a filesystem walk. A walk would offer `.venv/`, `node_modules/` and build output as
    governance artefacts, which is worse than offering nothing: an empty list simply leaves the
    field behaving as it did before discovery existed."""
    plain = tmp / "not-a-repo"
    (plain / "docs").mkdir(parents=True)
    (plain / "docs" / "REGISTER.md").write_text("# register\n", encoding="utf-8")

    found = discover.scan(plain)
    check(
        "a directory that is not a git repository offers no candidates",
        found.is_empty() or not found.artefacts,
        str(found),
    )


def test_a_proposal_needs_evidence_not_merely_a_candidate(tmp: Path) -> None:
    """`F40`. Ranking orders candidates; it never establishes that any of them are right.

    `rank_for_gate` returns `hit + rest` so the dropdown offers everything - correct, and `DR-38`'s
    rule. But `defaults.propose_gates` took `ranked[0]`, so in a repository holding one unrelated
    file the wizard PROPOSED that file as the precondition for `work_registration` - the gate
    meaning *no work begins until it is registered as an activity*. A README satisfies `SP032`
    (exists, non-empty, no placeholder), so the resulting gate passes while guarding nothing.

    The rule this pins: a proposal may only come from a candidate that actually matched the gate.
    Offering is not proposing.
    """
    bare = tmp / "bare-repo"
    bare.mkdir()
    (bare / "README.md").write_text("# a small tool\n", encoding="utf-8")
    (bare / "main.py").write_text("x = 1\n", encoding="utf-8")
    for args in (
        ["init", "-q"],
        ["config", "user.email", "h@example.invalid"],
        ["config", "user.name", "H"],
        ["config", "commit.gpgsign", "false"],
    ):
        subprocess.run(["git", "-C", str(bare), *args], check=True)
    subprocess.run(["git", "-C", str(bare), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(bare), "commit", "-qm", "bare"], check=True)

    found = discover.scan(bare)
    check(
        "the unrelated file is still OFFERED - nothing is hidden from the adopter",
        "README.md" in discover.rank_for_gate(found.artefacts, "work_registration"),
        str(found.artefacts),
    )
    check(
        "but it is not a MATCH for that gate, because it matched no keyword",
        discover.matched_for_gate(found.artefacts, "work_registration") == [],
        str(discover.matched_for_gate(found.artefacts, "work_registration")),
    )

    proposals = defaults.propose_gates(
        level="essential", builds_ui=False, mode="simple", found=found
    )
    artefact_proposals = [p for p in proposals if p.field.endswith(".artefact")]
    check(
        "so no precondition artefact is proposed at all (F40)",
        artefact_proposals == [],
        f"proposed anyway: {[p.describe() for p in artefact_proposals]}",
    )

    # The positive control. Without it this suite would pass by proposing nothing, ever.
    (bare / "activity").mkdir()
    (bare / "activity" / "register.md").write_text("# activity register\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(bare), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(bare), "commit", "-qm", "register"], check=True)
    found = discover.scan(bare)
    proposals = defaults.propose_gates(
        level="essential", builds_ui=False, mode="simple", found=found
    )
    proposed = {p.field: p.value for p in proposals}
    check(
        "and a real register IS proposed once one exists",
        proposed.get("gates.work_registration.artefact") == "activity/register.md",
        str(proposed.get("gates.work_registration.artefact")),
    )


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True)


def _init(repo: Path) -> None:
    for args in (
        ["init", "-q"], ["config", "user.email", "h@example.invalid"],
        ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"],
    ):
        _git(repo, *args)


def test_discovery_cannot_find_the_framework_in_the_mirror(tmp: Path) -> None:
    """`F61` / R7. Discovery proposed `.github/instructions/authority.instructions.md` as the
    adopter's authority map and the installed workflow's own step as the adopter's contract test,
    and the level screen told a bare repository "You appear to have: a CI workflow" sixty seconds
    after the installer wrote it. A repository containing nothing but the install payload must
    yield no candidates, no proposals and no "you appear to have"."""
    import json
    import sys

    from surfaceplate.adopt import plan

    ROOT_SRC = ROOT / "surfaceplate"
    repo = tmp / "only-the-payload"
    repo.mkdir()
    _init(repo)
    result = subprocess.run(
        [sys.executable, str(ROOT_SRC / "install_standard.py"), "--source", str(ROOT_SRC),
         "--target", str(repo), "--no-hooks"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "install")
    installed = set(json.loads((repo / ".standards" / "INSTALL.json").read_text())["files"])

    found = discover.scan(repo)
    offered = set(found.artefacts) | set(found.register_dirs) | set(found.lock_files)
    check(
        "no installed file is offered as an artefact, register or lock file",
        not (offered & installed) and not any(p.startswith(".standards") for p in offered),
        str(sorted(offered)[:6]),
    )
    check(
        "the installed workflow's steps are not offered as CI steps",
        not found.ci_steps,
        str(found.ci_steps),
    )
    state = {"mode": {"mode": "simple"}, "identity": {"owner": "O"},
             "stack": {"builds_user_interface": False}, "level": {"conformance_level": "standard"}}
    proposals = [p for p in defaults.propose(state, found=found) if p.origin == "discovered"]
    check(
        "and nothing is proposed as discovered",
        not proposals,
        "; ".join(p.describe() for p in proposals[:4]),
    )
    present, _absent = plan.detected_signals(repo)
    check(
        "and the level screen does not say 'you appear to have' a CI workflow",
        not any("CI workflow" in line for line in present),
        str(present),
    )


def test_ranking_happens_before_the_cap(tmp: Path) -> None:
    """`F75`. `_capped` cut the artefact list to 200 before `matched_for_gate` ran, so a
    repository with 300 files under `docs/` lost its real `activity/register.md` and got no
    proposal. Rank first, cap last, cap per field."""
    repo = tmp / "big-docs"
    (repo / "docs" / "archive").mkdir(parents=True)
    for i in range(300):
        (repo / "docs" / "archive" / f"note-{i:03d}.md").write_text("# note\n", encoding="utf-8")
    (repo / "activity").mkdir()
    (repo / "activity" / "register.md").write_text("# activity register\n", encoding="utf-8")
    _init(repo)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "big")

    found = discover.scan(repo)
    proposed = {
        p.field: p.value
        for p in defaults.propose_gates(level="essential", builds_ui=False, mode="simple", found=found)
    }
    check(
        "a real register is proposed even with 300 documents ahead of it",
        proposed.get("gates.work_registration.artefact") == "activity/register.md",
        str(proposed.get("gates.work_registration.artefact")),
    )
    check(
        "and the register is offered in the per-gate list, ranked first",
        discover.rank_for_gate(found.artefacts, "work_registration")[:1] == ["activity/register.md"],
        str(discover.rank_for_gate(found.artefacts, "work_registration")[:3]),
    )


def test_a_non_ascii_path_is_offered_verbatim(tmp: Path) -> None:
    """Code item 8. `git ls-files` C-quotes a non-ASCII path (`"docs/caf\\303\\251.md"`), and
    `_tracked_files` kept the quotes, so the real file was dropped and a quoted string offered.
    `git ls-files -z` outputs paths verbatim regardless of `core.quotePath`."""
    repo = tmp / "accents"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "caf\u00e9-register.md").write_text("# register\n", encoding="utf-8")
    _init(repo)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "accent")
    found = discover.scan(repo)
    check(
        "the accented path is offered exactly as it is on disk",
        "docs/caf\u00e9-register.md" in found.artefacts,
        str(found.artefacts),
    )
    check(
        "and no C-quoted form of it is offered",
        not any(p.startswith('"') or "\\303" in p for p in found.artefacts),
        str(found.artefacts),
    )


def test_is_empty_is_true_when_git_cannot_answer(tmp: Path) -> None:
    """Code item 9. `Discovered.is_empty()` could never be true because `candidate_paths` always
    appended `**`, so its documented fallback had no case. A tree git cannot read is empty."""
    plain = tmp / "not-git"
    (plain / "docs").mkdir(parents=True)
    (plain / "docs" / "REGISTER.md").write_text("# register\n", encoding="utf-8")
    found = discover.scan(plain)
    check("a non-git tree scans as empty", found.is_empty(), str(found))
    check("and a git repository with content does not", not discover.scan(make_repo(tmp / "again")).is_empty())


def test_the_cap_is_on_the_offer_not_on_the_answer(repo: Path) -> None:
    """`F75` moved the cap from the scan to the field: the scan keeps everything so ranking has
    everything to promote, and what an adopter is offered is cut to `SHOWN` afterwards."""
    from surfaceplate.adopt import plan

    found = discover.scan(repo)
    gates = plan.gate_plan(level="full", builds_ui=True, mode="simple", found=found)
    offers = [
        len(f.choices)
        for spec in gates
        for f in spec.fields
        if f.kind == "select"
    ]
    check(
        "every dropdown an adopter is offered is short enough to pick from",
        offers and all(n <= discover.SHOWN for n in offers),
        str(offers),
    )
    check(
        "and the ranked-first candidate survives whatever the cap removes",
        discover.rank_for_gate(found.artefacts, "work_registration")[0] == "docs/REGISTER.md",
        str(discover.rank_for_gate(found.artefacts, "work_registration")[:2]),
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        repo = make_repo(tmp)

        print("discovery finds what is really there")
        test_finds_the_real_things(repo)

        print("\nand never offers what is not (the load-bearing half)")
        test_never_offers_what_is_not_really_there(repo)
        test_a_repository_git_cannot_read_yields_nothing(tmp)

        print("\nand never PROPOSES what it merely offers (F40)")
        test_a_proposal_needs_evidence_not_merely_a_candidate(tmp)

        print("\nF61, F75 and code items 8, 9: the framework is not in the mirror, and the cap comes last")
        test_discovery_cannot_find_the_framework_in_the_mirror(tmp)
        test_ranking_happens_before_the_cap(tmp)
        test_a_non_ascii_path_is_offered_verbatim(tmp)
        test_is_empty_is_true_when_git_cannot_answer(tmp)

        print("\nlist sizes")
        test_the_cap_is_on_the_offer_not_on_the_answer(repo)

    print()
    if FAILURES:
        print(f"DISCOVER=FAIL  ({len(FAILURES)} failed, {PASSES} passed)")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"DISCOVER=PASS  ({PASSES} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
