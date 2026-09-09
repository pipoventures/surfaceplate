#!/usr/bin/env python3
"""Fail if the identifier registers disagree with reality.

This is the remedy for F11, which `DR-8` raised and left open: *"Nothing enforces that a newly
added finding code is unique, contiguous, or documented."*

The case for a check rather than more care is that care demonstrably did not work. On
2026-08-31, `org/FINDINGS.md` carried **three** false statements at once, all written by people
reading the file at the time:

- `F5`'s entry said `INSTALL.md:29` still held a non-resolving clone URL. It had been corrected.
- The code-space table said the checker emitted `SP001`-`SP043`. `SP046` and `SP047` existed,
  added by the same session that was editing the file.
- The `ACT-<n>` row said there was "no register behind it". `activity/register.md` existed.

None of these is a typo. Each was true when written and became false when something else
changed, which is precisely the class of error a reader cannot catch by being careful: nothing
about a stale sentence looks different from a current one.

WHAT THIS CHECKS, and equally what it does not: it compares *declarations against reality*. It
cannot tell whether a finding's prose is still accurate - that is not mechanically decidable,
and `F5`'s stale entry would have survived this check. What it makes impossible is a code that
exists in one register and not the other.

Usage:
    python tests/check_code_registers.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "org" / "FINDINGS.md"
CHECKER = ROOT / "surfaceplate" / "check_conformance.py"

# A code is emitted where a Finding is constructed. Deliberately not "any SPnnn literal in the
# file": the checker names other codes in remedy prose ("see SP034"), and counting those would
# report codes that are documented rather than emitted - the opposite of what this checks.
EMITTED = re.compile(r"Finding\(\s*\"(SP\d+)\"")

DECLARATION = re.compile(r"```text\n(emitted:.*?)```", re.DOTALL)
RANGE = re.compile(r"SP(\d+)(?:-SP(\d+))?")

# `F70` / `F71` (`ACT-045`): the front door is checked, not trusted. Every relative link and every
# path-like code span in README.md and INSTALL.md must resolve - in this repository, or, for a
# `.standards/` path, in an installed checkout (which is the installer's payload, by
# construction); the README's version line equals `surfaceplate/VERSION`; the gate and control
# counts the documents state equal the catalogue; and every code the checker emits is in the
# generated catalogue below, which this script writes with `--write` and checks otherwise.
README = ROOT / "README.md"
INSTALL = ROOT / "INSTALL.md"
VERSION_FILE = ROOT / "surfaceplate" / "VERSION"
LEVELS_DOC = ROOT / "surfaceplate" / "core" / "CONFORMANCE_LEVELS.md"
CATALOGUE_BEGIN = "<!-- BEGIN GENERATED: finding codes (tests/check_code_registers.py --write) -->"
CATALOGUE_END = "<!-- END GENERATED: finding codes -->"
# `DR-76`, surface 4 of `DR-69`. What each level requires, arranged by the twelve topics rather
# than as a flat list of controls - GENERATED from the checker's own levels and `rules.CONTROL_TOPICS`,
# so the reader gets the topic view and neither structure restates the other.
TOPICS_BEGIN = "<!-- BEGIN GENERATED: levels by topic (tests/check_code_registers.py --write) -->"
TOPICS_END = "<!-- END GENERATED: levels by topic -->"
# `DR-69`: "twelve" names three different things in the shipped corpus - twelve controls, twelve
# topics, twelve cross-application control principles. Every current use is qualified; this keeps
# it that way. Bare uses only: "the twelve", "twelve." and "twelve," - a qualified "twelve topic
# documents" is exactly what is wanted and must not be flagged.
BARE_TWELVE = re.compile(r"\btwelve(?=[\s]*[.,;)]|\s+(?:are|is|were|of\b))", re.IGNORECASE)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")
PATHISH = re.compile(r"`((?:\.standards|\.github|surfaceplate|org|audit|core|prompts|tests|scripts|docs)/[A-Za-z0-9_./*-]+)`")
# `F130`: a `name==version` pin, wherever it is written. Anchored on a digit so that a comparison
# written in prose or code ("x == y") cannot be read as a pin.
PINNED = re.compile(r"([A-Za-z][A-Za-z0-9_.-]*)==([0-9][A-Za-z0-9_.]*)")
# `F128`: the same treatment, applied to what the payload says about itself - see
# `payload_pointer_checks`. Only pointers that name an installed destination are resolved.
PAYLOAD_POINTER = re.compile(
    r"`((?:\.standards/[A-Za-z0-9_./*-]+)"
    r"|(?:\.claude/(?:rules|skills)/[A-Za-z0-9_./*-]+)"
    r"|(?:\.github/(?:instructions|skills)/[A-Za-z0-9_./*-]+)"
    r"|(?:[A-Za-z0-9_.*-]+\.instructions\.md))`"
)
# A comment may sit between the code and the title (SP038's does), so it is skipped.
TITLE = re.compile(r"Finding\(\s*\"(SP\d{3})\",\s*(?:#[^\n]*\n\s*)*((?:f?\"[^\"]*\"\s*)+)")
PLACEHOLDERS = {
    "{gate_id}": "<gate>", "{control_id}": "<control>", "{level}": "<level>", "{rel}": "<file>",
    "{label}": "<record>", "{reference}": "<reference>", "{scanner}": "<scanner>", "{status}": "<status>",
    "{path}": "<path>", "{name}": "<name>",
}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "nineteen": 19}

CHECKS = 0
FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(f"{label}{': ' + detail if detail else ''}")


def parse_codes(spec: str) -> set[int]:
    """Expand 'SP001-SP035, SP037' into the integers it names."""
    codes: set[int] = set()
    for lo, hi in RANGE.findall(spec):
        start = int(lo)
        end = int(hi) if hi else start
        if end < start:
            raise SystemExit(f"declared range SP{lo}-SP{hi} runs backwards")
        codes.update(range(start, end + 1))
    return codes


def declared_space(text: str) -> dict[str, set[int]]:
    match = DECLARATION.search(text)
    if not match:
        raise SystemExit(
            "org/FINDINGS.md has no ```text block declaring the SP code space. The check "
            "derives the expected codes from that block rather than restating them; without "
            "it there is nothing to compare the checker against."
        )
    space: dict[str, set[int]] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        key, _, spec = line.partition(":")
        space[key.strip()] = parse_codes(spec)
    for required in ("emitted", "gap", "reserved"):
        if required not in space:
            raise SystemExit(f"the SP declaration block has no '{required}:' line")
    return space


def _catalogue_rows(checker_text: str) -> list[tuple[str, str]]:
    """`(code, titles)` for every code the checker constructs a `Finding` for, titles read from
    the source with their f-string placeholders shown as `<gate>`, `<control>` and so on."""
    titles: dict[str, list[str]] = {}
    for code, raw in TITLE.findall(checker_text):
        text = "".join(re.findall(r"\"([^\"]*)\"", raw))
        for placeholder, shown in PLACEHOLDERS.items():
            text = text.replace(placeholder, shown)
        text = re.sub(r"\{[a-z_]+\}", "<value>", text)
        if text not in titles.setdefault(code, []):
            titles[code].append(text)
    return [(code, "; ".join(titles[code])) for code in sorted(titles)]


def render_catalogue(checker_text: str) -> str:
    rows = _catalogue_rows(checker_text)
    lines = [
        CATALOGUE_BEGIN,
        "",
        f"{len(rows)} codes. Generated from the checker's own source by `tests/check_code_registers.py --write`;",
        "the same script fails in CI when this table and the checker disagree. A code's title is what",
        "the report prints; `<gate>`, `<control>`, `<file>` stand for the name the report fills in.",
        "",
        "| Code | What it reports |",
        "|---|---|",
    ]
    for code, title in rows:
        lines.append(f"| `{code}` | {title} |")
    lines += ["", CATALOGUE_END]
    return "\n".join(lines)


def render_levels_by_topic(checker) -> str:
    """What each level requires, by topic. Generated, never hand-maintained.

    `DR-76` decided that surface 4 of `DR-69` is a VIEW and not a restructuring, for the reason
    `DR-71` gave about the profile: the goal was never nesting, it was that a reader sees twelve
    named subjects. `CONFORMANCE_LEVELS` stays a flat map of level -> controls, read by 58 places
    that all ask "is this control required here" and none of which ask about topics. Keying it by
    topic would hold `rules.CONTROL_TOPICS` twice inside the framework, which is `F130`'s shape.
    """
    import sys

    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import rules  # noqa: E402

    levels = ("essential", "standard", "full")
    lines = [
        TOPICS_BEGIN,
        "",
        "Generated by `tests/check_code_registers.py --write` from the checker's own",
        "`CONFORMANCE_LEVELS` and the topic map in `rules.py`; the same script fails in CI when this",
        "table and the code disagree. A topic with no row requires no *selectable control* at any",
        "level by this axis - which is not the same as requiring nothing, since the nineteen",
        "prerequisite gates are a separate obligation with their own catalogue grouping.",
        "",
        "| Topic | Every level | `essential` | `standard` | `full` |",
        "|---|---|---|---|---|",
    ]
    # The three baseline controls are required at EVERY level and are therefore absent from
    # `CONFORMANCE_LEVELS`. Omitting them made topics 3 and 8 read as four em-dashes - a topic
    # that in fact obliges every adopter, shown as obliging none. They get their own column.
    baseline = sorted(checker.BASELINE_CONTROLS) if hasattr(checker, "BASELINE_CONTROLS") else [
        "actual_diff_review", "agent_work_packets", "secret_hygiene"
    ]
    for number in sorted(rules.TOPIC_NAMES):
        controls = sorted(c for c, topic in rules.CONTROL_TOPICS.items() if topic == number)
        if not controls:
            continue
        always = [c for c in controls if c in baseline]
        cells = [", ".join(f"`{c}`" for c in always) if always else "—"]
        for level in levels:
            here = [c for c in controls if c in checker.CONFORMANCE_LEVELS[level]]
            cells.append(", ".join(f"`{c}`" for c in here) if here else "—")
        if set(cells) == {"—"}:
            continue  # a topic this axis says nothing about; the gates still may
        lines.append(f"| {number}. {rules.TOPIC_NAMES[number]} | " + " | ".join(cells) + " |")
    lines += ["", TOPICS_END]
    return "\n".join(lines)


def _installed_targets() -> set[str]:
    import sys

    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import install_standard  # noqa: E402

    payload = install_standard.build_payload(ROOT / "surfaceplate")
    targets = set(payload)
    # Written by the installer without being payload: the record, the profile it creates from
    # the template, and the two files it creates when absent and manages a block in.
    targets |= {install_standard.PROFILE_PATH, ".standards/INSTALL.json", ".github/copilot-instructions.md", "AGENTS.md"}
    return targets


def _resolves_installed(path: str, targets: set[str]) -> bool:
    import fnmatch

    bare = path.rstrip("/")
    if "*" in bare:
        return any(fnmatch.fnmatch(t, bare) for t in targets)
    return any(t == bare or t.startswith(bare + "/") for t in targets)


def front_door_checks(checker_text: str, write: bool) -> None:
    import sys

    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import check_conformance  # noqa: E402

    targets = _installed_targets()
    for doc in (README, INSTALL):
        text = doc.read_text(encoding="utf-8")
        for target in sorted(set(LINK.findall(text))):
            if "://" in target or target.startswith("mailto:"):
                continue
            check(f"{doc.name}: link `{target}` resolves in this repository", (doc.parent / target).exists())
        for path in sorted(set(PATHISH.findall(text))):
            if path.startswith((".standards/", ".github/")):
                check(f"{doc.name}: `{path}` exists in an installed checkout", _resolves_installed(path, targets))
            else:
                check(f"{doc.name}: `{path}` exists in this repository", (ROOT / path.replace("*", "")).exists() or (ROOT / path.split("*")[0]).exists())
    readme = README.read_text(encoding="utf-8")
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    stated = re.search(r"\*\*Version ([0-9][0-9.]*)\.\*\*", readme)
    check("README.md states the version surfaceplate/VERSION holds", bool(stated) and stated.group(1) == version,
          f"README says {stated.group(1) if stated else 'nothing'}, VERSION is {version}")
    gates = len(check_conformance.GATE_CATALOGUE)
    for doc in (README, INSTALL, LEVELS_DOC, ROOT / "surfaceplate" / "core" / "PREREQUISITE_GATES.md"):
        text = doc.read_text(encoding="utf-8")
        for number in re.findall(r"\b(\d+)(?:-gate catalogue| prerequisite gates)\b", text):
            check(f"{doc.name}: '{number} gates' is the catalogue's count", int(number) == gates, f"the catalogue holds {gates}")
    levels = LEVELS_DOC.read_text(encoding="utf-8")
    controls = len(check_conformance.CONFORMANCE_LEVELS["full"]) + 3
    checked = len(check_conformance.VERIFIED_CONTROLS | {"secret_hygiene"})
    for ten, twelve in re.findall(r"\*\*(\w+) of the (\w+) controls this framework defines are checked\*\*", levels):
        check("CONFORMANCE_LEVELS.md: the checked-controls sentence matches the checker", WORDS.get(ten.lower()) == checked and WORDS.get(twelve.lower()) == controls,
              f"document says {ten} of {twelve}; checker has {checked} of {controls}")
    check("CONFORMANCE_LEVELS.md does not also claim every control is checked",
          "Every control is checked" not in levels and "Nothing is declared-only" not in levels.split("*This paragraph read")[0])
    # `DR-76`: the levels-by-topic view, same generate-and-check pattern as the catalogue below.
    topic_view = render_levels_by_topic(check_conformance)
    tbegin, tend = levels.find(TOPICS_BEGIN), levels.find(TOPICS_END)
    present_topics = levels[tbegin:tend + len(TOPICS_END)] if tbegin >= 0 and tend >= 0 else ""
    if write and present_topics != topic_view:
        if tbegin >= 0:
            levels = levels[:tbegin] + topic_view + levels[tend + len(TOPICS_END):]
        else:
            levels = levels.rstrip("\n") + "\n\n## What each level requires, by topic\n\n" + topic_view + "\n"
        LEVELS_DOC.write_text(levels, encoding="utf-8")
        present_topics = topic_view
        print(f"wrote the levels-by-topic view into {LEVELS_DOC.relative_to(ROOT)}")
    check("CONFORMANCE_LEVELS.md's levels-by-topic view matches the checker and the topic map",
          present_topics == topic_view, "run: python tests/check_code_registers.py --write")

    # `DR-69`: "twelve" names three different things in the shipped corpus - controls, topics, and
    # cross-application control principles. A bare "the twelve" is therefore unreadable, and the
    # collision is the kind that only becomes visible once someone writes the ambiguous sentence.
    for path in sorted((ROOT / "surfaceplate" / "standard" / "topics").glob("*.md")) + [
        LEVELS_DOC,
        ROOT / "surfaceplate" / "core" / "PREREQUISITE_GATES.md",
        ROOT / "surfaceplate" / "core" / "CONTROL_PRINCIPLES.md",
        ROOT / "surfaceplate" / "standard" / "conformance-block.md",
    ]:
        if not path.exists():
            continue
        bare = BARE_TWELVE.findall(path.read_text(encoding="utf-8"))
        check(f"{path.name}: 'twelve' is never used bare - it names three different sets here",
              not bare, f"{len(bare)} bare use(s)")

    expected = render_catalogue(checker_text)
    begin, end = levels.find(CATALOGUE_BEGIN), levels.find(CATALOGUE_END)
    present = levels[begin:end + len(CATALOGUE_END)] if begin >= 0 and end >= 0 else ""
    if write and present != expected:
        if begin >= 0:
            levels = levels[:begin] + expected + levels[end + len(CATALOGUE_END):]
        else:
            levels = levels.rstrip("\n") + "\n\n## Every finding code the checker can report\n\n" + expected + "\n"
        LEVELS_DOC.write_text(levels, encoding="utf-8")
        present = expected
        print(f"wrote the finding-code catalogue into {LEVELS_DOC.relative_to(ROOT)}")
    check("every code the checker emits is in the generated catalogue in CONFORMANCE_LEVELS.md, and nothing else is",
          present == expected, "run: python tests/check_code_registers.py --write")


def dependency_pin_checks() -> None:
    """`F130`: the same version is pinned in five places and nothing compared them.

    `pyproject.toml` is the authority for what this package depends on. The self-check workflow
    installs its own hard-coded copy of that list; `standards-conformance.yml` installs the two
    runtime pins; the **payload's** copy of that workflow installs them into every adopting
    repository; and `INSTALL.md` tells a reader to install `textual` by version. Five declarations
    of one fact.

    Found when Dependabot's pytest bump edited `pyproject.toml` alone and every suite passed:
    CI had installed 8.4.2 from its own line and never saw the change under review. A dependency
    change was about to be judged by a run that did not install it - and the payload copy makes the
    same drift reach adopters, whose CI would install a set the package does not declare.

    LIMIT, stated rather than implied: this compares versions for packages `pyproject.toml`
    declares. A pin elsewhere for something it does not declare (`build` in `publish.yml`, a
    publish-time tool) is not checked, because there is no authority here to compare it against.
    """
    import tomllib

    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = data["project"]
    declared: dict[str, str] = {}
    groups = [project.get("dependencies", [])] + list(project.get("optional-dependencies", {}).values())
    for group in groups:
        for spec in group:
            m = PINNED.fullmatch(spec.strip())
            if m:
                declared[m.group(1).lower().replace("_", "-")] = m.group(2)
    check("pyproject.toml declares exactly-pinned dependencies to compare against", bool(declared))

    files = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    files += sorted((ROOT / "surfaceplate" / "standard" / ".github" / "workflows").glob("*.yml"))
    files += [ROOT / "INSTALL.md", ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "scripts" / "front_door.sh"]
    for path in files:
        if not path.exists():
            continue
        for name, version in PINNED.findall(path.read_text(encoding="utf-8")):
            key = name.lower().replace("_", "-")
            if key not in declared:
                continue
            check(
                f"{path.relative_to(ROOT).as_posix()}: {name}=={version} matches pyproject.toml",
                version == declared[key],
                f"pyproject.toml pins {declared[key]}",
            )


def payload_pointer_checks(targets: set[str]) -> None:
    """`F128`: the front door is checked and the payload's own documents were not.

    The `change` skill, shipped to every adopter, said *"the registered activity ID (see
    `activity.instructions.md`)"* - a file the twelve-topic restructure stopped writing three
    surfaces earlier, and a Copilot-only emitted filename before that. Nothing failed, because no
    check reads what the payload says about itself. `F50` is the same defect one layer out: a
    hand-off command naming a file deleted three packets earlier, caught only when someone ran it.

    Narrow on purpose. It resolves exactly the pointers that name an installed destination - an
    agent-instruction filename, a rules file, a skill, or a `.standards/` path. A payload document
    naming `README.md` or a stack's own file is naming the adopter's tree, which this cannot and
    must not try to resolve.
    """
    import sys

    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import install_standard  # noqa: E402

    payload = install_standard.build_payload(ROOT / "surfaceplate")
    for dest in sorted(payload):
        if not dest.endswith(".md"):
            continue
        source = payload[dest]
        text = source.read_text(encoding="utf-8") if isinstance(source, Path) else source
        for pointer in sorted(set(PAYLOAD_POINTER.findall(text))):
            # A bare `x.instructions.md` can only mean the Copilot destination; that it reads as a
            # bare filename is part of what made this defect survive.
            qualified = pointer if "/" in pointer else f".github/instructions/{pointer}"
            check(
                f"payload {dest}: `{pointer}` names a file the installer writes",
                _resolves_installed(qualified, targets),
                "no installed destination matches it",
            )


def main() -> int:
    import sys

    write = "--write" in sys.argv[1:]
    findings_text = FINDINGS.read_text(encoding="utf-8")
    checker_text = CHECKER.read_text(encoding="utf-8")
    front_door_checks(checker_text, write)
    payload_pointer_checks(_installed_targets())
    dependency_pin_checks()

    # ---- SP codes: declaration against the code that emits them ----
    space = declared_space(findings_text)
    emitted = {int(code[2:]) for code in EMITTED.findall(checker_text)}

    check(
        "every emitted SP code is declared",
        emitted <= space["emitted"],
        ", ".join(f"SP{n:03d}" for n in sorted(emitted - space["emitted"])),
    )
    check(
        "every declared SP code is emitted",
        space["emitted"] <= emitted,
        ", ".join(f"SP{n:03d}" for n in sorted(space["emitted"] - emitted)),
    )
    # The SDS036 defect: a code documented but implemented by nothing, for releases, unnoticed.
    check(
        "no reserved SP code is quietly in use",
        not (space["reserved"] & emitted),
        ", ".join(f"SP{n:03d}" for n in sorted(space["reserved"] & emitted)),
    )
    check(
        "no declared gap is in use",
        not (space["gap"] & emitted),
        ", ".join(f"SP{n:03d}" for n in sorted(space["gap"] & emitted)),
    )
    # An undeclared hole is the thing that hides a code nobody remembers removing.
    whole = space["emitted"] | space["gap"] | space["reserved"]
    holes = set(range(1, max(whole) + 1)) - whole
    check(
        "the SP space has no undeclared hole",
        not holes,
        ", ".join(f"SP{n:03d}" for n in sorted(holes)),
    )

    # ---- F codes: the register against itself ----
    rows = [int(m) for m in re.findall(r"^\| F(\d+) \|", findings_text, re.MULTILINE)]
    bodies = [int(m) for m in re.findall(r"^## F(\d+) ", findings_text, re.MULTILINE)]

    check("the live register is not empty", bool(rows))
    check(
        "no F code is indexed twice",
        len(rows) == len(set(rows)),
        ", ".join(f"F{n}" for n in sorted({n for n in rows if rows.count(n) > 1})),
    )
    check(
        "no F code has two body sections",
        len(bodies) == len(set(bodies)),
        ", ".join(f"F{n}" for n in sorted({n for n in bodies if bodies.count(n) > 1})),
    )
    check(
        "F codes are contiguous from F1",
        set(rows) == set(range(1, max(rows) + 1)) if rows else False,
        ", ".join(f"F{n}" for n in sorted(set(range(1, max(rows) + 1)) - set(rows))) if rows else "",
    )
    # A body with no index entry is a finding that exists but cannot be found from the table -
    # the register's own summary would understate what it holds.
    check(
        "every body section is indexed in the table",
        set(bodies) <= set(rows),
        ", ".join(f"F{n}" for n in sorted(set(bodies) - set(rows))),
    )
    # `F72`: ten findings said Open in the body and Closed in the index, and nothing compared
    # them. The index row's status column and the body's `**Severity: ... <status>.**` line
    # must agree on Open versus Closed; a partial closure ("Closed for deferrals; open for
    # gate exceptions") counts as whichever word it leads with.
    index_status = {
        int(m.group(1)): m.group(2).strip().strip("*").strip()
        for m in re.finditer(r"^\| F(\d+) \|[^|]*\|[^|]*\| ([^|]*)\|", findings_text, re.MULTILINE)
    }
    body_status = {
        int(m.group(1)): m.group(2).strip()
        for m in re.finditer(r"^## F(\d+) [^\n]*\n\n\*\*Severity: [^.]*\. ([^*]*)\*\*", findings_text, re.MULTILINE)
    }

    def word(status: str) -> str:
        head = status.lower()
        return "closed" if head.startswith("closed") else "open" if head.startswith("open") else "?"

    disagree = sorted(
        n for n in body_status if n in index_status and word(index_status[n]) != word(body_status[n])
    )
    check(
        "every finding's body status agrees with its index status (F72)",
        not disagree,
        ", ".join(f"F{n} (index {word(index_status[n])}, body {word(body_status[n])})" for n in disagree),
    )
    unparsed = sorted(n for n in body_status if word(body_status[n]) == "?")
    check(
        "every body status line leads with Open or Closed",
        not unparsed,
        ", ".join(f"F{n}: {body_status[n][:40]!r}" for n in unparsed),
    )

    if FAILURES:
        print("CODE_REGISTERS=FAIL")
        print()
        for failure in FAILURES:
            print(f"  {failure}")
        print()
        print("Something states a fact about this repository that this repository does not have.")
        print("Correct the statement, or the code it describes, so the two agree - a register or a")
        print("document that describes what is not there is worse than none: it reads as")
        print("authoritative and is not. For a payload pointer, the document ships to every")
        print("adopter, so the wrong name is theirs to trip over as well as yours.")
        return 1

    # Reported so that "the registers agree" is distinguishable from "nothing was compared",
    # the defect recorded as F3.
    print(
        f"CODE_REGISTERS=PASS  ({CHECKS} checks; "
        f"{len(space['emitted'])} SP codes, {len(rows)} F codes)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
