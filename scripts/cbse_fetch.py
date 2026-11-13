#!/usr/bin/env python3
"""Fetch official CBSE / NCERT source material for a chapter and turn it into searchable text.

Every source this script touches is an official, public government page:
  * cbseacademic.nic.in  - curriculum (syllabus) and sample question papers (SQP + marking scheme)
  * www.cbse.gov.in      - previous years' board question papers and marking schemes
  * ncert.nic.in         - current NCERT textbook chapters, answer keys and exemplar

cbseacademic.nic.in has served an expired TLS certificate at times, so certificate
verification is relaxed for these three hosts only. Nothing is uploaded anywhere.

Subcommands (run with -h for options):
  session                         print the current CBSE academic session and key URLs
  syllabus  --cls XII --subject chemistry
  sqp       --cls XII --subject chemistry
  papers    --cls XII --subject chemistry [--years 2019-2026]
  ncert     --cls 12 --subject chemistry [--book 1] [--chapter 1]
  search    --dir <cache> --terms "Raoult" "osmotic" ...   (find chapter questions in extracted text)
  render    --pdf <file> --pages 3,4 [--zoom 2]              (PNG pages for figures / scanned papers)

All output lands under --out (default ./teachme_cache). Each PDF gets a sibling .txt
with "=== PAGE n ===" markers so you can cite page numbers.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import io
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
CBSE_ACAD = "https://cbseacademic.nic.in/"
CBSE_MAIN = "https://www.cbse.gov.in/cbsenew/"
NCERT = "https://ncert.nic.in/"
RELAXED_HOSTS = {"cbseacademic.nic.in", "www.cbse.gov.in", "cbse.gov.in", "ncert.nic.in"}

# Common aliases so "maths", "bio", "sst" etc. resolve to the names CBSE uses.
ALIASES = {
    "math": ["mathematics", "maths", "math"],
    "maths": ["mathematics", "maths", "math"],
    "mathematics": ["mathematics", "maths", "math"],
    "maths standard": ["mathematics standard", "maths standard", "math_s", "mathematics_std", "standard"],
    "maths basic": ["mathematics basic", "maths basic", "math_b", "mathematics_basic", "basic"],
    "applied maths": ["applied mathematics", "applied_math", "applied maths"],
    "bio": ["biology"],
    "biology": ["biology"],
    "chem": ["chemistry"],
    "chemistry": ["chemistry"],
    "phy": ["physics"],
    "physics": ["physics"],
    "science": ["science", "scince"],
    "sst": ["social science", "social_science", "socialscience"],
    "social science": ["social science", "social_science", "socialscience"],
    "eco": ["economics"],
    "economics": ["economics"],
    "accounts": ["accountancy"],
    "accountancy": ["accountancy"],
    "bst": ["business studies", "business_studies", "businessstudies", "buisness_studies"],
    "business studies": ["business studies", "business_studies", "businessstudies", "buisness_studies"],
    "english": ["english core", "english_core", "english language and literature", "english_ll", "englishl", "english"],
    "english core": ["english core", "english_core"],
    "history": ["history"],
    "geography": ["geography"],
    "political science": ["political science", "politicalscience", "political_science"],
    "pol sci": ["political science", "politicalscience", "political_science"],
    "psychology": ["psychology"],
    "sociology": ["sociology"],
    "computer science": ["computer science", "computer_science"],
    "cs": ["computer science", "computer_science"],
    "informatics practices": ["informatics practices", "informatics_practices"],
    "ip": ["informatics practices", "informatics_practices"],
    "physical education": ["physical education", "physicaleducation", "physical_education"],
}

# NCERT textbook.php uses these subject names in its book picker.
NCERT_SUBJECT_NAMES = {
    "chemistry": "Chemistry", "physics": "Physics", "biology": "Biology",
    "mathematics": "Mathematics", "maths": "Mathematics", "math": "Mathematics",
    "science": "Science", "social science": "Social Science", "sst": "Social Science",
    "english": "English", "economics": "Economics", "accountancy": "Accountancy",
    "business studies": "Business Studies", "history": "History", "geography": "Geography",
    "political science": "Political Science", "psychology": "Psychology", "sociology": "Sociology",
    "computer science": "Computer Science", "informatics practices": "Informatics Practices",
    "hindi": "Hindi", "sanskrit": "Sanskrit", "physical education": "Health and Physical Education",
}

ROMAN = {"9": "IX", "10": "X", "11": "XI", "12": "XII", "IX": "IX", "X": "X", "XI": "XI", "XII": "XII"}
ARABIC = {"IX": 9, "X": 10, "XI": 11, "XII": 12}


# --------------------------------------------------------------------------- utils

def log(*a):
    print(*a, file=sys.stderr, flush=True)


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def subject_keys(subject: str) -> list[str]:
    s = norm(subject)
    keys = ALIASES.get(s, [s])
    return [norm(k) for k in keys]


def cls_roman(c: str) -> str:
    c = str(c).strip().upper()
    if c not in ROMAN:
        raise SystemExit(f"Unknown class {c!r}; use 9-12 or IX-XII")
    return ROMAN[c]


def current_session(today: dt.date | None = None) -> str:
    """CBSE sessions run April -> March. Oct 2026 -> '2026-27'; Feb 2027 -> '2026-27'."""
    today = today or dt.date.today()
    start = today.year if today.month >= 4 else today.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


def session_end_year(session: str) -> int:
    m = re.match(r"(\d{4})-(\d{2})$", session)
    if not m:
        raise SystemExit(f"Session must look like 2026-27, got {session!r}")
    return int(m.group(1)) + 1


def _ctx_for(url: str):
    host = urllib.parse.urlparse(url).hostname or ""
    if host in RELAXED_HOSTS:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return ssl.create_default_context()


def fetch(url: str, retries: int = 3, timeout: int = 90) -> bytes:
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, context=_ctx_for(url), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            last = e
        except Exception as e:  # network hiccup; NCERT sometimes drops the first request
            last = e
        time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"fetch failed for {url}: {last}")


def save(url: str, dest: Path, force: bool = False) -> Path | None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return dest
    try:
        data = fetch(url)
    except urllib.error.HTTPError as e:
        log(f"  HTTP {e.code}: {url}")
        return None
    except Exception as e:
        log(f"  FAILED: {url} ({e})")
        return None
    if data[:5] != b"%PDF-" and dest.suffix.lower() == ".pdf":
        log(f"  not a PDF (got {data[:40]!r}): {url}")
        return None
    dest.write_bytes(data)
    return dest


def anchors(page_html: str) -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', page_html, flags=re.S | re.I):
        text = html.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))
        out.append((m.group(1), re.sub(r"\s+", " ", text).strip()))
    return out


# ------------------------------------------------------------------ PDF -> text

def pdf_to_text(pdf: Path) -> tuple[int, int]:
    """Write <pdf>.txt with page markers. Returns (pages, characters)."""
    txt = pdf.with_suffix(".txt")
    pages: list[str] = []
    try:
        try:
            import pymupdf as fitz  # type: ignore
        except ImportError:
            import fitz  # type: ignore
        with fitz.open(pdf) as doc:
            pages = [p.get_text() for p in doc]
    except Exception:
        try:
            from pypdf import PdfReader  # type: ignore
            pages = [(p.extract_text() or "") for p in PdfReader(str(pdf)).pages]
        except Exception:
            exe = shutil.which("pdftotext")
            if exe:
                r = subprocess.run([exe, "-layout", str(pdf), "-"], capture_output=True, text=True)
                pages = r.stdout.split("\f")
    # CBSE PDFs often join words with zero-width joiners; turn them into spaces so search works.
    pages = [re.sub(r"[​‌‍ ]", " ", t) for t in pages]
    body = "\n".join(f"=== PAGE {i + 1} ===\n{t}" for i, t in enumerate(pages))
    txt.write_text(body, encoding="utf-8")
    return len(pages), sum(len(p.strip()) for p in pages)


def convert_all(root: Path, skip_hindi: bool = True) -> list[dict]:
    rows = []
    for pdf in sorted(root.rglob("*.pdf")):
        if skip_hindi and re.search(r"hindi|_h[_.\-]|_h$|\(h\)", pdf.stem + "/" + str(pdf.parent), re.I):
            continue
        n, chars = pdf_to_text(pdf)
        rows.append({"pdf": str(pdf), "txt": str(pdf.with_suffix(".txt")), "pages": n,
                     "chars": chars, "scanned": chars < 200 * max(n, 1) * 0.1})
    return rows


# ------------------------------------------------------------------- session

def cmd_session(a):
    s = current_session()
    end = session_end_year(s)
    print(json.dumps({
        "today": dt.date.today().isoformat(),
        "session": s,
        "board_exam_year": end,
        "curriculum_page": f"{CBSE_ACAD}curriculum_{end}.html",
        "sqp_pages": [f"{CBSE_ACAD}SQP_CLASSXII_{s[:4]}-{end % 100:02d}.html",
                      f"{CBSE_ACAD}SQP_CLASSX_{s[:4]}-{end % 100:02d}.html"],
        "pyq_pages": [f"{CBSE_MAIN}question-paper.html", f"{CBSE_MAIN}marking-scheme.html"],
        "ncert_textbooks": f"{NCERT}textbook.php",
        "note": "If the curriculum page for this session 404s, CBSE has not published it yet: "
                "fall back to the previous session and say so in the artifact.",
    }, indent=2))


# ------------------------------------------------------------------ syllabus

def curriculum_sections(page: str) -> list[tuple[str, list[tuple[str, str]]]]:
    """Group links under the top-level 'Secondary Curriculum: Part ...' cards; nested cards
    (Languages, Main Subjects, ...) also use h4 headers, so they fold into the current top card."""
    parts = re.split(r'<h4 class="card-header">', page)
    out: list[tuple[str, list[tuple[str, str]]]] = []
    for p in parts[1:]:
        head = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", p.split("</h4>")[0]))).strip()
        if re.search(r"curriculum\s*:?\s*part", head, re.I) or not out:
            out.append((head, []))
        out[-1][1].extend(anchors(p))
    return out


def pick_section(sections, cls: str):
    want = {"IX": r"\(Class IX\)", "X": r"\(Class X\)", "XI": r"XI-XII", "XII": r"XI-XII"}[cls]
    for head, links in sections:
        if re.search(want, head):
            return head, links
    return None, []


def cmd_syllabus(a):
    cls = cls_roman(a.cls)
    session = a.session or current_session()
    end = session_end_year(session)
    out = Path(a.out) / "syllabus" / session
    out.mkdir(parents=True, exist_ok=True)
    page_url = f"{CBSE_ACAD}curriculum_{end}.html"
    try:
        page = fetch(page_url).decode("utf-8", "ignore")
    except Exception as e:
        raise SystemExit(f"Could not open {page_url}: {e}\nTry --session for the previous year.")
    (out / f"curriculum_{end}.html").write_text(page, encoding="utf-8")
    head, links = pick_section(curriculum_sections(page), cls)
    keys = subject_keys(a.subject)
    hits, intro = [], None
    for href, text in links:
        if not href.lower().endswith(".pdf"):
            continue
        t = norm(text)
        if intro is None and t.startswith("introduction") and "curriculum" in t:
            intro = (href, text)
        # "science" should catch "Science at Advanced Level" but not "Social Science".
        if any(t == k or t.startswith(k + " ") for k in keys):
            hits.append((href, text))
    if not hits:  # fall back to the file name when the link text is unusual
        for href, text in links:
            if href.lower().endswith(".pdf") and any(k.replace(" ", "") in norm(Path(href).stem).replace(" ", "") for k in keys):
                hits.append((href, text))
    # "Reading Material" links follow their subject link; keep the one immediately after a hit.
    for i, (href, text) in enumerate(links):
        if text.lower().startswith("reading material") and i and links[i - 1] in hits:
            hits.append((href, f"{links[i - 1][1]} - Reading Material"))
    if intro:
        hits.append(intro)
    if not hits:
        log(f"No syllabus PDF matched {a.subject!r} in section {head!r}. Links available:")
        for href, text in links:
            log(f"   {text}  ->  {href}")
        raise SystemExit(2)
    result = []
    seen = set()
    for href, text in hits:
        url = urllib.parse.urljoin(CBSE_ACAD, href)
        if url in seen:
            continue
        seen.add(url)
        dest = out / Path(urllib.parse.urlparse(url).path).name
        p = save(url, dest, a.force)
        if p:
            n, chars = pdf_to_text(p)
            result.append({"label": text, "url": url, "pdf": str(p), "txt": str(p.with_suffix(".txt")),
                           "pages": n, "chars": chars})
            log(f"  ok  {text}: {url}")
    print(json.dumps({"session": session, "class": cls, "section": head, "files": result}, indent=2))


# ----------------------------------------------------------------------- SQP

def cmd_sqp(a):
    cls = cls_roman(a.cls)
    if cls not in ("X", "XII"):
        raise SystemExit("CBSE publishes sample papers only for Class X and XII.")
    session = a.session or current_session()
    end = session_end_year(session)
    tag = f"{session[:4]}-{end % 100:02d}"
    page_url = f"{CBSE_ACAD}SQP_CLASS{cls}_{tag}.html"
    out = Path(a.out) / "sqp" / session
    out.mkdir(parents=True, exist_ok=True)
    try:
        page = fetch(page_url).decode("utf-8", "ignore")
    except Exception as e:
        raise SystemExit(f"Could not open {page_url} ({e}). The SQP for {session} may not be out yet; "
                         f"retry with --session for the previous year and say so in the artifact.")
    keys = [k.replace(" ", "") for k in subject_keys(a.subject)]
    files = []
    for href, text in anchors(page):
        if not href.lower().endswith(".pdf") or "_hi" in href.lower():
            continue
        fname = norm(Path(href).stem).replace(" ", "")
        base = re.sub(r"(sqp|ms|pq)$", "", fname)
        if any(base == k or base.startswith(k) for k in keys):
            url = urllib.parse.urljoin(CBSE_ACAD, href)
            p = save(url, out / Path(href).name, a.force)
            if p:
                n, chars = pdf_to_text(p)
                files.append({"url": url, "pdf": str(p), "txt": str(p.with_suffix(".txt")), "pages": n})
    if not files:
        log("No SQP matched. PDF names on the page:")
        for href, _ in anchors(page):
            if href.lower().endswith(".pdf") and "_hi" not in href.lower():
                log("   " + Path(href).name)
        raise SystemExit(2)
    print(json.dumps({"session": session, "class": cls, "page": page_url, "files": files}, indent=2))


# --------------------------------------------------------------------- papers

def _year_of(href: str) -> str:
    m = re.search(r"/(20\d\d(?:-COMPTT)?)/", href, re.I)
    return m.group(1).upper() if m else "?"


def cmd_papers(a):
    cls = cls_roman(a.cls)
    out = Path(a.out) / "papers" / f"{cls}_{norm(a.subject).replace(' ', '_')}"
    out.mkdir(parents=True, exist_ok=True)
    y0, y1 = (int(x) for x in a.years.split("-")) if "-" in a.years else (int(a.years), int(a.years))
    keys = [k.replace(" ", "") for k in subject_keys(a.subject)]
    cls_dirs = {cls}
    if cls == "X":
        cls_dirs.add("SECOND_BOARD_X")
    picked: dict[str, str] = {}
    for kind, page in (("QP", "question-paper.html"), ("MS", "marking-scheme.html")):
        try:
            html_page = fetch(CBSE_MAIN + page).decode("utf-8", "ignore")
        except Exception as e:
            log(f"Could not open {CBSE_MAIN + page}: {e}")
            continue
        for href, _ in anchors(html_page):
            parts = href.replace("\\", "/").split("/")
            if len(parts) < 4 or not re.search(r"\.(zip|pdf|rar)$", href, re.I):
                continue
            year = _year_of(href)
            ynum = int(year[:4]) if year[:4].isdigit() else 0
            if not (y0 <= ynum <= y1):
                continue
            cdir = parts[-2].upper()
            if cdir not in cls_dirs:
                continue
            fname = norm(urllib.parse.unquote(Path(parts[-1]).stem)).replace(" ", "")
            fname = re.sub(r"^\d+", "", fname)  # "086science" -> "science"
            if any(fname == k or fname.startswith(k) or k.startswith(fname) and len(fname) >= 4 for k in keys):
                label = f"{year}_{kind}" + ("_SECOND" if cdir == "SECOND_BOARD_X" else "")
                picked.setdefault(label, urllib.parse.urljoin(CBSE_MAIN, href.replace(" ", "%20")))
    # Older years are not linked from the index but are still served at predictable URLs.
    if y0 < 2022:
        names = sorted({a.subject.strip().title().replace(" ", "_"), a.subject.strip().upper().replace(" ", "_")})
        for y in range(y0, min(y1, 2021) + 1):
            for kind, folder in (("QP", "question-paper"), ("MS", "Marking-Scheme")):
                label = f"{y}_{kind}"
                if label in picked:
                    continue
                for n in names:
                    url = f"{CBSE_MAIN}{folder}/{y}/{cls}/{n}.zip"
                    try:
                        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
                        with urllib.request.urlopen(req, context=_ctx_for(url), timeout=30) as r:
                            if r.status == 200:
                                picked[label] = url
                                break
                    except Exception:
                        pass
    if not picked:
        raise SystemExit("No papers matched. Check the subject spelling (e.g. 'maths standard', 'science').")
    index = []
    for label, url in sorted(picked.items()):
        d = out / label
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
        arc = out / f"{label}{ext}"
        if not save(url, arc, a.force):
            continue
        if ext == ".zip":
            try:
                with zipfile.ZipFile(arc) as z:
                    for info in z.infolist():
                        name = info.filename.replace("\\", "/")
                        if name.endswith("/") or ".." in name:
                            continue
                        target = d / name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(z.read(info))
            except zipfile.BadZipFile:
                log(f"  bad zip: {url}")
                continue
        elif ext == ".pdf":
            d.mkdir(exist_ok=True)
            shutil.copy(arc, d / arc.name)
        else:
            log(f"  {ext} archive skipped (extract manually if needed): {url}")
            continue
        rows = convert_all(d, skip_hindi=not a.keep_hindi)
        for r in rows:
            r["label"] = label
            r["source_url"] = url
            r["set"] = guess_set(Path(r["pdf"]).name)
        index.extend(rows)
        log(f"  ok  {label}: {len(rows)} PDFs  <- {url}")
    (out / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    scanned = [r for r in index if r["scanned"]]
    print(json.dumps({"class": cls, "subject": a.subject, "dir": str(out), "pdfs": len(index),
                      "scanned_without_text": [r["pdf"] for r in scanned],
                      "by_label": {lab: sum(1 for r in index if r["label"] == lab) for lab in sorted({r['label'] for r in index})}},
                     indent=2))


def guess_set(name: str) -> str:
    m = re.search(r"(\d{2,3})[\s_\-/]*(\d)[\s_\-/]*(\d)", name)
    if m:
        return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
    m = re.search(r"(\d{2,3})\s*\(?(B|C)\)?", name, re.I)
    if m:
        return f"{m.group(1)}({m.group(2).upper()})"
    return Path(name).stem


# ---------------------------------------------------------------------- NCERT

def ncert_books(cls: int, subject: str) -> list[tuple[str, str, int]]:
    """Return [(book title, code, last chapter index)] from NCERT's textbook picker script."""
    page = fetch(NCERT + "textbook.php").decode("utf-8", "ignore")
    sub = NCERT_SUBJECT_NAMES.get(norm(subject), subject.title())
    pat = (r'document\.test\.tclass\.value==' + str(cls) +
           r'\)\s*&&\s*\(document\.test\.tsubject\.options\[sind\]\.text=="' + re.escape(sub) + r'"\)\)\s*\{(.*?)\}')
    m = re.search(pat, page, re.S)
    if not m:
        return []
    block = m.group(1)
    # Commented-out options (//document.test...) are stale entries NCERT left in the script.
    live = "\n".join(l for l in block.splitlines() if not l.strip().startswith("//"))
    texts = dict(re.findall(r'options\[(\d+)\]\.text="([^"]*)"', live))
    out = []
    for k, code, last in re.findall(r'options\[(\d+)\]\.value="textbook\.php\?([a-z0-9]+)=0-(\d+)"', live):
        out.append((texts.get(k, code), code, int(last)))
    return out


def cmd_ncert(a):
    cls = ARABIC[cls_roman(a.cls)]
    out = Path(a.out) / "ncert"
    out.mkdir(parents=True, exist_ok=True)
    books = ncert_books(cls, a.subject)
    english = [b for b in books if b[1][1] == "e"]
    if not books:
        raise SystemExit(f"NCERT picker has no '{a.subject}' for class {cls}. Check the subject name on "
                         f"{NCERT}textbook.php")
    if a.list or not a.chapter:
        res = []
        for title, code, last in english:
            ps = save(f"{NCERT}textbook/pdf/{code}ps.pdf", out / f"{code}ps.pdf", a.force)
            contents = ""
            if ps:
                pdf_to_text(ps)
                contents = ps.with_suffix(".txt").read_text(encoding="utf-8")
                m = re.search(r"^\s*(CONTENTS|Contents)\s*$", contents, re.M)
                contents = contents[m.start():m.start() + 3000] if m else contents[-3000:]
            res.append({"title": title, "code": code, "chapters": last, "prelims_pdf": str(ps) if ps else None,
                        "contents_excerpt": contents})
        print(json.dumps({"class": cls, "subject": a.subject, "english_books": res,
                          "all_books": [{"title": t, "code": c} for t, c, _ in books]}, indent=2))
        return
    if a.book:
        cand = [b for b in english if b[1].endswith(str(a.book))] or [english[int(a.book) - 1]]
    else:
        cand = english[:1]
    title, code, last = cand[0]
    ch = int(a.chapter)
    files = {}
    for key, name in (("chapter", f"{code}{ch:02d}.pdf"), ("answers", f"{code}an.pdf"), ("prelims", f"{code}ps.pdf")):
        p = save(f"{NCERT}textbook/pdf/{name}", out / name, a.force)
        if p:
            n, chars = pdf_to_text(p)
            files[key] = {"url": f"{NCERT}textbook/pdf/{name}", "pdf": str(p), "txt": str(p.with_suffix(".txt")),
                          "pages": n, "chars": chars}
    reprint = ""
    if "chapter" in files:
        m = re.search(r"Reprint\s+(\d{4}-\d{2})", Path(files["chapter"]["txt"]).read_text(encoding="utf-8"))
        reprint = m.group(1) if m else "not stated"
    print(json.dumps({"class": cls, "book": title, "code": code, "chapter": ch, "reprint": reprint,
                      "files": files,
                      "exemplar_hint": f"{NCERT}exemplar-problems (find the {a.subject} class {cls} exemplar and its chapter PDF)"},
                     indent=2))


# --------------------------------------------------------------------- search

QSTART = re.compile(r"^\s*(?:Q\.?\s*(?:No\.?)?\s*)?(\d{1,2})\s*[.)]\s*(\S.*)?$", re.I)
EN_WORDS = re.compile(r"\b(the|of|which|following|is|are|and|to|in|for|write|give|reason|calculate|"
                      r"what|why|how|explain|when|with|answer|correct|statement)\b", re.I)


def english_pages(text: str) -> list[tuple[str, str]]:
    """Board papers are bilingual: a Hindi page (often in a legacy font that extracts as junk)
    followed by the same page in English. Keep the English pages only."""
    pages = re.split(r"^=== PAGE (\d+) ===$", text, flags=re.M)
    out = []
    for i in range(1, len(pages) - 1, 2):
        num, body = pages[i], pages[i + 1]
        words = len(EN_WORDS.findall(body))
        junk = len(re.findall(r"[$^{}_>]\S", body))
        if words >= 4 and words * 3 >= junk:
            out.append((num, body))
    return out


def split_questions(text: str) -> list[tuple[str, str, str]]:
    """Split a paper / marking scheme into (page, question number, chunk) using the
    numbered-question lines on English pages. Numbers must run in sequence, which skips
    list items and marks. It locates questions; always read the chunk (and render the page
    when it has figures) before using a question."""
    chunks: list[tuple[str, str, str]] = []
    expect = 1
    cur_q, cur, cur_page = None, [], "1"
    for page, body in english_pages(text):
        for line in body.splitlines():
            m = QSTART.match(line)
            if m:
                n = int(m.group(1))
                if n == expect or (cur_q is not None and n == int(cur_q) + 1):
                    if cur_q is not None:
                        chunks.append((cur_page, cur_q, "\n".join(cur)))
                    cur_q, cur, cur_page = str(n), [], page
                    expect = n + 1
            if cur_q is not None:
                cur.append(line)
    if cur_q is not None:
        chunks.append((cur_page, cur_q, "\n".join(cur)))
    return chunks


def cmd_search(a):
    root = Path(a.dir)
    terms = [t.lower() for t in a.terms]
    hits = []
    for txt in sorted(root.rglob("*.txt")):
        if a.only and a.only.lower() not in str(txt).lower():
            continue
        text = txt.read_text(encoding="utf-8", errors="ignore")
        if len(text.strip()) < 100:
            continue
        chunks = split_questions(text)
        if len(chunks) < 5:  # table-style marking schemes: fall back to whole pages
            pages = english_pages(text) or re.findall(r"=== PAGE (\d+) ===\n(.*?)(?=\n=== PAGE|\Z)", text, re.S)
            chunks = [(p, "?", body) for p, body in pages]
        for page, qno, chunk in chunks:
            low = chunk.lower()
            score = sum(low.count(t) for t in terms)
            if score >= a.min_hits:
                hits.append({"file": str(txt), "page": page, "q": qno, "score": score,
                             "excerpt": re.sub(r"\s+", " ", chunk)[:a.chars]})
    if a.require:
        req = [t.lower() for t in a.require]
        hits = [h for h in hits if any(t in h["excerpt"].lower() for t in req)]
    hits.sort(key=lambda h: (-h["score"], h["file"]))
    out = Path(a.save) if a.save else None
    if out:
        out.write_text(json.dumps(hits, indent=2), encoding="utf-8")
    if a.group:
        write_groups(hits, root, Path(a.group))
        return
    print(json.dumps({"matches": len(hits), "saved_to": str(out) if out else None,
                      "top": hits[: a.limit]}, indent=2))


def _paper_label(path: Path, root: Path) -> str:
    rel = path.relative_to(root).parts
    return rel[0] if len(rel) > 1 else path.parent.name


def _qkey(text: str) -> str:
    t = re.sub(r"^\s*\d{1,2}\s*[.)]", "", text)
    t = re.sub(r"\^?\d{2,3}\s*[/(]\s*[A-Z0-9]+\s*[/)]?\s*\d?\^?|\[ ?P\.T\.O\. ?\]|\*[^*]{2,20}\*|SECTION\s*[-–]?\s*[A-E]", " ", t)
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()[:140]


def write_groups(hits: list[dict], root: Path, dest: Path):
    """Merge the same question appearing in several sets / years into one group and write a
    readable text file: one block per distinct question, listing every paper it appeared in."""
    groups: dict[str, dict] = {}
    for h in hits:
        if h["q"] == "?":
            key = "page:" + h["file"] + ":" + h["page"]
        else:
            key = _qkey(h["excerpt"])
        g = groups.setdefault(key, {"text": h["excerpt"], "seen": [], "score": h["score"]})
        f = Path(h["file"])
        g["seen"].append(f"{_paper_label(f, root)} {guess_set(f.name)} Q{h['q']} p{h['page']}")
        g["score"] = max(g["score"], h["score"])
    order = sorted(groups.values(), key=lambda g: (min(s.split()[0] for s in g["seen"]), -g["score"]), reverse=False)
    lines = [f"{len(order)} distinct questions/pages from {len(hits)} hits\n"]
    for i, g in enumerate(order, 1):
        lines.append(f"### G{i} | score {g['score']} | " + "; ".join(sorted(set(g["seen"]))))
        lines.append(re.sub(r"\s+", " ", g["text"]).strip())
        lines.append("")
    dest.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"hits": len(hits), "distinct": len(order), "written": str(dest)}, indent=2))


# --------------------------------------------------------------------- render

def cmd_render(a):
    try:
        try:
            import pymupdf as fitz  # type: ignore
        except ImportError:
            import fitz  # type: ignore
    except ImportError:
        raise SystemExit("PyMuPDF is needed to render pages (pip install pymupdf).")
    pdf = Path(a.pdf)
    outdir = Path(a.out) / "renders"
    outdir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf)
    pages = range(1, doc.page_count + 1) if a.pages == "all" else [int(p) for p in a.pages.split(",")]
    made = []
    for p in pages:
        pix = doc[p - 1].get_pixmap(matrix=fitz.Matrix(a.zoom, a.zoom))
        dest = outdir / f"{pdf.stem}_p{p}.png"
        pix.save(dest)
        made.append(str(dest))
    print(json.dumps({"pngs": made}, indent=2))


# ----------------------------------------------------------------------- main

def main():
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="teachme_cache", help="cache directory (default ./teachme_cache)")
    ap.add_argument("--force", action="store_true", help="re-download even if cached")
    sp = ap.add_subparsers(dest="cmd", required=True)

    sp.add_parser("session").set_defaults(fn=cmd_session)

    for name, fn in (("syllabus", cmd_syllabus), ("sqp", cmd_sqp)):
        p = sp.add_parser(name)
        p.add_argument("--cls", required=True)
        p.add_argument("--subject", required=True)
        p.add_argument("--session", help="e.g. 2026-27 (default: current)")
        p.set_defaults(fn=fn)

    p = sp.add_parser("papers")
    p.add_argument("--cls", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--years", default=f"2019-{dt.date.today().year}")
    p.add_argument("--keep-hindi", action="store_true")
    p.set_defaults(fn=cmd_papers)

    p = sp.add_parser("ncert")
    p.add_argument("--cls", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--book", help="book number / suffix, e.g. 1 for Part I")
    p.add_argument("--chapter", help="chapter number within the book")
    p.add_argument("--list", action="store_true", help="list books and their contents pages")
    p.set_defaults(fn=cmd_ncert)

    p = sp.add_parser("search")
    p.add_argument("--dir", required=True)
    p.add_argument("--terms", nargs="+", required=True)
    p.add_argument("--min-hits", type=int, default=1)
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--chars", type=int, default=700)
    p.add_argument("--save", help="write all matches to this JSON file")
    p.add_argument("--require", nargs="+", help="keep only hits containing at least one of these (cuts false positives)")
    p.add_argument("--only", default="", help="substring the file path must contain, e.g. _QP or 2025")
    p.add_argument("--group", help="write distinct questions (merged across sets/years) to this text file")
    p.set_defaults(fn=cmd_search)

    p = sp.add_parser("render")
    p.add_argument("--pdf", required=True)
    p.add_argument("--pages", default="1")
    p.add_argument("--zoom", type=float, default=2.0)
    p.set_defaults(fn=cmd_render)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
