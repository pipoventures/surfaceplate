"""Creating the artefact a required gate needs, instead of asking for one that is not there.

`DR-43` records the decision. The short version of why this module exists at all: every packet
before it made the wizard more honest about what it does not know, and `ACT-034` finished that job -
a repository with nothing in it is now told plainly that nothing matches. True, and a dead end. The
adopter cannot proceed, because the thing the gate needs does not exist.

**A seed is not a template, and the difference is the whole design.** Every file in
`surfaceplate/templates/` deliberately carries placeholder tokens - `F15` made them do so, so an
unfilled template is caught - and `SP032` rejects a precondition artefact containing one. Copying a
template into place would therefore create a gate artefact that **fails the checker on the very next
run**, quietly, after the adopter had finished. A seed is the opposite kind of file: complete, true,
and valid the moment it is written, holding no entries rather than holding blanks.

**Creating an artefact does not create the practice**, and that is the risk this module carries
rather than solves. A register that exists satisfies the gate's structural check while the practice
it stands for may not happen. Three things keep that honest: the seed says so in its own text, the
offer says so at the point of choosing, and the run's closing report says so beside the paths it
wrote. `effective_from` is today, so the audit checks a real thing from today forward and claims
nothing about the past.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

SEEDS = Path(__file__).resolve().parent.parent / "seeds"

# Which required gate each seed answers, and where it goes. Deliberately NOT every gate: an
# equivalence-evidence protocol or an output-validation record cannot be created empty and remain a
# true statement about a repository, so those are left to be answered by a human who has one. These
# four cover `essential` (one required gate) and `standard` (four) completely, which is where
# essentially every adopter starts.
SEEDABLE: dict[str, tuple[str, str, str]] = {
    "work_registration": (
        "activity/register.md",
        "activity-register.md",
        "a register for naming work before it starts",
    ),
    "decision_before_implementation": (
        "docs/decisions/decision-log.md",
        "decision-log.md",
        "an append-only log for material decisions",
    ),
    "change_record_before_completion": (
        "CHANGELOG.md",
        "CHANGELOG.md",
        "a changelog describing what changed for anyone relying on this repository",
    ),
    "authority_map": (
        "documentation/governance/inventory/source_of_truth_matrix.yaml",
        "source-of-truth-matrix.yaml",
        "an authority map routing each material question to its one canonical answer",
    ),
}


# `DR-47` (2): a scaffolded artefact is a file the tool creates and therefore knows. The adoption
# decision record is the one non-gate artefact this module creates: `adoption.decision_record_id`
# has no honest source unless a decisions directory already exists to name a record in, and
# inventing an identifier for a record nobody wrote was the thing `defaults.py` refused to do.
# Where a decisions directory exists the id is asked instead (report Part II §II.4).
DECISION_RECORD_ID = "DR-0001"
DECISION_RECORD = (
    "docs/decisions/DR-0001-adopt-surfaceplate.md",
    "adoption-decision-record.md",
    "the record of this adoption decision, which the profile's decision_record_id names",
)
DECISION_RECORD_GATE = "adoption_decision_record"  # the `gate_id` an `Offer` for it carries


@dataclass(frozen=True)
class Offer:
    """One file the wizard could create, and the gate it would answer."""

    gate_id: str
    path: str  # repository-relative
    seed: str  # file name under `seeds/`
    why: str

    def content(self) -> str:
        return (SEEDS / self.seed).read_text(encoding="utf-8")

    def preview(self, lines: int = 4) -> str:
        body = [ln for ln in self.content().splitlines() if ln.strip()]
        return "\n".join(body[:lines])


def _occupied(target: Path) -> bool:
    """Whether anything at all is at this path - including a symlink pointing nowhere.

    `Path.exists()` follows symlinks and answers **False for a dangling one**, which defeated this
    module's only hard rule: a repository whose `CHANGELOG.md` was a broken symlink got an offer,
    and `write_text` then followed the link and created the file **outside the repository** while
    the run reported having written it inside. `os.path.lexists` asks about the link itself.
    """
    return os.path.lexists(target)


def _inside(repo: Path, target: Path) -> bool:
    """Whether `target` really lands inside `repo`, after `..` and symlinks are resolved.

    `SEEDABLE` holds four fixed relative paths so a traversing path cannot arise from normal use.
    This is here because "cannot arise" is an argument about today's callers, and the thing it
    guards - writing into somebody's repository - is the one place in this tool where being wrong
    is not recoverable.
    """
    root = repo.resolve()
    candidate = (repo / target).parent.resolve() if not target.is_absolute() else target.resolve()
    return root == candidate or root in candidate.parents


def offers(repo: Path, gate_ids) -> list[Offer]:
    """What could be created for these gates, in catalogue order.

    **A path that is occupied is never offered.** Not offered-and-skipped, not offered with a
    warning - absent, so there is no interaction in which the wizard could overwrite an adopter's
    own file. That is the one hard rule here: this module may create, and may never replace.

    The caller decides which gates to pass. It must pass only gates the profile will actually
    declare with a required artefact: offering for a gate the adopter's level never asks about
    produced files that no gate referenced, on a screen that claimed they were needed.
    """
    out: list[Offer] = []
    for gate_id in gate_ids:
        if gate_id not in SEEDABLE:
            continue
        path, seed, why = SEEDABLE[gate_id]
        if _occupied(repo / path):
            continue
        out.append(Offer(gate_id=gate_id, path=path, seed=seed, why=why))
    return out


def decision_record_offer(repo: Path) -> Offer | None:
    """The adoption decision record, offered only where nothing is at its path."""
    path, seed, why = DECISION_RECORD
    if _occupied(repo / path):
        return None
    return Offer(gate_id=DECISION_RECORD_GATE, path=path, seed=seed, why=why)


def write(repo: Path, accepted: list[Offer]) -> tuple[list[Path], list[str]]:
    """Create the accepted files. Returns `(written, problems)`.

    **Creation is atomic**: `open(..., "x")` both refuses an occupied path and creates the file in
    one operation, so there is no window between checking and writing for a file - or a symlink - to
    appear in. The earlier form checked `exists()` and then truncated, which is the classic shape of
    a check that is not a guarantee, and the docstring sold it as one.

    **Nothing raises out of here.** A parent that exists as a regular file used to abort the run
    with `NotADirectoryError` *after* earlier offers were already on disk and *before* the profile
    was written - a half-finished adoption with a traceback. Problems are collected and reported to
    the adopter instead, and the rest of the run continues.
    """
    written: list[Path] = []
    problems: list[str] = []
    for offer in accepted:
        target = repo / offer.path
        if not _inside(repo, Path(offer.path)):
            problems.append(f"{offer.path}: refused - it does not land inside this repository")
            continue
        if _occupied(target):
            problems.append(f"{offer.path}: left alone - something is already there")
            continue
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "x", encoding="utf-8", newline="\n") as handle:
                handle.write(offer.content())
        except FileExistsError:
            problems.append(f"{offer.path}: left alone - it appeared while this run was deciding")
            continue
        except OSError as exc:
            problems.append(f"{offer.path}: could not be created - {exc.strerror or exc}")
            continue
        written.append(target)
    return written, problems


def seed_texts() -> list[str]:
    """Every seed's full text. `tests/test_provenance.py` uses this to allow exactly the framework
    content this module can write, and nothing else."""
    return [p.read_text(encoding="utf-8") for p in sorted(SEEDS.glob("*")) if p.is_file()]
