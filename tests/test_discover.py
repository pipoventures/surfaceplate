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


def test_the_cap_is_on_the_offer_not_on_the_answer(repo: Path) -> None:
    found = discover.scan(repo)
    check(
        "candidate lists stay short enough to pick from",
        all(
            len(group) <= discover._MAX_CANDIDATES
            for group in (found.artefacts, found.paths, found.register_dirs, found.ci_steps)
        ),
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
