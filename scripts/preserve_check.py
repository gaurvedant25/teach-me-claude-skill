#!/usr/bin/env python3
"""Compare an earlier version of a chapter's content with the current one, so an update never
silently deletes or rewrites material.

    python preserve_check.py OLD_CONTENT_DIR NEW_CONTENT_DIR [--report report.md]

Checks (anything listed must be reviewed and either restored or recorded in `corrections`):
  * every question id from the old version still exists (questions, PYQs, NCERT, case parts)
  * each kept question's wording, options, answer key and source are unchanged
  * each kept question's solution text is unchanged (changes are listed, not failed - they may be fixes)
  * flashcards: same count or more, same order for the old ones (progress is keyed by position in v1
    and by id afterwards), front/back unchanged
  * every text string from the old lessons/topics still appears somewhere in the new lessons
  * formulas, glossary terms, sources and figures are still present
Exit code 1 if anything was removed; 0 if only edits were found (they are listed for review).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402  (reuses the same loader, so @file and patches resolve identically)


def strings(obj, skip=("svg", "figure", "verify", "id", "topic", "questionIds", "questionId", "type", "kind", "status", "role", "widget")):
    out = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k not in skip:
                out += strings(v, skip)
    elif isinstance(obj, list):
        for v in obj:
            out += strings(v, skip)
    return out


def norm(s: str) -> str:
    return " ".join(s.split())


def questions(d):
    return {q.get("id"): q for q in build.all_questions(d) if q.get("id")}


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old", type=Path)
    ap.add_argument("new", type=Path)
    ap.add_argument("--report", type=Path)
    a = ap.parse_args()
    old, new = build.load_content(a.old), build.load_content(a.new)
    removed, changed, notes = [], [], []

    oq, nq = questions(old), questions(new)
    for qid, q in oq.items():
        if qid not in nq:
            removed.append(f"question {qid} is missing")
            continue
        n = nq[qid]
        for k in ("q", "options", "answer", "assertion", "reason", "passage", "source", "type", "marks"):
            if json.dumps(q.get(k), sort_keys=True) != json.dumps(n.get(k), sort_keys=True):
                changed.append(f"question {qid}: field '{k}' changed")
        if json.dumps(q.get("solution"), sort_keys=True) != json.dumps(n.get("solution"), sort_keys=True):
            changed.append(f"question {qid}: solution changed")
        if q.get("explanation") != n.get("explanation"):
            changed.append(f"question {qid}: explanation changed")
    notes.append(f"questions: {len(oq)} before, {len(nq)} now ({len(set(nq) - set(oq))} new)")

    of, nf = old.get("flashcards") or [], new.get("flashcards") or []
    if len(nf) < len(of):
        removed.append(f"flashcards: {len(of)} before, {len(nf)} now")
    for i, c in enumerate(of):
        if i >= len(nf):
            break
        if (c.get("front"), c.get("back")) != (nf[i].get("front"), nf[i].get("back")):
            changed.append(f"flashcard #{i + 1} ({nf[i].get('id', '')}) text or position changed")
    notes.append(f"flashcards: {len(of)} before, {len(nf)} now")

    new_lesson_text = {norm(s) for s in strings(new.get("topics"))}
    new_all_text = " \u0000 ".join(norm(s) for s in strings(new))
    missing_text = []
    for s in strings(old.get("topics")):
        ns = norm(s)
        if len(ns) < 4 or ns in new_lesson_text:
            continue
        missing_text.append(ns if ns in new_all_text else ns)
    for s in missing_text:
        changed.append(f"lesson text not found verbatim in the new lessons: {s[:140]!r}")
    notes.append(f"lesson strings: {len(strings(old.get('topics')))} before; {len(missing_text)} not found verbatim")

    for key, label in (("formulas", "name"), ("terms", "term"), ("sources", "title")):
        on = {norm(x.get(label, "")) for x in old.get(key) or []}
        nn = {norm(x.get(label, "")) for x in new.get(key) or []}
        for x in sorted(on - nn):
            removed.append(f"{key}: '{x}' missing")
    old_svgs = {norm(s) for s in strings(old, skip=()) if s.strip().startswith("<svg")}
    new_svgs = {norm(s) for s in strings(new, skip=()) if s.strip().startswith("<svg")}
    for i, s in enumerate(sorted(old_svgs - new_svgs)):
        removed.append(f"figure missing (first chars: {s[:80]!r})")

    lines = ["# Preservation check", "", f"Old: `{a.old}`  ", f"New: `{a.new}`", ""]
    lines += ["## Summary", ""] + [f"- {n}" for n in notes] + [f"- removed items: {len(removed)}", f"- changed items to review: {len(changed)}", ""]
    lines += ["## Removed (must be restored or justified)", ""] + ([f"- {r}" for r in removed] or ["- none"]) + [""]
    lines += ["## Changed (review: each should be a deliberate fix listed in corrections)", ""] + ([f"- {c}" for c in changed] or ["- none"])
    text = "\n".join(lines) + "\n"
    if a.report:
        a.report.write_text(text, encoding="utf-8")
    print(text)
    sys.exit(1 if removed else 0)


if __name__ == "__main__":
    main()
