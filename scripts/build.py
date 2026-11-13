#!/usr/bin/env python3
r"""Validate a teach-me content file and build the study artifact (one self-contained HTML page).

    python build.py content.json --out "Solutions - Class 12 Chemistry.html"
    python build.py content/ --out solutions.html      # folder of *.json parts, merged by name order

What it checks (errors stop the build, warnings are printed):
  * structure: required fields, unique ids, valid question types, MCQ answer indices in range,
    topic / question cross-references that resolve
  * PYQ provenance: every past-year question names year, paper set, question number and marks
  * numerical answers: every `verify` expression is recomputed in Python and must match `expected`
  * math: unbalanced $ delimiters; with Node available, every TeX string is rendered by the same
    KaTeX + mhchem build the page uses, so a parse error is caught here instead of on the page
  * SVG: well-formed XML, no scripts or event handlers
  * coverage: counts against the minimums in references/content-spec.md (warnings; --strict fails)
  * lessons: unique permanent ids, worked examples with Given/Find/Relationship/calc/verify, try/details/
    interactive/recap blocks, prerequisite units and diagnostics
  * answer boxes: every `check.answer` agrees with a recomputation; mistake values lie outside tolerance
  * PYQ labels (form, ms.status), flashcard ids, formula status, coverage-map ids that really exist,
    verification checks and corrections records
  * patches: `{"patches": {id: fields}}` are applied after loading and may not change wording or keys

Authoring convenience: LaTeX may be written with single backslashes inside JSON strings
("$\\frac{a}{b}$" and "$\frac{a}{b}$" both work). The loader doubles any backslash that is not a
JSON escape we keep (\" \\ \/ \uXXXX), so "\nu", "\theta", "\beta", "\frac" survive intact.
The cost: "\n" never means newline - use separate blocks / list items instead.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "template.html"
KATEX_VERSION = "0.16.9"
KATEX_URLS = {
    "katex.min.js": f"https://cdnjs.cloudflare.com/ajax/libs/KaTeX/{KATEX_VERSION}/katex.min.js",
    "mhchem.min.js": f"https://cdnjs.cloudflare.com/ajax/libs/KaTeX/{KATEX_VERSION}/contrib/mhchem.min.js",
}

Q_TYPES = {"mcq", "ar", "tf", "fill", "short", "long", "numerical", "case", "oneword", "diagram", "map"}
BLOCK_TYPES = {"p", "h", "list", "formula", "table", "callout", "example", "svg", "check", "compare",
               "flow", "steps", "quote", "img",
               # v2 lesson blocks
               "objective", "worked", "try", "details", "interactive", "recap"}
CALLOUT_KINDS = {"tip", "mistake", "exam", "remember", "ncert", "beyond", "mnemonic", "warning", "why", "real",
                 "notation"}
PYQ_KINDS = {"main", "compartment", "second", "term1", "term2", "sqp", "other"}
TRY_ROLES = {"partial", "independent", "apply", "check"}
WIDGETS = {"dilution", "particles", "vapour", "osmosis"}
FORMULA_STATUS = {"exact", "dilute", "ideal", "definition", "empirical", "approx"}
PYQ_FORMS = {"original", "restated", "adapted"}
MS_STATUS = {"checked", "key", "computed", "unavailable"}
COVERAGE_STATUS = {"covered", "expand", "verify"}
CHECK_KINDS = {"temperature", "plain"}

# Minimums from references/content-spec.md. Chapters that genuinely have fewer items
# (e.g. a short English poem) can lower them in meta.targets.
DEFAULT_TARGETS = {"topics": 4, "flashcards": 30, "practice": 40, "pyqs": 15, "formulas_or_terms": 8,
                   "mcq_like": 15, "mock_ready": 1}

errors: list[str] = []
warnings: list[str] = []


def err(where: str, msg: str):
    errors.append(f"[error] {where}: {msg}")


def warn(where: str, msg: str):
    warnings.append(f"[warn]  {where}: {msg}")


# --------------------------------------------------------------------------- loading

def relax_backslashes(raw: str) -> str:
    """Inside JSON strings, double every backslash that is not one of \\ \" \\/ or a real \\uXXXX."""
    out = []
    i, n = 0, len(raw)
    in_str = False
    while i < n:
        c = raw[i]
        if not in_str:
            out.append(c)
            if c == '"':
                in_str = True
            i += 1
            continue
        if c == '"':
            in_str = False
            out.append(c)
            i += 1
            continue
        if c == "\\" and i + 1 < n:
            nxt = raw[i + 1]
            if nxt in '"\\/':
                out.append(raw[i:i + 2])
                i += 2
                continue
            if nxt == "u" and re.fullmatch(r"[0-9a-fA-F]{4}", raw[i + 2:i + 6] or ""):
                out.append(raw[i:i + 6])
                i += 6
                continue
            out.append("\\\\")
            i += 1
            continue
        if c == "\n":  # raw newline inside a string (invalid JSON) -> keep as a space
            out.append(" ")
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def load_one(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(relax_backslashes(raw))
    except json.JSONDecodeError as e:
        lines = relax_backslashes(raw).splitlines()
        ctx = lines[e.lineno - 1][max(0, e.colno - 60): e.colno + 40] if e.lineno - 1 < len(lines) else ""
        raise SystemExit(f"JSON error in {path} line {e.lineno} col {e.colno}: {e.msg}\n  near: {ctx}")


def merge(a, b):
    """Dicts merge recursively, lists concatenate, scalars from b win."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = merge(out[k], v) if k in out else v
        return out
    if isinstance(a, list) and isinstance(b, list):
        return a + b
    return b


def inline_files(obj, base: Path):
    """Any string "@file:relative/path.svg" is replaced by that file's text, so figures can be
    generated by a script (to scale) and kept out of the JSON."""
    if isinstance(obj, dict):
        return {k: inline_files(v, base) for k, v in obj.items()}
    if isinstance(obj, list):
        return [inline_files(v, base) for v in obj]
    if isinstance(obj, str) and obj.startswith("@file:"):
        f = base / obj[6:].strip()
        if not f.exists():
            err("content", f"referenced file not found: {f}")
            return ""
        return f.read_text(encoding="utf-8").strip()
    return obj


def all_questions(d: dict):
    """Every question object, including case parts and OR alternatives."""
    def walk(q):
        yield q
        for p in q.get("parts") or []:
            yield from walk(p)
        if isinstance(q.get("alt"), dict):
            yield from walk(q["alt"])
    pre = d.get("prereq") or {}
    lists = [d.get("questions"), d.get("pyqs"), pre.get("diagnostic"), pre.get("questions")]
    lists += list((d.get("ncert") or {}).values())
    for lst in lists:
        for q in lst or []:
            yield from walk(q)


def apply_patches(d: dict):
    """`patches: {"<question id>": {field: value}}` adds teaching fields (teach, check, hints,
    optionNotes, form, ms ...) to an existing question without rewriting its file, so the original
    wording stays untouched and the upgrade is reviewable on its own. Dict values merge, others replace.
    Case parts are addressed as "<case id>.<n>" unless they have their own id."""
    patches = d.pop("patches", None) or {}
    if not patches:
        return
    byid = {}
    for q in all_questions(d):
        for i, p in enumerate(q.get("parts") or []):
            p.setdefault("id", f"{q.get('id')}.{i + 1}")
        if isinstance(q.get("alt"), dict):
            q["alt"].setdefault("id", f"{q.get('id')}-or")
        byid[q.get("id")] = q
    for qid, fields in patches.items():
        q = byid.get(qid)
        if q is None:
            err(f"patches[{qid}]", "no question with this id")
            continue
        for k, v in fields.items():
            if k in ("id", "q", "options", "answer", "source"):
                if k in q and q[k] != v:
                    err(f"patches[{qid}].{k}", "patches may not change a question's id, wording, options, key or source - edit the question itself and log it in corrections")
                    continue
            q[k] = merge(q[k], v) if isinstance(q.get(k), dict) and isinstance(v, dict) else v


def load_content(path: Path) -> dict:
    """A single JSON file, or a folder of *.json parts merged in file-name order
    (e.g. 00-meta.json, 10-topics-a.json, 20-pyqs.json ...)."""
    if path.is_dir():
        parts = sorted(p for p in path.glob("*.json") if not p.name.startswith("_"))
        if not parts:
            raise SystemExit(f"no .json parts in {path}")
        d: dict = {}
        for p in parts:
            d = merge(d, load_one(p))
        d = inline_files(d, path)
    else:
        d = inline_files(load_one(path), path.parent)
    apply_patches(d)
    return d


# --------------------------------------------------------------------------- walking

def iter_strings(obj, where=""):
    if isinstance(obj, str):
        yield where, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("svg", "verify", "id", "topic", "questionIds", "img", "figure", "tex", "expr", "lesson", "unit", "widget"):
                continue
            yield from iter_strings(v, f"{where}.{k}" if where else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_strings(v, f"{where}[{i}]")


MATH_RE = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$|(?<!\\)\$(.+?)(?<!\\)\$", re.S)


def math_segments(s: str) -> list[tuple[str, bool]]:
    return [((m.group(1) or m.group(2)), bool(m.group(1))) for m in MATH_RE.finditer(s)]


def check_dollars(where: str, s: str):
    stripped = re.sub(r"\\\$", "", s)
    if stripped.count("$") % 2:
        err(where, f"odd number of $ delimiters (escape a literal dollar as \\$): {s[:90]!r}")


# --------------------------------------------------------------------------- checks

def check_svg(where: str, svg: str):
    if not svg.strip().startswith("<svg"):
        err(where, "svg must start with <svg")
        return
    if re.search(r"<script|\son\w+\s*=|javascript:", svg, re.I):
        err(where, "svg may not contain scripts or event handlers")
    try:
        ET.fromstring(svg)
    except ET.ParseError as e:
        err(where, f"svg is not well-formed XML ({e})")
    if "viewBox" not in svg:
        warn(where, "svg has no viewBox; it will not scale on phones")
    if re.search(r'fill="#[0-9a-fA-F]{3,6}"|stroke="#[0-9a-fA-F]{3,6}"', svg):
        warn(where, "svg uses literal hex colours; use currentColor or the tm-* classes so it works in dark mode")


SAFE_FUNCS = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
SAFE_FUNCS.update({"abs": abs, "round": round, "min": min, "max": max, "sum": sum, "pow": pow,
                   "ln": math.log, "log10": math.log10})


def run_verify(where: str, v) -> list:
    """Recompute each verify expression; return the recomputed numeric values."""
    vals: list = []
    checks = v if isinstance(v, list) else [v]
    for i, c in enumerate(checks):
        if isinstance(c, str):
            if not c.lower().startswith("n/a"):
                err(where, f"verify string must start with 'n/a:' and give a reason, got {c!r}")
            continue
        expr, expected = c.get("expr"), c.get("expected")
        tol = c.get("tol", 0.01)
        if expr is None or expected is None:
            err(where, "verify needs expr and expected")
            continue
        try:
            got = eval(expr, {"__builtins__": {}}, SAFE_FUNCS)  # content is authored by the skill itself
        except Exception as e:
            err(where, f"verify expr failed: {expr!r} ({e})")
            continue
        if isinstance(expected, str):
            if str(got) != expected:
                err(where, f"verify mismatch: {expr} = {got!r}, expected {expected!r}")
            continue
        ok = math.isclose(float(got), float(expected), rel_tol=tol, abs_tol=c.get("abs_tol", 0.0))
        if not ok:
            err(where, f"verify mismatch: {expr} = {got:.6g}, content says {expected} (rel tol {tol})")
        vals.append(float(got))
    return vals


def check_answer_check(where: str, c: dict, verified: list):
    """`check` drives the in-page answer checker. Its answer must agree with a recomputed value."""
    if not isinstance(c, dict) or c.get("answer") is None:
        err(where, "check needs answer (number)")
        return
    ans = c["answer"]
    if not isinstance(ans, (int, float)):
        err(where, "check.answer must be a number")
        return
    if c.get("kind", "plain") not in CHECK_KINDS:
        err(where, f"check.kind must be one of {sorted(CHECK_KINDS)}")
    if c.get("kind") == "temperature" and c.get("scale") not in ("K", "C"):
        err(where, "temperature check needs scale 'K' or 'C'")
    units = c.get("units")
    if units is not None and (not isinstance(units, list) or not all(isinstance(u, str) for u in units)):
        err(where, "check.units must be a list of accepted unit spellings")
    tol = c.get("tol", abs(ans) * 0.01)
    if tol <= 0:
        err(where, "check.tol must be > 0")
    if tol > abs(ans) * 0.05 + 1e-12 and not c.get("tolReason"):
        warn(where, f"check.tol {tol} is over 5% of the answer; add tolReason")
    ref = []
    if c.get("expr"):
        try:
            ref.append(float(eval(c["expr"], {"__builtins__": {}}, SAFE_FUNCS)))
        except Exception as e:
            err(where, f"check.expr failed: {e}")
    ref += verified
    if not ref:
        err(where, "check.answer has nothing to agree with: add verify to the question or check.expr")
    elif not any(abs(r - ans) <= tol + 1e-12 for r in ref):
        err(where, f"check.answer {ans} (tol {tol}) matches none of the recomputed values {[round(r, 6) for r in ref]}")
    for i, st in enumerate(c.get("steps") or []):
        if not st.get("label") or not isinstance(st.get("answer"), (int, float)):
            err(f"{where}.steps[{i}]", "check step needs label and numeric answer")
            continue
        if st.get("expr"):
            try:
                v = float(eval(st["expr"], {"__builtins__": {}}, SAFE_FUNCS))
                t = st.get("tol", abs(st["answer"]) * 0.01)
                if abs(v - st["answer"]) > t + 1e-12:
                    err(f"{where}.steps[{i}]", f"step answer {st['answer']} but expr gives {v:.6g}")
            except Exception as e:
                err(f"{where}.steps[{i}]", f"step expr failed: {e}")
        else:
            warn(f"{where}.steps[{i}]", "check step without expr (its value is not recomputed)")
    for i, m in enumerate(c.get("mistakes") or []):
        if not isinstance(m.get("answer"), (int, float)) or not m.get("msg"):
            err(f"{where}.mistakes[{i}]", "mistake needs numeric answer and msg")
        elif abs(m["answer"] - ans) <= tol:
            err(f"{where}.mistakes[{i}]", "a mistake value falls inside the correct answer's tolerance")


def check_teach(where: str, t: dict):
    """Teaching solution: Given -> Find -> Relationship (and why) -> Convert -> Calculate -> Check."""
    if not isinstance(t, dict):
        err(where, "teach must be an object")
        return
    if t.get("given") is not None and not isinstance(t["given"], list):
        err(where, "teach.given must be a list")
    for k in ("convert", "calc"):
        for i, x in enumerate(t.get(k) or []):
            if not isinstance(x, dict) or not x.get("t"):
                err(f"{where}.{k}[{i}]", "each step needs t (and optional why)")
    if t.get("calc") and not t.get("relation"):
        warn(where, "teach has calculations but no relation: say which relationship is used and why")


def check_question(q: dict, where: str, ids: set, topics: set, kind: str):
    qid = q.get("id")
    if not qid:
        err(where, "question without id")
    elif qid in ids:
        err(where, f"duplicate id {qid}")
    else:
        ids.add(qid)
    where = f"{where}({qid})"
    t = q.get("type")
    if t not in Q_TYPES:
        err(where, f"type {t!r} not one of {sorted(Q_TYPES)}")
        return
    if q.get("topic") and q["topic"] not in topics:
        err(where, f"topic {q['topic']!r} does not exist")
    if t == "mcq":
        opts = q.get("options") or []
        if len(opts) < 2:
            err(where, "mcq needs options")
        a = q.get("answer")
        if not isinstance(a, int) or not 0 <= a < len(opts):
            err(where, f"mcq answer must be an index into options, got {a!r}")
        if not q.get("explanation"):
            warn(where, "mcq without explanation")
    elif t == "ar":
        if not (q.get("assertion") and q.get("reason")):
            err(where, "ar needs assertion and reason")
        if q.get("answer") not in (0, 1, 2, 3):
            err(where, "ar answer must be 0-3 (A both true & R explains, B both true not explains, C A true R false, D A false R true)")
        if not q.get("explanation"):
            err(where, "ar needs an explanation of why")
    elif t == "case":
        if not q.get("passage"):
            err(where, "case needs a passage")
        parts = q.get("parts") or []
        if not parts:
            err(where, "case needs parts")
        for i, p in enumerate(parts):
            p.setdefault("id", f"{qid}.{i + 1}")
            p.setdefault("topic", q.get("topic"))
            check_question(p, f"{where}.parts[{i}]", ids, topics, "part")
    elif t in ("tf", "fill", "oneword"):
        if q.get("answer") in (None, ""):
            err(where, f"{t} needs answer")
    else:  # short / long / numerical / diagram / map
        sol = q.get("solution") or {}
        if not (sol.get("steps") or sol.get("final") or sol.get("points")):
            err(where, "needs solution.steps / solution.points / solution.final")
        for i, s in enumerate(sol.get("steps") or []):
            if not isinstance(s, dict) or "t" not in s:
                err(where, f"solution.steps[{i}] must be an object with t (text) and optional m (marks)")
        if q.get("marks") and sol.get("steps"):
            got = sum(float(s.get("m", 0)) for s in sol["steps"] if isinstance(s, dict))
            if got and abs(got - float(q["marks"])) > 1e-6:
                warn(where, f"step marks add to {got}, question carries {q['marks']}")
    if t == "numerical" and "verify" not in q:
        err(where, "numerical question needs verify (a Python expression recomputing the answer, or 'n/a: reason')")
    verified = run_verify(where, q["verify"]) if "verify" in q else []
    if q.get("check") is not None:
        check_answer_check(f"{where}.check", q["check"], verified)
    if q.get("teach") is not None:
        check_teach(f"{where}.teach", q["teach"])
    if q.get("hints") is not None and (not isinstance(q["hints"], list) or not all(isinstance(h, str) and h for h in q["hints"])):
        err(where, "hints must be a list of non-empty strings, from gentlest to most specific")
    if q.get("optionNotes") is not None:
        n_opts = 4 if t == "ar" else len(q.get("options") or [])
        if len(q["optionNotes"]) != n_opts:
            err(where, f"optionNotes needs one entry per option ({n_opts}); use '' for the correct one")
    if q.get("scaffold") is not None and not isinstance(q["scaffold"], list):
        err(where, "scaffold must be a list of steps")
    for i, r in enumerate((q.get("solution") or {}).get("rubric") or []):
        if not isinstance(r, dict) or not r.get("t"):
            err(f"{where}.solution.rubric[{i}]", "rubric item needs t (and m marks)")
    if q.get("figure"):
        check_svg(f"{where}.figure", q["figure"])
    if q.get("alt"):
        q["alt"].setdefault("id", f"{qid}-or")
        q["alt"].setdefault("topic", q.get("topic"))
        q["alt"].setdefault("marks", q.get("marks"))
        check_question(q["alt"], f"{where}.alt", ids, topics, "part")
    if kind == "pyq":
        src = q.get("source") or {}
        for f in ("year", "set", "q", "marks"):
            if src.get(f) in (None, ""):
                err(where, f"PYQ source.{f} missing - never list a PYQ you cannot trace to a paper")
        if src.get("kind", "main") not in PYQ_KINDS:
            err(where, f"source.kind must be one of {sorted(PYQ_KINDS)}")
        form = q.get("form")
        if form is None:
            warn(where, "PYQ without form (original / restated / adapted)")
        elif form not in PYQ_FORMS:
            err(where, f"form must be one of {sorted(PYQ_FORMS)}")
        if form == "adapted" and not q.get("adaptNote"):
            err(where, "adapted PYQ needs adaptNote saying what differs from the paper")
        ms = q.get("ms")
        if ms is None:
            warn(where, "PYQ without ms.status (checked / key / computed / unavailable)")
        elif not isinstance(ms, dict) or ms.get("status") not in MS_STATUS:
            err(where, f"ms.status must be one of {sorted(MS_STATUS)}")
    if kind == "ncert":
        src = q.get("source") or {}
        if not src.get("ref"):
            err(where, "NCERT question needs source.ref (e.g. 'Exercise 1.12' or 'Intext 1.3')")


def check_blocks(blocks, where, ids_wanted: list):
    for i, b in enumerate(blocks or []):
        if not isinstance(b, dict):
            err(f"{where}[{i}]", "block must be an object")
            continue
        w = f"{where}[{i}]"
        t = b.get("type")
        if t not in BLOCK_TYPES:
            err(w, f"block type {t!r} not one of {sorted(BLOCK_TYPES)}")
            continue
        if t == "svg":
            check_svg(w, b.get("svg", ""))
        if t == "callout" and b.get("kind") not in CALLOUT_KINDS:
            err(w, f"callout kind must be one of {sorted(CALLOUT_KINDS)}")
        if t in ("check", "try"):
            qids = b.get("questionIds") or ([b["questionId"]] if b.get("questionId") else [])
            if not qids:
                err(w, f"{t} block needs questionIds")
            ids_wanted.extend((w, x) for x in qids)
            if t == "try" and b.get("role") not in TRY_ROLES:
                err(w, f"try block role must be one of {sorted(TRY_ROLES)}")
        if t == "worked":
            if not (b.get("calc") or b.get("steps")) or not b.get("answer"):
                err(w, "worked block needs calc (or steps) and answer")
            if b.get("calc") and not (b.get("given") and b.get("find") and b.get("relation")):
                err(w, "worked calculation needs given, find and relation (Given -> Find -> Relationship -> ...)")
            check_teach(w, b)
            if "verify" in b:
                run_verify(w, b["verify"])
            elif b.get("calc"):
                err(w, "worked calculation needs verify")
            for j, st in enumerate(b.get("board") or []):
                if not isinstance(st, (dict, str)):
                    err(f"{w}.board[{j}]", "board step must be text or {t, m}")
            if b.get("figure"):
                check_svg(f"{w}.figure", b["figure"])
        if t == "details":
            if not b.get("title"):
                err(w, "details block needs a title (what the hidden part contains)")
            check_blocks(b.get("blocks"), f"{w}.blocks", ids_wanted)
        if t == "interactive" and b.get("widget") not in WIDGETS:
            err(w, f"interactive widget must be one of {sorted(WIDGETS)}")
        if t == "recap" and not b.get("items"):
            err(w, "recap needs items")
        if t == "objective" and not b.get("text"):
            err(w, "objective needs text")
        if t == "example":
            if not (b.get("steps") or b.get("answer")):
                err(w, "worked example needs steps or answer")
            if "verify" in b:
                run_verify(w, b["verify"])
        if t == "table":
            head = b.get("head") or []
            for r, row in enumerate(b.get("rows") or []):
                if head and len(row) != len(head):
                    err(w, f"table row {r} has {len(row)} cells, header has {len(head)}")
        if t == "formula":
            if not b.get("tex"):
                err(w, "formula block needs tex")
            if b.get("status") is not None and b["status"] not in FORMULA_STATUS:
                err(w, f"formula status must be one of {sorted(FORMULA_STATUS)}")
        if t == "img" and not str(b.get("src", "")).startswith("data:image/"):
            err(w, "img blocks must embed a data:image/... URI (external images are blocked in artifacts)")


def validate(d: dict):
    meta = d.get("meta") or {}
    for f in ("chapter", "subject", "class", "session", "board", "generated"):
        if not meta.get(f):
            err("meta", f"missing meta.{f}")
    topics = d.get("topics") or []
    tids = set()
    for i, t in enumerate(topics):
        if not t.get("id") or not t.get("title"):
            err(f"topics[{i}]", "topic needs id and title")
        if t.get("id") in tids:
            err(f"topics[{i}]", f"duplicate topic id {t.get('id')}")
        tids.add(t.get("id"))
    ids: set = set()
    wanted: list = []
    lesson_ids: set = set()

    def check_lesson(l, where):
        if not l.get("id") or not l.get("title"):
            err(where, "lesson needs id and title")
        if l.get("id") in lesson_ids or l.get("id") in tids:
            err(where, f"duplicate lesson id {l.get('id')}")
        lesson_ids.add(l.get("id"))
        if not l.get("blocks"):
            err(where, "lesson has no blocks")
        check_blocks(l.get("blocks"), f"{where}.blocks", wanted)

    for i, t in enumerate(topics):
        if t.get("lessons"):
            for j, l in enumerate(t["lessons"]):
                check_lesson(l, f"topics[{i}]({t.get('id')}).lessons[{j}]({l.get('id')})")
                if not l.get("objective"):
                    warn(f"topics[{i}].lessons[{j}]", "lesson without objective")
            if t.get("blocks"):
                err(f"topics[{i}]", "topic has both lessons and blocks; put all blocks into lessons")
        else:
            lesson_ids.add(f"{t.get('id')}-1")  # the page wraps a lesson-less topic as <id>-1
            check_blocks(t.get("blocks"), f"topics[{i}]({t.get('id')}).blocks", wanted)
            if not t.get("blocks"):
                err(f"topics[{i}]", "topic has no content blocks")
    pre = d.get("prereq")
    pre_units = set()
    if pre:
        for j, u in enumerate(pre.get("units") or []):
            check_lesson(u, f"prereq.units[{j}]({u.get('id')})")
            pre_units.add(u.get("id"))
        for i, q in enumerate(pre.get("diagnostic") or []):
            check_question(q, f"prereq.diagnostic[{i}]", ids, tids, "diagnostic")
            if q.get("unit") and q["unit"] not in pre_units:
                err(f"prereq.diagnostic[{i}]", f"unit {q['unit']!r} is not a prereq unit id")
        for i, q in enumerate(pre.get("questions") or []):
            check_question(q, f"prereq.questions[{i}]", ids, tids, "diagnostic")
    for i, q in enumerate(d.get("questions") or []):
        check_question(q, f"questions[{i}]", ids, tids, "practice")
    for i, q in enumerate(d.get("pyqs") or []):
        check_question(q, f"pyqs[{i}]", ids, tids, "pyq")
    ncert = d.get("ncert") or {}
    for part in ("intext", "exercises", "exemplar"):
        for i, q in enumerate(ncert.get(part) or []):
            check_question(q, f"ncert.{part}[{i}]", ids, tids, "ncert")
    for w, qid in wanted:
        if qid not in ids:
            err(w, f"check block refers to unknown question id {qid!r}")
    fc_ids: set = set()
    for i, f in enumerate(d.get("flashcards") or []):
        if f.get("id"):
            if f["id"] in fc_ids:
                err(f"flashcards[{i}]", f"duplicate flashcard id {f['id']}")
            fc_ids.add(f["id"])
        else:
            warn(f"flashcards[{i}]", "flashcard without a stable id (progress is keyed by id)")
        if not (f.get("front") and f.get("back")):
            err(f"flashcards[{i}]", "flashcard needs front and back")
        if f.get("topic") and f["topic"] not in tids:
            err(f"flashcards[{i}]", f"topic {f['topic']!r} does not exist")
    for i, f in enumerate(d.get("formulas") or []):
        if not (f.get("name") and (f.get("tex") or f.get("text"))):
            err(f"formulas[{i}]", "formula needs name and tex")
        if f.get("status") is not None and f["status"] not in FORMULA_STATUS:
            err(f"formulas[{i}]", f"formula status must be one of {sorted(FORMULA_STATUS)}")
        if f.get("lesson") and f["lesson"] not in lesson_ids:
            err(f"formulas[{i}]", f"lesson {f['lesson']!r} does not exist")
    for i, c in enumerate(d.get("coverage") or []):
        w = f"coverage[{i}]"
        if not (c.get("kind") and c.get("ref")):
            err(w, "coverage entry needs kind and ref")
        if c.get("status") not in COVERAGE_STATUS:
            err(w, f"coverage status must be one of {sorted(COVERAGE_STATUS)}")
        if c.get("status") == "covered" and not c.get("where"):
            err(w, "'covered' needs where (lesson or question ids that actually teach/solve it)")
        for x in c.get("where") or []:
            if x not in lesson_ids and x not in ids:
                err(w, f"where id {x!r} is neither a lesson nor a question")
    V = d.get("verification") or {}
    for i, c in enumerate(V.get("checks") or []):
        if not (c.get("what") and c.get("how") and c.get("status") in ("done", "partial", "open")):
            err(f"verification.checks[{i}]", "check needs what, how, status (done/partial/open) and result")
    for i, c in enumerate(d.get("corrections") or []):
        if not (c.get("item") and c.get("change")):
            err(f"corrections[{i}]", "correction needs item and change")
    syl = d.get("syllabus") or {}
    if not syl.get("inSyllabus"):
        err("syllabus", "syllabus.inSyllabus (official topic list for this chapter) is required")
    if "notForExam" not in syl:
        err("syllabus", "syllabus.notForExam is required (use [] and say so in syllabus.note if nothing is excluded)")
    if not d.get("sources"):
        err("sources", "list the sources used (official URLs)")
    for where, s in iter_strings(d):
        check_dollars(where, s)


def coverage(d: dict, strict: bool):
    tg = dict(DEFAULT_TARGETS)
    tg.update((d.get("meta") or {}).get("targets") or {})
    qs = d.get("questions") or []
    counts = {
        "topics": len(d.get("topics") or []),
        "flashcards": len(d.get("flashcards") or []),
        "practice": len(qs),
        "pyqs": len(d.get("pyqs") or []),
        "formulas_or_terms": len(d.get("formulas") or []) + len(d.get("terms") or []),
        "mcq_like": sum(1 for q in qs if q.get("type") in ("mcq", "ar")),
        "mock_ready": 1 if sum(1 for q in qs + (d.get("pyqs") or []) if q.get("type") in ("short", "long", "numerical", "case")) >= 5 else 0,
    }
    for k, need in tg.items():
        if counts.get(k, 0) < need:
            (err if strict else warn)("coverage", f"{k} = {counts.get(k, 0)}, target {need}")
    return counts


# --------------------------------------------------------------------------- KaTeX via node

def katex_check(d: dict, cache: Path | None):
    node = shutil.which("node")
    if not node:
        warn("math", "node not found - TeX was not test-rendered; check the page visually for red math boxes")
        return
    cache = cache or Path(tempfile.gettempdir()) / f"teachme_katex_{KATEX_VERSION}"
    kdir = cache / "node_modules" / "katex"
    kdir.mkdir(parents=True, exist_ok=True)
    try:
        if not (kdir / "katex.min.js").exists():
            (kdir / "katex.min.js").write_bytes(urllib.request.urlopen(KATEX_URLS["katex.min.js"], timeout=60).read())
            (kdir / "package.json").write_text('{"name":"katex","main":"katex.min.js"}')
        if not (cache / "mhchem.min.js").exists():
            (cache / "mhchem.min.js").write_bytes(urllib.request.urlopen(KATEX_URLS["mhchem.min.js"], timeout=60).read())
    except Exception as e:
        warn("math", f"could not download KaTeX for checking ({e}); TeX not test-rendered")
        return
    items = []
    for where, s in iter_strings(d):
        for tex, display in math_segments(s):
            items.append({"w": where, "tex": tex, "d": display})
    def walk(o, w):
        if isinstance(o, dict):
            if (o.get("type") == "formula" or w.startswith("formulas[")) and isinstance(o.get("tex"), str):
                items.append({"w": f"{w}.tex", "tex": o["tex"], "d": True})
            for k, v in o.items():
                walk(v, f"{w}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{w}[{i}]")
    for k in ("topics", "formulas", "prereq"):
        walk(d.get(k), k)
    (cache / "items.json").write_text(json.dumps(items), encoding="utf-8")
    (cache / "check.js").write_text(
        "const katex=require('katex');require('./mhchem.min.js');\n"
        "const items=require('./items.json');const bad=[];\n"
        "for(const it of items){try{katex.renderToString(it.tex,{displayMode:it.d,throwOnError:true,output:'mathml',strict:'ignore'})}"
        "catch(e){bad.push({w:it.w,tex:it.tex,msg:String(e.message).slice(0,160)})}}\n"
        "console.log(JSON.stringify({n:items.length,bad}));\n", encoding="utf-8")
    r = subprocess.run([node, "check.js"], cwd=cache, capture_output=True, text=True)
    if r.returncode:
        warn("math", f"KaTeX check could not run: {r.stderr[:300]}")
        return
    res = json.loads(r.stdout)
    for b in res["bad"]:
        err(b["w"], f"TeX does not render: {b['tex'][:80]!r} -> {b['msg']}")
    print(f"math: {res['n']} TeX snippets test-rendered, {len(res['bad'])} failed")


# --------------------------------------------------------------------------- build

def build(d: dict, out: Path):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    marker = "/*__TEACHME_DATA__*/null"
    if marker not in tpl:
        raise SystemExit("template marker missing")
    meta = d["meta"]
    title = meta.get("pageTitle") or f"{meta['chapter']} · Class {meta['class']} {meta['subject']}"
    page = tpl.replace(marker, payload).replace("__TEACHME_TITLE__", html_escape(title))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    # The Artifact host adds <!doctype>/<head>/<body> at publish time. For looking at the page
    # locally (browser pane, double-click) write a wrapped twin so it is not in quirks mode.
    preview = out.with_name(out.stem + ".preview.html")
    preview.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
                       '<style>:root{padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}'
                       'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
                       + page + "</body></html>", encoding="utf-8")
    size = out.stat().st_size
    if size > 15_000_000:
        err("build", f"page is {size / 1e6:.1f} MB; artifacts must stay under 16 MB")
    return size


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("content", type=Path)
    ap.add_argument("--out", type=Path, help="output .html (default: next to content.json)")
    ap.add_argument("--strict", action="store_true", help="treat coverage shortfalls as errors")
    ap.add_argument("--no-katex", action="store_true", help="skip the Node/KaTeX render check")
    ap.add_argument("--katex-cache", type=Path)
    a = ap.parse_args()

    d = load_content(a.content)
    validate(d)
    counts = coverage(d, a.strict)
    if not a.no_katex:
        katex_check(d, a.katex_cache)
    for w in warnings:
        print(w)
    if errors:
        for e in errors:
            print(e)
        print(f"\nBUILD FAILED: {len(errors)} error(s). Fix them in {a.content} and rebuild.")
        sys.exit(1)
    out = a.out or (a.content / "index.html" if a.content.is_dir() else a.content.with_suffix(".html"))
    size = build(d, out)
    print(json.dumps({"built": str(out), "kb": round(size / 1024), "counts": counts,
                      "ncert": {k: len(v) for k, v in (d.get("ncert") or {}).items()},
                      "warnings": len(warnings)}, indent=2))


if __name__ == "__main__":
    main()
