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


def offers(repo: Path, gate_ids) -> list[Offer]:
    """What could be created for these gates, in catalogue order.

    **A path that already exists is never offered.** Not offered-and-skipped, not offered with a
    warning - absent, so there is no interaction in which the wizard could overwrite an adopter's
    own file. That is the one hard rule here: this module may create, and may never replace.
    """
    out: list[Offer] = []
    for gate_id in gate_ids:
        if gate_id not in SEEDABLE:
            continue
        path, seed, why = SEEDABLE[gate_id]
        if (repo / path).exists():
            continue
        out.append(Offer(gate_id=gate_id, path=path, seed=seed, why=why))
    return out


def write(repo: Path, accepted: list[Offer]) -> list[Path]:
    """Create the accepted files. Returns what was actually written.

    Refuses again at the point of writing rather than trusting the offer that was built earlier: a
    real run puts a review screen between the two, and a file could have appeared in between. The
    check is cheap and the failure it prevents - overwriting an adopter's own register with an empty
    one - is not recoverable from inside this tool.
    """
    written: list[Path] = []
    for offer in accepted:
        target = repo / offer.path
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(offer.content(), encoding="utf-8", newline="\n")
        written.append(target)
    return written


def seed_texts() -> list[str]:
    """Every seed's full text. `tests/test_provenance.py` uses this to allow exactly the framework
    content this module can write, and nothing else."""
    return [p.read_text(encoding="utf-8") for p in sorted(SEEDS.glob("*")) if p.is_file()]
