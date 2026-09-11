"""A prompt to paste into an AI coding agent, so adoption has a door for people who find the
terminal hard.

    surfaceplate agent-prompt --target <repo>

WHY THIS EXISTS. Adoption had two doors and both assume a terminal: the Textual wizard, and the
no-terminal path (`adopt --propose` -> fill the answers record -> `adopt --answers`). The
maintainer asked for a third, for *"someone [who] finds the terminal too difficult to complete or
[has] doubts about stuff"*, by handing them a prompt for whatever agent they already use.

**This is not a new adoption mechanism.** It is the `--propose`/`--answers` path narrated by an
agent that can answer follow-up questions. `DR-35` records why that narration is needed: a live
adoption hit *"I don't know what this is"* three times in a row, and `explanations.py` was written
in response - 31 items, each in a `simple` and an `advanced` register. This points an agent at that
material instead of letting it invent its own.

THE HARD PART IS NOT EXPLAINING THE TOOL; IT IS BOUNDING THE AGENT. This standard reserves to
people the decisions an agent may not take, and the three most expensive defects of the year -
`F40`, `F84`, `F144` - were each *the tool supplying a value nobody chose*. A prompt that says
"help me adopt Surfaceplate" invites an agent to fill a profile with invented answers: the same
failure mode, one level up, in a friendlier wrapper. So the contract below is the feature, and the
explanation is the packaging.

WHAT THIS CANNOT DO, stated here rather than left to be discovered (`DR-85`): nothing makes an
agent obey a prompt. The prompt is text. What the design can do is refuse to make disobedience
easy - the agent is told to read the installed documents rather than paraphrase from training, and
`adopt --answers` refuses a record with `needs-human` lines outstanding, so nothing can be skipped.
It can still be *answered* by the wrong party, and the provenance record cannot today tell "the
human typed it" from "an agent typed it on their behalf". `DR-85` carries that gap.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# The registers `explanations.py` already maintains. Exposed here rather than invented: the
# distinction exists and was previously reachable only from inside the wizard.
REGISTERS = ("simple", "advanced")


def _payload():
    """`(about, doctor, discover, plan, rules)`.

    ABSOLUTE IMPORTS, AND NO FLAT FALLBACK - unlike `check_conformance.py`, which carries one
    because it is vendored into every adopting repository and runs from `.standards/` with the
    payload directory itself on `sys.path`.

    This module is not vendored and cannot be: it reads `surfaceplate.adopt`, and `adopt/plan.py`
    imports `surfaceplate.rules` absolutely, so the wizard package has no flat form. A fallback
    here would be dead code pretending to a portability this module does not have - and the
    suites exercise it the way an adopter does, by running the command.
    """
    from surfaceplate import about, doctor, rules
    from surfaceplate.adopt import discover, plan

    return about, doctor, discover, plan, rules


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        sys.stderr.write(f"error: {message}\n")
        sys.exit(3)


def _repository_lines(repo: Path) -> list[str]:
    """What this repository looks like, in counts rather than contents.

    Counts, deliberately. The agent needs to know that nine CI steps exist and none is named as a
    test; it does not need their text, and neither does whatever provider the human pastes this
    into. `_redact` then removes the paths that remain.
    """
    _about, doctor, discover, plan, rules = _payload()

    _installed, record = doctor._installed_standard_lines(repo)
    lines = ["## This repository", ""]
    if record is None:
        lines.append("  Surfaceplate is not installed here yet.")
    else:
        lines.append(f"  Surfaceplate {record.get('standard_version', '(unknown)')} is installed.")
        lines.append(f"  Grace ends {record.get('grace_expires', '(unknown)')}.")

    try:
        found = discover.scan(repo)
    except Exception:  # noqa: BLE001 - a tree git cannot answer for still gets a prompt
        lines += ["", "  Discovery could not read this repository (is it a git repository?)."]
        return lines

    steps = list(found.ci_steps)
    not_tests = sum(1 for s in steps if rules.step_name_is_clearly_not_a_test(s))
    lines += [
        "",
        "  What discovery found, in counts - the agent should run the commands below to see the",
        "  detail rather than take these as the whole picture:",
        f"    - {len(found.artefacts)} tracked document(s) that could serve as a gate's precondition",
        f"    - {len(steps)} CI step(s)"
        + (f", of which {not_tests} are named as fetching, preparing or shipping rather than testing"
           if steps else ""),
        f"    - {len(found.lock_files)} dependency lock file(s)"
        + ("" if found.has_dependency_manifest else "; no dependency manifest of any kind"),
        f"    - {len(found.scanner_workflows)} workflow(s) where a step runs the secret scanner",
        f"    - {len(found.register_dirs)} director(y/ies) of YAML records",
    ]
    present, absent = plan.detected_signals(repo)
    if present:
        lines += ["", "  Present: " + "; ".join(present)]
    if absent:
        lines.append("  Absent:  " + "; ".join(absent))
    return lines


def _contract_lines() -> list[str]:
    """The rules the agent is held to, and the reason for each.

    Stated as rules with reasons rather than as a policy quotation, because an agent that
    understands *why* a line is drawn is likelier to respect its edges than one handed a
    prohibition. The reasons are this framework's own and are not softened.
    """
    return [
        "## What you may do, and what you must not",
        "",
        "You MAY:",
        "  - run `surfaceplate install --dry-run` and read its output to me",
        "  - run `surfaceplate install` once I have agreed to what the dry run showed",
        "  - run `surfaceplate adopt --propose`, which writes an answers record and never the profile",
        "  - read that record and explain every line marked `needs-human` to me, in plain English",
        "  - run `surfaceplate check` and report its output verbatim",
        "  - run `surfaceplate adopt --answers <record>` once I have filled every `needs-human` line",
        "  - create the scaffolded artefacts I tick, when the tool offers them",
        "",
        "You MUST NOT:",
        "  - write a value into any line marked `needs-human`. Not a draft, not a suggestion in the",
        "    file, not a 'sensible default'. Ask me; wait for my answer; put my words there.",
        "  - choose a conformance level for me",
        "  - decide a gate's status, or write a rationale in my name",
        "  - tell me a check passed without showing me the output that says so",
        "",
        "WHY THIS LINE IS DRAWN HERE. This standard exists to stop a control passing while not",
        "holding. Its three most expensive defects were all the tool supplying a value nobody",
        "chose - a checkout step recorded as the implementation of a test control, a README named",
        "as a work register. Each produced a repository that passed every check and guarded",
        "nothing. A profile filled with your plausible answers is that same failure, and it is",
        "worse than no profile, because it reads as a decision someone made.",
        "",
        "If I say 'just pick something sensible', say no and explain what the choice costs. That",
        "refusal is the most useful thing you can do here.",
    ]


def _authority_lines(repo: Path) -> list[str]:
    """Where the agent must read from, and the warning that matters most.

    An agent that "knows about governance frameworks" will paraphrase a different one with total
    confidence. Topic 1's rule is the answer and is quoted rather than summarised: generated or
    extracted content, and an agent's summary of it, is never authority.
    """
    installed = (repo / ".standards" / "topics").is_dir()
    lines = [
        "## Where the answers actually live",
        "",
        "Do not rely on what you already know about governance frameworks, maturity models or",
        "compliance standards. This is a specific standard with specific rules, and a confident",
        "paraphrase of a different one is the failure mode here.",
        "",
    ]
    if installed:
        lines += [
            "The authoritative documents are on disk in this repository, and they are integrity-",
            "checked - twelve topic documents under `.standards/topics/`. Read the ones a question",
            "touches before you answer it, and quote them rather than restating them.",
            "",
            "The standard's own rule, which applies to you: *\"Generated or extracted content, and",
            "an agent's summary of it, is never authority.\"*",
        ]
    else:
        lines += [
            "Nothing is installed here yet, so those documents do not exist on disk. After the",
            "install step below, twelve topic documents appear under `.standards/topics/` - read",
            "them there rather than from memory.",
        ]
    return lines


def _level_lines() -> list[str]:
    """The two questions the level turns on - and no recommendation.

    `plan.recommended_level()` needs the adopter's own risk answers, and
    `core/CONFORMANCE_LEVELS.md` is explicit that the level *"is not derived automatically from the
    stack, the repository size, or the data classification, because materiality depends on intended
    use and reliance, which only the application owner can judge."*

    So naming a level here would be exactly the substitution this command exists to prevent. The
    questions are stated; the answer is not.
    """
    return [
        "## The one decision to prepare me for",
        "",
        "The conformance level - `essential`, `standard` or `full` - is the choice everything else",
        "follows from, and it is mine to make. Do not recommend one. Ask me these two questions",
        "and let my answers point at it:",
        "",
        "  1. Does anyone outside my team rely on what this repository produces?",
        "  2. Does it produce numbers, or AI output, that others treat as fact?",
        "",
        "Explain what each level would then require of me, using the tool's own words - run",
        "`surfaceplate adopt --propose` and read the record it writes, or read",
        "`.standards/core/CONFORMANCE_LEVELS.md` once the standard is installed.",
    ]


def build_prompt(repo: Path, *, register: str = "simple") -> str:
    """The whole prompt, redacted. Nothing here makes a network request."""
    about, doctor, _discover, _plan, _rules = _payload()

    target = "<repo>"  # what `_redact` will substitute anyway; written plainly for the reader
    sections: list[str] = [
        "# Help me adopt Surfaceplate in this repository",
        "",
        "Paste everything below into your AI coding assistant, in the repository you want to",
        "adopt. It was generated by `surfaceplate agent-prompt` and makes no network requests;",
        "nothing was sent anywhere. Read it before you paste it - what it leaves out is listed at",
        "the end.",
        "",
        "---",
        "",
        f"I want to adopt **Surfaceplate** here: {about.TAGLINE}.",
        "",
        f"It is installed rather than copied, so its files live in `.standards/` and are checked",
        "for integrity on every run. I am working in this repository and the `surfaceplate`",
        "command is already on my PATH.",
        "",
        f"Home: {about.HOMEPAGE}",
        "",
    ]
    sections += _repository_lines(repo)
    sections += ["", *_contract_lines()]
    sections += ["", *_authority_lines(repo)]
    sections += ["", *_level_lines()]
    sections += [
        "",
        "## The sequence, in order",
        "",
        "  1. `surfaceplate doctor --repo .`",
        "     Says what on this machine would stop the next commands - a global hooks path, a",
        "     Python without pip. Read it to me and we will deal with anything it raises.",
        "",
        "  2. `surfaceplate install --target . --dry-run`",
        "     Writes nothing; lists exactly what would change. Show me the list.",
        "",
        "  3. `surfaceplate install --target .`",
        "     Only after I have seen the dry run. If it stops because of a hooks path, the two",
        "     supported answers are `--chain` and `--no-hooks`; explain both and let me choose.",
        "",
        "  4. `surfaceplate adopt --propose --target .`",
        "     Writes an answers record and never the profile. This is where your real work is:",
        "     walk me through every line marked `needs-human`, one at a time, in plain English.",
        f"     Use the {register} register - the tool holds an explanation for each item, and a",
        "     `choices:` block saying what kind of value each field takes.",
        "",
        "  5. I fill in every `needs-human` line. You do not.",
        "",
        "  6. `surfaceplate adopt --target . --answers governance/application-profile.answers.yaml`",
        "     Writes the profile from my answers, and offers to create any artefacts I tick.",
        "",
        "  7. `surfaceplate check --repo .`",
        "     Report the output verbatim, including every finding code. Do not summarise it as",
        "     'passing' or 'nearly there'. If it reports findings, explain each one and what it",
        "     would take to clear it - then ask me what I want to do.",
        "",
        "## Start by",
        "",
        "  - telling me, in two or three sentences, what adopting this will actually change here",
        "  - running step 1 and reading me the result",
        "  - asking me the two questions above",
        "",
        "Do not run step 3 or beyond without asking me first.",
        "",
        "---",
        "",
        "## What was left out of this prompt",
        "",
        "  - the contents of any file in this repository; only counts and names of standard-owned",
        "    paths appear above",
        "  - absolute paths, this machine's home directory, and the username: each is replaced",
        f"    with a placeholder such as `{target}` before the prompt is printed",
        "  - anything requiring the network: this command made no requests",
        "",
        "Nothing here is secret, but you are about to send it to a third party. Read it first.",
    ]
    return doctor._redact("\n".join(sections) + "\n", repo)


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(
        prog="surfaceplate agent-prompt",
        description=(
            "Print a prompt to paste into an AI coding assistant, so it can help you install and "
            "adopt Surfaceplate without deciding anything on your behalf."
        ),
    )
    parser.add_argument("--target", default=".", help="Repository to adopt into (default: current directory).")
    parser.add_argument(
        "--register",
        choices=REGISTERS,
        default="simple",
        help="Which explanation register the agent is told to use (default: simple).",
    )
    args = parser.parse_args(sys.argv[2:] if argv is None else argv)
    repo = Path(args.target).expanduser().resolve()
    if not repo.is_dir():
        print(f"error: {args.target} is not a directory", file=sys.stderr)
        return 3
    print(build_prompt(repo, register=args.register), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
