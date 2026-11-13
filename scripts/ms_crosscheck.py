#!/usr/bin/env python3
"""Cross-check past-paper answers against the marking-scheme text of the same set.

    python ms_crosscheck.py CONTENT_DIR --papers cache/papers/XII_chemistry --sqp cache/sqp --out ms_report.json

For every PYQ (and case part) it finds the marking-scheme .txt for the question's year, kind and set
(as downloaded by cbse_fetch.py) and looks for evidence:
  * MCQ / assertion-reason: the key letter printed against the question number ("3. (B)", "Q3 B" ...)
  * numerical: each number in solution.final (and verify `expected`) appearing in that scheme, allowing
    the scheme's own rounding (2-4 significant figures)
It never decides that a written explanation is correct - theory answers are reported as 'not
auto-checkable'. The report lists, per question: status, the file used and the matching line, so a
person can confirm. Statuses:
  key-match, key-mismatch, numbers-found, numbers-missing, no-scheme-file, not-auto-checkable
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

LETTERS = "ABCD"


def ms_files(papers: Path, sqp: Path | None, src: dict) -> list[Path]:
    year, kind, setc = src.get("year"), src.get("kind", "main"), str(src.get("set", ""))
    if kind == "sqp":
        if not sqp:
            return []
        m = re.search(r"(\d{4})-(\d{2})", setc)
        sess = f"{m.group(1)}-{m.group(2)}" if m else ""
        return sorted((sqp / sess).glob("*Chemistry*MS*.txt")) if sess else []
    dirs = [papers / f"{year}_MS"] if kind == "main" else [papers / f"{year}-COMPTT_MS"]
    if "(B)" in setc.upper():  # paper for visually impaired candidates
        blind = re.compile(r"blind|visually|v\.i\.|56[\s_\-]*\(?b\)?(?![a-z])", re.I)
        return sorted(f for d in dirs for f in d.rglob("*.txt") if blind.search(f.name) and "hindi" not in str(f).lower())
    parts = [p for p in re.split(r"[/\s]+", setc) if p]
    if len(parts) < 2:
        return []
    out = []
    for d in dirs:
        for f in d.rglob("*.txt"):
            name = f.stem.replace(" ", "_")
            if "hindi" in str(f).lower():
                continue
            a, b = re.escape(parts[0]), re.escape(parts[1])
            if len(parts) >= 3:
                c = parts[2]
                pat = rf"{a}[\W_]+{b}[\W_]+(?:[\d,]*\b)?{re.escape(c)}\b" + rf"|{a}[\W_]+{b}[\W_]+{re.escape(c)}"
                combined = re.search(rf"{a}[\W_]+{b}[\W_]+(\d(?:,\d)+)", name)
                if re.search(pat, name) or (combined and c in combined.group(1).split(",")):
                    out.append(f)
            elif re.search(rf"{a}[\W_]+\(?{b}\)?", name):
                out.append(f)
    return out


def number_variants(x: float) -> set[str]:
    out = set()
    if x == 0 or not math.isfinite(x):
        return out
    for sig in (2, 3, 4, 5):
        v = float(f"{x:.{sig}g}")
        s = f"{v:.10f}".rstrip("0").rstrip(".")
        out.add(s)
        mant, exp = f"{x:.{sig - 1}e}".split("e")
        out.add(mant.rstrip("0").rstrip(".") + "x10" + str(int(exp)))
    return out


def norm_text(t: str) -> str:
    t = t.replace("−", "-").replace("–", "-").replace("×", "x").replace(" ", " ")
    t = re.sub(r"(\d)\s*[·⋅]\s*(\d)", r"\1.\2", t)  # 0·208 -> 0.208
    t = re.sub(r"\s*x\s*10\s*\^?\s*([-–]?\s*\d+)", lambda m: "x10" + m.group(1).replace(" ", ""), t)
    return t


def find_key(text: str, qno: str) -> tuple[str | None, str]:
    roman = {"i": "A", "ii": "B", "iii": "C", "iv": "D"}  # some schemes (2020) key options as (i)-(iv)
    pats = [rf"(?m)^\s*(?:Q\.?\s*)?{qno}\s*[\.\):\-]?\s*\(?([A-Da-d]|iv|iii|ii|i)\)?(?:[\s\.\)]|$)",
            rf"(?m)\b{qno}\s*[\.\)]\s*\(([A-Da-d]|iv|iii|ii|i)\)"]
    for p in pats:
        m = re.search(p, text)
        if m:
            line = text[max(0, m.start() - 10): m.end() + 60].replace("\n", " ")
            k = m.group(1)
            return roman.get(k, k.upper()), line
    return None, ""


def numbers_in(q: dict) -> list[float]:
    vals = []
    v = q.get("verify")
    for c in (v if isinstance(v, list) else [v] if v else []):
        if isinstance(c, dict) and isinstance(c.get("expected"), (int, float)):
            vals.append(float(c["expected"]))
    fin = (q.get("solution") or {}).get("final") or ""
    fin = re.sub(r"\$[^$]*\$", " ", fin)
    for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)(?:\s*[x×]\s*10\^?\{?(-?\d+)\}?)?", fin):
        x = float(m.group(1)) * (10 ** int(m.group(2)) if m.group(2) else 1)
        if x not in (0, 1, 2, 3, 4, 5, 10, 100):
            vals.append(x)
    seen, out = set(), []
    for x in vals:
        k = round(x, 12)
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("content", type=Path)
    ap.add_argument("--papers", type=Path, required=True)
    ap.add_argument("--sqp", type=Path)
    ap.add_argument("--out", type=Path, default=Path("ms_report.json"))
    a = ap.parse_args()
    d = build.load_content(a.content)
    report = []
    cache: dict[Path, str] = {}

    def text_of(f: Path, setc: str = "") -> str:
        key = (f, setc)
        if key not in cache:
            t = f.read_text(encoding="utf-8", errors="ignore")
            # files that hold several sets (2020: "56/5/1,2,3") -> keep only this set's section
            head = r"(?m)^\s*(?:Set\s*[–-]\s*\d*\s*)?\(?{}\)?\s*$"
            if setc and re.search(head.format(re.escape(setc)), t):
                heads = [m.start() for m in re.finditer(head.format(r"\d+/\w+/\d+"), t)]
                start = re.search(head.format(re.escape(setc)), t).start()
                nxt = [h for h in heads if h > start]
                t = t[start: nxt[0] if nxt else len(t)]
            cache[key] = norm_text(t)
        return cache[key]

    for q in d.get("pyqs") or []:
        src = q.get("source") or {}
        files = ms_files(a.papers, a.sqp, src)
        items = [(q, src.get("q"))]
        for i, p in enumerate(q.get("parts") or []):
            items.append((p, None))
        for item, qno in items:
            rec = {"id": item.get("id") or q.get("id"), "type": item.get("type"), "set": f"{src.get('year')} {src.get('kind', 'main')} {src.get('set')}",
                   "q": src.get("q"), "files": [str(f) for f in files]}
            if not files:
                rec["status"] = "no-scheme-file"
            elif item.get("type") in ("mcq", "ar") and qno:
                want = LETTERS[item["answer"]] if isinstance(item.get("answer"), int) else None
                got, line = None, ""
                for f in files:
                    got, line = find_key(text_of(f, str(src.get('set', ''))), re.escape(str(qno)))
                    if got:
                        rec["file"] = str(f)
                        break
                rec.update({"want": want, "got": got, "evidence": line})
                rec["status"] = "key-match" if got and got == want else "key-mismatch" if got else "key-not-located"
            elif item.get("type") == "numerical" or numbers_in(item):
                nums = numbers_in(item)
                found, missing = [], []
                for x in nums:
                    vs = number_variants(x)
                    hit = None
                    for f in files:
                        t = text_of(f, str(src.get('set', '')))
                        for v in sorted(vs, key=len, reverse=True):
                            if re.search(rf"(?<![\d.]){re.escape(v)}(?!\d)", t):
                                i = re.search(rf"(?<![\d.]){re.escape(v)}(?!\d)", t).start()
                                hit = (str(f), v, t[max(0, i - 60): i + 40].replace("\n", " "))
                                break
                        if hit:
                            break
                    (found if hit else missing).append({"value": x, "hit": hit})
                rec.update({"found": found, "missing": [m["value"] for m in missing]})
                rec["status"] = "numbers-found" if found and not missing else "numbers-partly-found" if found else "numbers-missing" if nums else "not-auto-checkable"
            else:
                rec["status"] = "not-auto-checkable"
            report.append(rec)
    a.out.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    print(json.dumps(Counter(r["status"] for r in report), indent=1))
    print(f"report: {a.out}")


if __name__ == "__main__":
    main()
