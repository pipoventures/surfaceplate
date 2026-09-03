#!/usr/bin/env python3
"""Build the independent review packet: one self-contained HTML page from its tracked source.

    python scripts/build_review_packet.py --ref <published commit> \\
        --sdist-url <url> --sdist-sha256 <hex> --wheel-sha256 <hex> \\
        --publish-run <run id> [--ci-run <run id>] [--zip dist/surfaceplate-<version>.zip] \\
        [--adopter-pin <hex>] [--out dist/INDEPENDENT_REVIEW_PACKET-<version>.html]

`DR-64` / `ACT-060`. The packet takes two human actions to an outside party: `H4`, the independent
recomputation of the framework anchor that closes `F6`, and `H6`, the independent audit. Its text
lives in `audit/INDEPENDENT_REVIEW_PACKET.md`, tracked, with `{{token}}` placeholders that this
script fills from the published release. The page it writes is a build output, like
`EVIDENCE_BUNDLE.md`, and is not committed; its SHA-256 is printed so the maintainer can quote it
in the message that carries it, since a file cannot contain its own hash.

Three things this script refuses, each a way the packet could mislead the reviewer:

- an unresolved `{{token}}` in the output (a blank where a value should be);
- a `--zip` whose inner `surfaceplate/MANIFEST.sha256` does not hash to the expected anchor (an
  archive built from a tree other than the published one - the shape found while designing this,
  when the zip in `dist/` came from a branch);
- an expected anchor computed from the working tree when `--ref` names a commit (the anchor is
  read from `git show <ref>:surfaceplate/MANIFEST.sha256`, never from whatever is on disk).

No dependency beyond the standard library. The Markdown renderer covers the subset the two source
documents use - headings, paragraphs, lists, block quotes, fenced code, pipe tables, inline code,
bold, italics and links - and passes anything else through as a paragraph, escaped.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import html
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "surfaceplate"))

import install_standard  # noqa: E402  (framework_anchor, normalise, sha256_text)

SOURCE = ROOT / "audit" / "INDEPENDENT_REVIEW_PACKET.md"
PROMPT = ROOT / "audit" / "GEMINI_ADVERSARIAL_REVIEW_PROMPT.md"
SCOPE = ROOT / "audit" / "AUDIT_SCOPE.md"
PROMPT_SLICE_FROM = "## Required evidence handling"
REPO_URL = "https://github.com/pipoventures/surfaceplate"
TOKEN = re.compile(r"\{\{([a-z0-9_]+)\}\}")


# ---------------------------------------------------------------------------------------------
# the values
# ---------------------------------------------------------------------------------------------


def version() -> str:
    return (ROOT / "surfaceplate" / "VERSION").read_text(encoding="utf-8").strip()


def anchor_at(ref: str | None) -> tuple[str, str]:
    """`(anchor, commit)`: the anchor of the manifest at `ref` (a commit, read with `git show`), or
    of the working tree when `ref` is None (the mode the test uses)."""
    if ref is None:
        value = install_standard.framework_anchor(ROOT / "surfaceplate")
        if value is None:
            raise SystemExit("the working tree has no surfaceplate/MANIFEST.sha256")
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        return value, head
    shown = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{ref}:surfaceplate/MANIFEST.sha256"], capture_output=True, text=True
    )
    if shown.returncode != 0:
        raise SystemExit(f"cannot read surfaceplate/MANIFEST.sha256 at {ref}: {shown.stderr.strip()}")
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", f"{ref}^{{commit}}"], capture_output=True, text=True, check=True).stdout.strip()
    return install_standard.sha256_text(install_standard.normalise(shown.stdout)), commit


def manifest_entries_at(ref: str | None) -> int:
    if ref is None:
        text = (ROOT / "surfaceplate" / "MANIFEST.sha256").read_text(encoding="utf-8")
    else:
        text = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:surfaceplate/MANIFEST.sha256"], capture_output=True, text=True, check=True).stdout
    return sum(1 for line in text.splitlines() if line.strip())


def inspect_zip(path: Path, expected_anchor: str) -> tuple[str, str]:
    """`(zip sha256, inner anchor)`; refuses an archive whose inner manifest is not the expected tree."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with zipfile.ZipFile(path) as archive:
        names = [n for n in archive.namelist() if n.endswith("/surfaceplate/MANIFEST.sha256")]
        if len(names) != 1:
            raise SystemExit(f"{path}: expected exactly one surfaceplate/MANIFEST.sha256 entry, found {len(names)}")
        inner = install_standard.sha256_text(install_standard.normalise(archive.read(names[0]).decode("utf-8")))
    if inner != expected_anchor:
        raise SystemExit(
            f"REFUSING: {path.name}'s inner manifest hashes to {inner[:12]}… but the published release's "
            f"anchor is {expected_anchor[:12]}…; this archive was built from a different tree. Rebuild it "
            "from the published commit before sending it to a reviewer."
        )
    return digest, inner


# ---------------------------------------------------------------------------------------------
# a small Markdown renderer
# ---------------------------------------------------------------------------------------------


def _inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", out)
    return out


def render_markdown(text: str) -> str:
    """The subset the sources use. Raw HTML blocks (the form) pass through when a line starts `<div`
    or `<section`, until the matching closing line."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    list_stack: list[tuple[str, int]] = []  # (tag, indent)

    def close_lists(to_indent: int = -1) -> None:
        while list_stack and list_stack[-1][1] > to_indent:
            out.append(f"</{list_stack[-1][0]}>")
            list_stack.pop()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            close_lists()
            i += 1
            continue
        if stripped.startswith(("<div", "<section", "<script", "<style")):
            # A raw block the form supplies: passed through to its matching close tag.
            close_lists()
            tag = stripped[1:].split()[0].rstrip(">")
            depth = 0
            while i < len(lines):
                out.append(lines[i])
                depth += lines[i].count(f"<{tag}") - lines[i].count(f"</{tag}>")
                i += 1
                if depth <= 0:
                    break
            continue
        if stripped.startswith("```"):
            close_lists()
            i += 1
            code: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(code), quote=False) + "</code></pre>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            close_lists()
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue
        if stripped.startswith("|"):
            close_lists()
            rows: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows if not re.match(r"^\|[\s:|-]+\|$", r)]
            if cells:
                head, body = cells[0], cells[1:]
                out.append("<table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in head) + "</tr></thead><tbody>")
                for row in body:
                    out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in row) + "</tr>")
                out.append("</tbody></table>")
            continue
        if stripped.startswith(">"):
            close_lists()
            quote: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            out.append("<blockquote><p>" + _inline(" ".join(quote)) + "</p></blockquote>")
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if m:
            indent = len(m.group(1))
            tag = "ol" if m.group(2)[0].isdigit() else "ul"
            if not list_stack or indent > list_stack[-1][1]:
                out.append(f"<{tag}>")
                list_stack.append((tag, indent))
            else:
                close_lists(indent)
                if not list_stack or list_stack[-1][1] != indent:
                    out.append(f"<{tag}>")
                    list_stack.append((tag, indent))
            item = [m.group(3)]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(\s*)([-*]|\d+\.)\s+", lines[i]) and (len(lines[i]) - len(lines[i].lstrip())) > indent and not lines[i].strip().startswith(("```", "|", "#")):
                item.append(lines[i].strip())
                i += 1
            out.append(f"<li>{_inline(' '.join(item))}</li>")
            continue
        close_lists()
        para = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(\s*)([-*]|\d+\.)\s+|^#{1,6}\s|^```|^\||^>|^<div|^<section|^<script|^<style", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{_inline(' '.join(para))}</p>")
    close_lists()
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# the composed parts: the scope rows and the form
# ---------------------------------------------------------------------------------------------


def scope_criteria() -> list[str]:
    text = SCOPE.read_text(encoding="utf-8")
    return [line.strip()[2:].rstrip(";.") for line in text.splitlines() if line.strip().startswith("- ")]


def scope_rows_markdown(criteria: list[str]) -> str:
    rows = ["| # | the kit is… | score | justification (cite a file) |", "|---|---|---|---|"]
    for n, c in enumerate(criteria, start=1):
        rows.append(f"| {n} | {c} | Holds / Gap / Strong | |")
    return "\n".join(rows)


def form_html(values: dict[str, str], criteria: list[str]) -> str:
    """The fillable form and the composer script. Plain HTML; one inline script; no network."""
    v = {k: html.escape(str(val), quote=True) for k, val in values.items()}
    criterion_rows = "\n".join(
        f'<tr><td>{n}</td><td>{html.escape(c)}</td><td><select data-crit="{n}"><option></option><option>Holds</option><option>Gap</option><option>Strong</option></select></td>'
        f'<td><input data-critwhy="{n}" placeholder="justification, citing a file"></td></tr>'
        for n, c in enumerate(criteria, start=1)
    )
    return f"""
<section id="form">
<h3>Part A — the anchor (AE-0002)</h3>
<div class="grid">
<label>Value A, your hash of the sdist's manifest <input id="a" placeholder="64 hex characters" spellcheck="false"></label>
<label>Value B, the tool's declared anchor <input id="b" placeholder="64 hex characters, or leave blank if not computed" spellcheck="false"></label>
<label>Value C, stated in this packet <input id="c" value="{v['anchor']}" readonly></label>
<label>Value D, GitHub at the commit (optional) <input id="d" placeholder="64 hex characters, or blank" spellcheck="false"></label>
<label>Operating system and tool used for A <input id="tool" placeholder="e.g. Ubuntu 24.04, sha256sum"></label>
<label>Your name (and affiliation or handle, if you wish) <input id="who"></label>
<label>Your role, as you describe it <input id="role" value="external reviewer"></label>
<label>Reviewed at (with offset) <input id="when" spellcheck="false"></label>
<label class="wide">Independence basis: your relationship to the maintainer (or none), that you hold no write access and wrote none of it, and that you computed on your own machine from PyPI and GitHub
<textarea id="basis" rows="3"></textarea></label>
<label class="wide">Limitations for the anchor record (one per line; leave empty if none)
<textarea id="lim_a" rows="2" placeholder="e.g. Value B not computed: the package's code was not run"></textarea></label>
<label>Outcome for the anchor record <select id="out_a"><option value="">choose</option><option>passed</option><option>passed_with_conditions</option><option>failed</option></select></label>
</div>
<p class="note">Agreement is computed from what you typed when you press Compose; the record states what you typed, not what the page thinks.</p>

<h3>Part B — the audit (AE-0003) <label class="inline"><input type="checkbox" id="did_b"> Part B performed</label></h3>
<div id="b_section" class="grid" hidden>
<label>The archive's SHA-256 as you computed it <input id="zip_hash" placeholder="64 hex characters" spellcheck="false"></label>
<label>The archive's inner manifest anchor as you computed it (must equal A) <input id="inner" placeholder="64 hex characters" spellcheck="false"></label>
<label>Verdict <select id="verdict"><option value="">choose</option><option>PASS</option><option>PASS WITH REQUIRED CHANGES</option><option>FAIL</option></select></label>
<label>Sections of the required output you completed <input id="sections" placeholder="e.g. 1-14, or 2, 8, 9, 13, 14"></label>
<div class="wide"><p><strong>The scope criteria</strong></p>
<table class="crit"><thead><tr><th>#</th><th>the kit is…</th><th>score</th><th>justification</th></tr></thead><tbody>
{criterion_rows}
</tbody></table></div>
<label class="wide">The report, in the prompt's required output shape (14 numbered sections; Markdown)
<textarea id="report" rows="18" placeholder="1. Verdict ...&#10;2. Manifest recomputation result ...&#10;..."></textarea></label>
<label class="wide">Limitations for the audit record: every EVIDENCE GAP, one per line
<textarea id="lim_b" rows="3"></textarea></label>
</div>

<p class="buttons"><button type="button" onclick="compose()">Compose the record(s)</button>
<button type="button" onclick="copyOut('yaml_a')">Copy AE-0002</button>
<button type="button" id="copy_b" onclick="copyOut('yaml_b')" hidden>Copy AE-0003</button>
<button type="button" id="copy_r" onclick="copyOut('report_md')" hidden>Copy the report</button>
<a id="dl_a" download="AE-0002-framework-anchor.yaml" hidden>Download AE-0002</a>
<a id="dl_b" download="AE-0003-independent-audit.yaml" hidden>Download AE-0003</a>
<a id="dl_r" download="INDEPENDENT_REVIEW.md" hidden>Download the report</a></p>
<p id="status" class="note"></p>
<label class="wide">AE-0002-framework-anchor.yaml <textarea id="yaml_a" rows="16" readonly></textarea></label>
<label class="wide" id="wrap_b" hidden>AE-0003-independent-audit.yaml <textarea id="yaml_b" rows="16" readonly></textarea></label>
<label class="wide" id="wrap_r" hidden>The report, as Markdown <textarea id="report_md" rows="10" readonly></textarea></label>
</section>
<script>
(function () {{
  var pad = function (n) {{ return (n < 10 ? "0" : "") + n; }};
  var now = new Date(); var off = -now.getTimezoneOffset(); var sign = off >= 0 ? "+" : "-"; off = Math.abs(off);
  document.getElementById("when").value = now.getFullYear() + "-" + pad(now.getMonth() + 1) + "-" + pad(now.getDate()) + "T" + pad(now.getHours()) + ":" + pad(now.getMinutes()) + ":" + pad(now.getSeconds()) + sign + pad(Math.floor(off / 60)) + ":" + pad(off % 60);
  document.getElementById("did_b").addEventListener("change", function () {{ document.getElementById("b_section").hidden = !this.checked; }});
}})();
function val(id) {{ return document.getElementById(id).value.trim(); }}
function fold(text) {{ return text.replace(/\\s+/g, " ").trim(); }}
function block(key, text, indent) {{
  var pad = indent || "";
  var words = fold(text).split(" "); var lines = []; var cur = "";
  words.forEach(function (w) {{ if (cur && (cur + " " + w).trim().length > 92) {{ lines.push(cur.trim()); cur = w; }} else {{ cur = (cur + " " + w); }} }});
  if (cur.trim()) lines.push(cur.trim());
  return pad + key + ": >-\\n" + lines.map(function (l) {{ return pad + "  " + l; }}).join("\\n") + "\\n";
}}
function items(text, extra) {{
  var out = text.split("\\n").map(fold).filter(Boolean).concat(extra || []);
  if (!out.length) return "";
  return "limitations:\\n" + out.map(function (l) {{ return block("-", l, "  ").replace("  -: >-", "  - >-"); }}).join("");
}}
function hex(s) {{ return /^[0-9a-f]{{64}}$/i.test(s); }}
function compose() {{
  var status = document.getElementById("status"); status.textContent = "";
  var a = val("a").toLowerCase(), b = val("b").toLowerCase(), c = val("c").toLowerCase(), d = val("d").toLowerCase();
  var problems = [];
  if (!hex(a)) problems.push("Value A must be 64 hex characters.");
  if (b && !hex(b)) problems.push("Value B must be 64 hex characters, or blank.");
  if (d && !hex(d)) problems.push("Value D must be 64 hex characters, or blank.");
  if (!val("who")) problems.push("Your name is required (reviewer_identity).");
  if (!val("basis")) problems.push("The independence basis is required.");
  if (!val("out_a")) problems.push("Choose an outcome for the anchor record.");
  if (problems.length) {{ status.textContent = problems.join(" "); return; }}
  var agree = [];
  agree.push(a === c ? "A equals C" : "A DIFFERS from C");
  if (b) agree.push(b === c ? "B equals C" : "B DIFFERS from C"); else agree.push("B not computed");
  if (d) agree.push(d === c ? "D equals C" : "D DIFFERS from C");
  var reference = "{v['sdist_url']} (sha256 {v['sdist_sha256']}); wheel sha256 {v['wheel_sha256']}; {v['commit_url']}; {v['publish_run_url']}; packet generated {v['generated_at']}.";
  var yamlA = "# governance/assurance/AE-0002-framework-anchor.yaml\\n"
    + "schema_version: \\"1.0\\"\\nevidence_id: AE-0002\\nevidence_type: independent_validation\\n"
    + "outcome: " + val("out_a") + "\\n"
    + "reviewer_role: " + (val("role") || "external reviewer") + "\\n"
    + "reviewer_identity: " + val("who") + "\\n"
    + "reviewed_at: \\"" + val("when") + "\\"\\n"
    + block("independence_basis", val("basis"))
    + block("scope", "Surfaceplate {v['version']}, published commit {v['commit']}. A (sdist manifest, own hash): " + a + ". B (the tool's declared anchor): " + (b || "not computed") + ". C (stated in the packet): " + c + ". D (GitHub at the commit): " + (d || "not computed") + ". Agreement: " + agree.join("; ") + ". Computed on " + (val("tool") || "an unstated system") + ".")
    + block("reference", reference)
    + items(val("lim_a"), document.getElementById("did_b").checked ? [] : ["The independent audit (release-plan item 10) was not performed; this record does not bear on H6."]);
  document.getElementById("yaml_a").value = yamlA;
  var dlA = document.getElementById("dl_a"); dlA.href = "data:text/yaml;charset=utf-8," + encodeURIComponent(yamlA); dlA.hidden = false;
  var didB = document.getElementById("did_b").checked;
  document.getElementById("wrap_b").hidden = !didB; document.getElementById("copy_b").hidden = !didB; document.getElementById("dl_b").hidden = !didB;
  document.getElementById("wrap_r").hidden = !didB; document.getElementById("copy_r").hidden = !didB; document.getElementById("dl_r").hidden = !didB;
  if (didB) {{
    var verdict = val("verdict");
    if (!verdict) {{ status.textContent = "Choose a verdict for the audit record."; return; }}
    var outcomeB = verdict === "PASS" ? "passed" : (verdict === "FAIL" ? "failed" : "passed_with_conditions");
    var crit = [];
    document.querySelectorAll("select[data-crit]").forEach(function (s) {{
      var n = s.getAttribute("data-crit"); var why = document.querySelector("input[data-critwhy='" + n + "']").value.trim();
      crit.push("| " + n + " | " + s.value + " | " + why + " |");
    }});
    var report = "# Independent review of Surfaceplate {v['version']} at commit {v['commit']}\\n\\n"
      + "Reviewer: " + val("who") + " (" + (val("role") || "external reviewer") + "), " + val("when") + ". Verdict: " + verdict + ".\\n\\n"
      + "## Scope criteria\\n\\n| # | score | justification |\\n|---|---|---|\\n" + crit.join("\\n") + "\\n\\n"
      + "## Report\\n\\n" + val("report") + "\\n";
    var limsB = val("lim_b");
    if (outcomeB !== "passed" && !fold(limsB)) {{ status.textContent = "An audit outcome other than passed needs at least one limitation (the schema requires it)."; return; }}
    var yamlB = "# governance/assurance/AE-0003-independent-audit.yaml\\n"
      + "schema_version: \\"1.0\\"\\nevidence_id: AE-0003\\nevidence_type: independent_validation\\n"
      + "outcome: " + outcomeB + "\\n"
      + "reviewer_role: independent reviewer\\n"
      + "reviewer_identity: " + val("who") + "\\n"
      + "reviewed_at: \\"" + val("when") + "\\"\\n"
      + block("independence_basis", val("basis") + " The archive's lineage was verified through its inner manifest anchor (" + (val("inner") || "not stated") + ").")
      + block("scope", "Independent audit of Surfaceplate {v['version']} at commit {v['commit']}: the archive {v['zip_name']} (sha256 " + (val("zip_hash") || "not stated") + ", inner manifest anchor " + (val("inner") || "not stated") + "), the repository, the self-check run read per step, and the suites run from the archive. Verdict: " + verdict + ". Sections done: " + (val("sections") || "not stated") + ".")
      + block("reference", "audit/INDEPENDENT_REVIEW_<date>.md (the report, verbatim); {v['ci_run_url']}; {v['commit_url']}; {v['sdist_url']}; packet generated {v['generated_at']}.")
      + items(limsB);
    document.getElementById("yaml_b").value = yamlB; document.getElementById("report_md").value = report;
    var dlB = document.getElementById("dl_b"); dlB.href = "data:text/yaml;charset=utf-8," + encodeURIComponent(yamlB);
    var dlR = document.getElementById("dl_r"); dlR.href = "data:text/markdown;charset=utf-8," + encodeURIComponent(report);
  }}
  status.textContent = "Composed. Copy or download, and send back with the audit text if Part B was done. Agreement as typed: " + agree.join("; ") + ".";
}}
function copyOut(id) {{
  var el = document.getElementById(id); el.select();
  try {{ navigator.clipboard.writeText(el.value); document.getElementById("status").textContent = "Copied."; }}
  catch (e) {{ document.execCommand("copy"); }}
}}
</script>
"""


# ---------------------------------------------------------------------------------------------
# the page
# ---------------------------------------------------------------------------------------------

CSS = """
body{margin:0;background:#f7f6f2;color:#1d1d1b;font:15px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
main{max-width:84ch;margin:0 auto;padding:2rem 1.25rem 4rem;background:#fff}
h1{font-size:1.6rem;margin:.2rem 0 1rem}h2{font-size:1.25rem;margin:2rem 0 .6rem;border-top:1px solid #ddd;padding-top:1rem}h3{font-size:1.05rem;margin:1.4rem 0 .4rem}
code,pre,input,textarea{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
code{background:#f0efe9;padding:0 .2em;word-break:break-all}pre{background:#f0efe9;padding:.8rem;overflow-x:auto;font-size:.85rem;line-height:1.45}pre code{background:none;padding:0;word-break:normal}
table{border-collapse:collapse;width:100%;margin:.6rem 0;font-size:.92rem}th,td{border:1px solid #d9d7cf;padding:.35rem .5rem;text-align:left;vertical-align:top}th{background:#f0efe9}
blockquote{margin:.6rem 0;padding:.2rem 1rem;border-left:4px solid #c9c6ba;color:#444}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:.7rem 1.2rem}.grid label{display:flex;flex-direction:column;gap:.25rem;font-size:.9rem}.grid .wide{grid-column:1/-1}
input,select,textarea{font-size:.9rem;padding:.35rem .45rem;border:1px solid #b9b6aa;border-radius:3px;background:#fff}input[readonly]{background:#f0efe9}
textarea{width:100%;box-sizing:border-box;resize:vertical}
.buttons button,.buttons a{display:inline-block;margin:.6rem .5rem .2rem 0;padding:.45rem .8rem;border:1px solid #444;border-radius:3px;background:#fff;color:#1d1d1b;font-size:.9rem;text-decoration:none;cursor:pointer}
.note{color:#555;font-size:.88rem}.inline{font-weight:normal;font-size:.9rem;margin-left:1rem}
.crit input{width:100%;box-sizing:border-box}
@media print{body{background:#fff}main{max-width:none;padding:0}.buttons,#copy_b,#copy_r{display:none}textarea{height:auto;min-height:6rem}a{color:inherit;text-decoration:none}}
"""


def build(args: argparse.Namespace) -> tuple[str, dict[str, str]]:
    ver = version()
    anchor, commit = anchor_at(args.ref)
    values: dict[str, str] = {
        "version": ver,
        "anchor": anchor,
        "commit": commit,
        "commit_url": f"{REPO_URL}/commit/{commit}",
        "sdist_url": args.sdist_url or "not supplied",
        "sdist_sha256": args.sdist_sha256 or "not supplied",
        "wheel_sha256": args.wheel_sha256 or "not supplied",
        "publish_run_url": f"{REPO_URL}/actions/runs/{args.publish_run}" if args.publish_run else "not supplied",
        "ci_run_url": f"{REPO_URL}/actions/runs/{args.ci_run}" if args.ci_run else "the self-check run for the commit was not supplied; find it under the repository's Actions tab for the commit above",
        "zip_name": "the release archive (none was attached to this packet)",
        "zip_sha256": "not supplied",
        "manifest_entries": str(manifest_entries_at(args.ref)),
        "generated_at": _dt.datetime.now().astimezone().replace(microsecond=0).isoformat(),
        "adopter_pin": (
            f"An adopting repository installed from this release records `{args.adopter_pin}` in `.standards/INSTALL.json`; "
            "it must equal C, and the maintainer states it here as a fact about that repository, which you cannot see."
            if args.adopter_pin else "No adopting repository's pin was supplied for comparison."
        ),
    }
    if args.zip:
        zip_path = Path(args.zip)
        values["zip_sha256"], _inner = inspect_zip(zip_path, anchor)
        values["zip_name"] = zip_path.name
    prompt_text = PROMPT.read_text(encoding="utf-8")
    if PROMPT_SLICE_FROM not in prompt_text:
        raise SystemExit(f"{PROMPT.name} has no {PROMPT_SLICE_FROM!r} heading to slice from")
    values["audit_prompt"] = prompt_text[prompt_text.index(PROMPT_SLICE_FROM):]
    criteria = scope_criteria()
    if not criteria:
        raise SystemExit(f"{SCOPE.name} lists no criteria")
    values["scope_rows"] = scope_rows_markdown(criteria)
    values["form"] = form_html(values, criteria)
    source = SOURCE.read_text(encoding="utf-8")
    filled = TOKEN.sub(lambda m: values[m.group(1)] if m.group(1) in values else m.group(0), source)
    unresolved = sorted(set(TOKEN.findall(filled)))
    if unresolved:
        raise SystemExit(f"unresolved placeholders in the packet: {', '.join(unresolved)}")
    body = render_markdown(filled)
    page = (
        "<!DOCTYPE html>\n<html lang=\"en-GB\"><head><meta charset=\"utf-8\">"
        f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>Independent review packet — Surfaceplate {ver}</title>"
        f"<style>{CSS}</style></head><body><main>\n{body}\n</main></body></html>\n"
    )
    return page, values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the independent review packet as one HTML page.")
    parser.add_argument("--ref", help="The published commit; the expected anchor is read from its manifest. Default: the working tree.")
    parser.add_argument("--zip", help="The release archive to describe; refused unless its inner manifest hashes to the expected anchor.")
    parser.add_argument("--sdist-url")
    parser.add_argument("--sdist-sha256")
    parser.add_argument("--wheel-sha256")
    parser.add_argument("--publish-run", help="The GitHub Actions run id that published the release.")
    parser.add_argument("--ci-run", help="The self-check run id for the published commit.")
    parser.add_argument("--adopter-pin", help="The framework digest an adopting repository records, stated as the maintainer's fact.")
    parser.add_argument("--out", help="Where to write the page (default dist/INDEPENDENT_REVIEW_PACKET-<version>.html).")
    args = parser.parse_args(argv)
    page, values = build(args)
    out = Path(args.out) if args.out else ROOT / "dist" / f"INDEPENDENT_REVIEW_PACKET-{values['version']}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8", newline="\n")
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"Packet:         {out}")
    print(f"Expected anchor {values['anchor']}  (commit {values['commit'][:12]})")
    print(f"Page SHA-256:   {digest}")
    print("Quote the page's digest in the message that carries it; the page cannot contain its own hash.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
