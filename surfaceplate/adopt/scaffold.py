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
    # `DR-55`: every gate whose artefact can be an honest empty register, log or statement of
    # the standard's own rule. Paths follow the worked example. What stays out, on purpose: the
    # four interface gates, the regression suite, the equivalence protocol, and the two gates
    # that reuse the map and the register.
    "options_before_build": (
        "docs/decisions/OPTIONS.md",
        "options-log.md",
        "a log of design options considered, holding none yet",
    ),
    "risk_classification": (
        "governance/RISK_CLASSIFICATION.md",
        "risk-classification.md",
        "the standard's scale and rule, with this repository's level meanings left to declare",
    ),
    "test_convention": (
        "docs/testing/TEST_CONVENTIONS.md",
        "test-conventions.md",
        "the standard's naming convention, with this repository's test areas left to declare",
    ),
    "data_source_lifecycle": (
        "governance/DATA_SOURCES.md",
        "data-source-register.md",
        "a register of data sources and their approval state, holding none yet",
    ),
    "output_validation_before_external_use": (
        "docs/OUTPUT_VALIDATION.md",
        "output-validation-log.md",
        "a log of validated outputs, holding none yet",
    ),
    "dependency_output_delta": (
        "docs/DEPENDENCY_REVIEW.md",
        "dependency-review-log.md",
        "a log of dependency reviews, holding none yet",
    ),
    "records_before_release": (
        "docs/RELEASE_CHECKLIST.md",
        "release-checklist.md",
        "the records a release needs, quoted from the standard, with one line only this repository can fill",
    ),
}


# `DR-54` (3): the one control whose implementation reference can be created as a true statement.
# A findings register holding no findings is complete and honest on the day it is written; a lock
# file or a CI step cannot be invented the same way.
SEEDABLE_CONTROLS: dict[str, tuple[str, str, str]] = {
    "assurance_findings": (
        "docs/FINDINGS.md",
        "findings-register.md",
        "a register of known limitations and findings, holding none yet",
    ),
    # `DR-55`: the record-directory controls. The reference is the directory; what is written is
    # a note inside it, which the checker does not read (it validates `*.y*ml` only), so an empty
    # directory with the note is exactly what the control's check describes as a valid start.
    "method_registry": (
        "governance/method-registry",
        "method-registry-readme.md",
        "a directory for method records, holding none yet",
    ),
    "overrides": (
        "governance/overrides",
        "overrides-readme.md",
        "a directory for override records, holding none yet",
    ),
    "run_lineage": (
        "governance/run-lineage",
        "run-lineage-readme.md",
        "a directory for run records, holding none yet",
    ),
    "provenance": (
        "governance/run-lineage",
        "run-lineage-readme.md",
        "the same directory of run records as run_lineage, holding none yet",
    ),
}

# For a reference that is a directory, the file the seed writes inside it.
DIRECTORY_NOTE = "README.md"


def write_path_for(reference: str) -> str:
    """Where a seed is written: the reference itself for a file, the note inside it for a directory."""
    return f"{reference}/{DIRECTORY_NOTE}" if not reference.rsplit("/", 1)[-1].count(".") else reference


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
    control_id: str = ""  # set for a control's implementation reference (`DR-54` (3))
    reference: str = ""  # what the profile records, where it differs from `path` (a directory)

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


def offers_for_controls(repo: Path, control_ids) -> list[Offer]:
    """What could be created for these controls' implementation references (`DR-54` (3)); the same
    one hard rule as `offers`: an occupied path is never offered."""
    out: list[Offer] = []
    for control_id in control_ids:
        if control_id not in SEEDABLE_CONTROLS:
            continue
        reference, seed, why = SEEDABLE_CONTROLS[control_id]
        if _occupied(repo / reference):
            continue
        out.append(Offer(gate_id=f"control:{control_id}", path=write_path_for(reference), seed=seed, why=why,
                         control_id=control_id, reference=reference))
    return out


def seed_preview(path: str, lines: int = 2) -> str:
    """The first lines of whichever seed creates `path`, for the help beside a "create it" row."""
    for table in (SEEDABLE, SEEDABLE_CONTROLS):
        for seed_path, seed, _why in table.values():
            if path in (seed_path, write_path_for(seed_path)):
                body = [ln for ln in (SEEDS / seed).read_text(encoding="utf-8").splitlines() if ln.strip()]
                return " / ".join(body[:lines])
    return ""


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
    seen: set[str] = set()
    for offer in accepted:
        if offer.path in seen:
            continue  # two controls sharing one directory (`provenance`, `run_lineage`): one note
        seen.add(offer.path)
        target = repo / offer.path
        if not _inside(repo, Path(offer.path)):
            problems.append(f"{offer.path}: refused - it does not land inside this repository")
            continue
        if _occupied(target):
            problems.append(f"{offer.path}: left alone - something is already there")
            continue
        # Two separate tries, because they fail for different reasons and used to share one
        # `FileExistsError` handler: a parent that exists as a regular FILE raises it from
        # `mkdir`, and was reported as a race on the target that never happened (code item 12).
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except (FileExistsError, NotADirectoryError):
            problems.append(
                f"{offer.path}: could not be created - a parent of it is a file, not a directory"
            )
            continue
        except OSError as exc:
            problems.append(f"{offer.path}: could not be created - {exc.strerror or exc}")
            continue
        try:
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


def rollback(repo: Path, written: list[Path]) -> tuple[list[Path], list[str]]:
    """Remove the files `write` created in this run, and the directories left empty by removing
    them, up to the repository root. Returns `(removed, problems)`.

    `F101`: the seeds are written before the profile so that the profile never names a file that
    does not exist; when the profile write then fails, the seeds were left on disk and reported.
    They are this run's own files - created seconds earlier with an exclusive create, so nothing
    of the adopter's is among them - and are removed, with the report as the fallback where a
    removal itself fails. An empty directory is pruned only if it is empty; git tracks no empty
    directory, so the tracked tree is exactly as it was.
    """
    removed: list[Path] = []
    problems: list[str] = []
    root = repo.resolve()
    for target in written:
        try:
            target.unlink()
            removed.append(target)
        except FileNotFoundError:
            continue
        except OSError as exc:
            problems.append(f"{target}: could not be removed - {exc.strerror or exc}")
            continue
        parent = target.parent
        while parent.resolve() != root and root in parent.resolve().parents:
            try:
                parent.rmdir()  # only an empty directory can be removed this way
            except OSError:
                break
            parent = parent.parent
    return removed, problems


def seed_texts() -> list[str]:
    """Every seed's full text. `tests/test_provenance.py` uses this to allow exactly the framework
    content this module can write, and nothing else."""
    return [p.read_text(encoding="utf-8") for p in sorted(SEEDS.glob("*")) if p.is_file()]
