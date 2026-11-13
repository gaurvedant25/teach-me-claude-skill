# Content data format (what `scripts/build.py` reads)

The page template (`assets/template.html`) is fixed; you only write data. Write it as a **folder of JSON
parts** merged in file-name order (dicts merge, lists concatenate), so no single file gets huge:

```
content/
  00-meta.json        meta, syllabus, sources, verification, revision
  01-records.json     coverage, verification.checks, corrections (generate from the content)
  05-prereq.json      {"prereq": {"intro", "units": [...], "diagnostic": [...], "questions": [...]}}
  10-lessons-*.json   {"topics": [ {..., "lessons": [...]} ], "questions": [lesson-specific questions]}
  20-formulas.json    {"formulas": [...], "terms": [...]}
  30-ncert.json       {"ncert": {"intext": [...], "exercises": [...]}}
  40-pyqs.json        {"pyqs": [...]}
  50-practice.json    {"questions": [...]}
  60-flashcards.json  {"flashcards": [...]}
  70-patches-*.json   {"patches": {"<question id>": {teaching fields to add}}}
  _superseded/        old parts kept for reference; not built
```

Build: `python scripts/build.py content/ --out <name>.html` (also writes `<name>.preview.html` for local viewing).

## Contents
1. Writing text: math, chemistry, emphasis
2. meta, syllabus, sources, verification, revision
3. topics, lessons and content blocks
4. questions (all kinds) - common fields, then per type
5. PYQ provenance, NCERT references, `verify`
6. formulas, terms, flashcards
7. SVG diagrams that work in light and dark mode

---

## 1. Writing text

Every text field accepts:

| Write | Renders as |
|---|---|
| `$...$` | inline math (KaTeX -> MathML) |
| `$$...$$` | display math |
| `$\ce{H2SO4}$`, `$\ce{A + B -> C}$`, `$\ce{N2 + 3H2 <=> 2NH3}$` | chemistry (mhchem) |
| `$\pu{1.86 K kg mol-1}$` | units with proper spacing (mhchem) |
| `**bold**`, `*italic*`, `==highlight==` | emphasis / marker highlight for the one phrase examiners look for |
| `` `code` `` | monospace (programming, IUPAC fragments) |
| `\$` | a literal dollar sign |

* LaTeX backslashes may be written single (`$\frac{a}{b}$`) - the loader escapes them. Consequence:
  `\n` is **not** a newline. Use separate blocks / list items / steps.
* For a line break *inside* math (aligned / cases), write `\\\\`.
* Use `\times`, never `x`, for multiplication; `\circ` for standard-state (`$E^\circ$`, `$p^\circ_A$`);
  `\Delta`, `\pi`, `\Lambda_m`. Units upright: `$\text{K kg mol}^{-1}$` or `$\pu{K kg mol-1}$`.
* The build test-renders every TeX snippet with the same KaTeX build the page uses; fix every error it lists.

## 2. Top-level objects

```json
{
  "meta": {
    "board": "CBSE", "class": "XII", "subject": "Chemistry", "subjectCode": "043",
    "session": "2026-27", "chapter": "Solutions", "chapterNo": 1, "unitLabel": "Unit",
    "book": "NCERT Chemistry Part I (Reprint 2026-27), Unit 1",
    "weightage": "7 of 70 theory marks",
    "generated": "2026-10-19", "lastVerified": "2026-10-19",
    "accent": "chemistry",
    "summary": "Two or three sentences: what the chapter is about and why it matters in the paper.",
    "pattern": ["How this chapter shows up in the board paper (from SQP + PYQ analysis), one bullet each."],
    "studyPlan": [{"title": "Day 1 - Concentration terms and Henry's law", "items": ["Topics 1-3", "NCERT Ex 1.1-1.8"], "time": "2 h"}],
    "testPattern": [{"type": ["mcq"], "marks": 1, "n": 5}, {"type": ["ar"], "marks": 1, "n": 2},
                    {"marks": 2, "n": 2}, {"marks": 3, "n": 2}, {"type": ["case"], "n": 1}, {"marks": 5, "n": 1}],
    "targets": {"flashcards": 30}
  },
  "syllabus": {
    "inSyllabus": ["Types of solutions", "Expressing concentration of solutions", "..."],
    "notForExam": [{"topic": "Surface Chemistry", "note": "Moved to formative assessment only in 2026-27 - not in the board paper."}],
    "note": "Anything a student should know about scope this year.",
    "source": "CBSE Chemistry curriculum 2026-27, Unit 1"
  },
  "sources": [{"title": "CBSE Curriculum 2026-27, Chemistry (043)", "url": "https://...", "note": "Unit list, marks, formative-only topics"}],
  "verification": {"checkedOn": "2026-10-19", "notes": ["All 23 numericals recomputed in Python (build verify step).", "..."]},
  "revision": {
    "keyPoints": ["..."], "mistakes": ["..."], "mnemonics": ["..."], "examTips": ["..."], "lastMinute": ["..."]
  }
}
```

* Theme: the page is always white in the student's logo colours - yellow #FFC531 and near-black
  #15171C - with the logo (open book, yellow dot) in the header and as the tab icon, for every subject.
  Yellow is used only as a fill with dark text; readable accents use the darker amber built into the
  template. Do not draw diagrams in raw yellow (use the `tm-*` classes). `meta.accent` changes only the
  yellow fill and may be set to a hex colour only if the user asks for a
  different colour; subject names are ignored.
* `meta.testPattern`: the mix for the Chapter test tab. Scale the board pattern down to one chapter.
  Groups with no `type` exclude mcq/ar/case. Default is shown above.
* `meta.targets`: lower a coverage minimum only when the chapter truly has less (say why in `verification.notes`).
* `syllabus.notForExam` is required. Use `[]` and say "nothing excluded" in `note` when that is the case.
* `verification.checks: [{what, how, status: done|partial|open, result}]`, `coverage: [{kind, ref, where[], status: covered|expand|verify, note?}]`
  and `corrections: [{item, change, status}]` are described in `verification-checklist.md`.
* `prereq.units` are lessons (section 3); `prereq.diagnostic` and `prereq.questions` are questions
  (section 4); a diagnostic question's `unit` names the refresher that fixes it.

## 3. Topics and blocks

```json
{"id": "t4", "title": "Vapour pressure and Raoult's law", "ncertRef": "1.4", "minutes": 45, "summary": "One line.",
 "lessons": [{"id": "t4-1", "title": "Raoult's law for two volatile liquids", "ncertRef": "1.4.1", "minutes": 18,
              "objective": "Calculate partial and total vapour pressures ...", "blocks": [ ...blocks... ]}]}
```
A topic has `lessons` (preferred; see `lesson-template.md`) or, for very short topics, `blocks` (shown as
one lesson `<id>-1`). Never both. Lesson ids are permanent.

Block types:

| type | fields | use for |
|---|---|---|
| `p` | `text` | a paragraph |
| `h` | `text` | a sub-heading inside a topic |
| `list` | `items[]`, `ordered?`, `title?` | points, features, differences |
| `steps` | `items[]` (string or `{t, m}`), `title?` | procedures, derivations, mechanisms |
| `formula` | `tex`, `label?`, `where?` | key equations (display); `where` explains each symbol + units |
| `table` | `head[]`, `rows[][]`, `caption?` | comparisons, data (cells accept rich text) |
| `callout` | `kind`, `text`, `title?` | kinds: `tip`, `exam`, `mistake`, `remember`, `mnemonic`, `ncert`, `why`, `real`, `warning`, `beyond` |
| `example` | `title`, `source?`, `question`, `steps[]`, `answer`, `hideSolution?`, `figure?`, `verify?` | worked examples (NCERT examples: `source: "NCERT Example 1.4"`) |
| `svg` | `svg`, `caption?`, `alt?` | diagrams, graphs, apparatus, structures |
| `flow` | `items[]` of `{"node": ...}` / `{"arrow": "reagent / condition"}`, `caption?` | reaction sequences, processes, cause -> effect chains |
| `compare` | `left{title, items[]}`, `right{...}`, `more?[]` | X vs Y side by side |
| `quote` | `text`, `cite?` | poetry / source lines (literature, history sources) |
| `img` | `src` (`data:image/...` only), `alt`, `caption?` | rare; prefer SVG |
| `check` | `questionIds[]`, `title?` | quick-check questions (any ids) |
| `objective` | `text` | normally set as the lesson's `objective` field instead |
| `worked` | `title`, `source?`, `problem`, `given[]`, `find`, `relation`, `why?`, `convert[{t, why?}]`, `calc[{t, why?}]`, `check?`, `answer`, `board?[{t, m?}]`, `boardNote?`, `figure?`, `verify` | worked examples (`lesson-template.md` §4); a written-answer example uses `steps` + `answer` instead of `calc` |
| `try` | `questionIds[]`, `role`: `partial` / `independent` / `apply` / `check` | the practice parts of a lesson |
| `details` | `title`, `blocks[]` | one expandable layer for extra detail or an alternative method (no nesting) |
| `interactive` | `widget`: `dilution` / `particles` / `vapour` / `osmosis`, widget options | see `practice-feedback.md` §6 |
| `recap` | `items[]`, `next?` | end of every lesson |

`formula` blocks also take `symbols: [[symbol, meaning, unit]]`, `conditions` and `status`
(`exact`, `definition`, `empirical`, `ideal`, `dilute`, `approx`). `callout` also has kind `notation`.
`example` (older) blocks still render, but new content uses `worked`.

`callout kind: "beyond"` is for useful context that is *not* examined - it renders with a
"Beyond the syllabus (not examined)" label so the student knows to skip it before exams.

## 4. Questions

One shape for practice questions (`questions`), past papers (`pyqs`) and NCERT (`ncert.intext`,
`ncert.exercises`, `ncert.exemplar`). Ids must be unique across all lists.

Common fields: `id`, `type`, `topic` (topic id), `marks`, `difficulty` (`easy`|`medium`|`hard`),
`competency` (true for application / case / data questions), `q` (stem), `figure` (svg),
`source` (see 5), `alt` (an internal-choice OR question, same shape).

| type | extra fields |
|---|---|
| `mcq` | `options[]`, `answer` (0-based index), `explanation` (why the right one is right AND why the tempting wrong one is wrong) |
| `ar` | `assertion`, `reason`, `answer` 0-3 (0: both true, R explains A; 1: both true, R doesn't explain; 2: A true R false; 3: A false R true), `explanation` |
| `tf`, `fill`, `oneword` | `answer` (string), `explanation?` |
| `short`, `long`, `numerical`, `diagram`, `map` | `solution: {points?[], steps?[{t, m}], final?, notes?, figure?}` |
| `case` | `passage`, `parts[]` (each a full question, usually mcq / short; give `marks` and `label` ("a", "b", ...) per part; an internal-choice OR inside a case goes in that part's `alt`) |

A past paper's case-study passage is often long: summarise it faithfully in your own words (start with
"The passage (summarised): ...") and keep every fact or number the parts rely on.

Teaching and feedback fields (any question; details in `practice-feedback.md`):
`check` (answer box: `answer`, `units`, `tol`, `kind`, `scale`, `delta`, `prompt`, `steps`, `alts`, `mistakes`, `note`),
`hints[]`, `optionNotes[]` (MCQ), `teach` (full reasoning in worked-example form, shown with the solution),
`scaffold[]` (steps already given - partial problems), `concept` (short tag used to find a fresh
equivalent question for review), `solution.rubric[{t, m}]`.

`solution`:
* `steps` - the answer as a student should write it, one step per line. Put `m` (marks) only when the
  split comes from the official marking scheme for that question; otherwise the page labels the split
  "suggested". Step marks should add up to `marks`.
* `points` - "value points" an examiner looks for (theory answers); keep them short.
* `final` - the boxed final answer with units and correct significant figures.
* `notes` - examiner-style advice: what loses marks, the alternative accepted answer, etc.

## 5. Provenance and verification

**PYQ** (`pyqs[]`), all four of year / set / q / marks are required by the build:

```json
"source": {"year": 2025, "kind": "main", "set": "56/4/1", "q": "28", "marks": 3,
           "repeats": ["2025 56/4/2 Q27", "2025 56/4/3 Q30"]}
```
`kind`: `main`, `compartment`, `second` (Class X second exam), `term1`, `term2` (2022), `sqp`, `other`.
For sample papers use `"kind": "sqp"`, `"set": "SQP 2026-27"` and the session's first year as `year`;
they are shown as sample papers and left out of the year-wise trend table.
Use `repeats` when the same question appears in other sets - one entry, many codes. Write `q` in
your own words but keep every number, compound, condition and what is asked exactly as on the
paper. Label each PYQ with `form` (`original` / `restated` / `adapted` + `adaptNote`) and
`ms: {status: checked|key|computed|unavailable, note?}` - see `verification-checklist.md` §3.

**patches** - `{"patches": {"py12": {"ms": {...}, "hints": [...]}}}` adds fields to an existing
question (case parts as `"<case id>.<n>"`). Dict values merge, others replace; changing `q`, `options`,
`answer`, `id` or `source` is refused. Use patches to upgrade questions without rewriting their files.

**NCERT** (`ncert.*`): `"source": {"book": "NCERT", "ref": "Exercise 1.12"}` or
`"ref": "Intext 1.3"`, `"Example 1.4"`; exemplar: `"book": "NCERT Exemplar", "ref": "Q 42 (Short answer)"`.

**verify** - required on every `numerical` question, allowed on any question / example. A Python
expression that recomputes the answer from the question's data; the build evaluates it with the
`math` module available (`log10`, `log`/`ln`, `exp`, `sqrt` ...) and fails on mismatch:

```json
"verify": {"expr": "1.86 * (5/60) / 0.250", "expected": 0.62, "tol": 0.01}
"verify": [{"expr": "...", "expected": 3.0}, {"expr": "...", "expected": 0.0821, "tol": 0.005}]
"verify": "n/a: answer is a ratio stated in words, checked by hand"
```
`tol` is relative (default 1%). Use the same rounded constants the question gives (board papers
give $R$, $K_f$, log values) so the check matches what a student would get by hand.

## 6. Formulas, terms, flashcards

```json
"formulas": [{"name": "Raoult's law (non-volatile solute)", "tex": "\frac{p_1^\circ - p_1}{p_1^\circ} = x_2",
              "where": "$p_1^\circ$ vapour pressure of pure solvent ...", "units": "dimensionless",
              "status": "ideal", "conditions": "...", "lesson": "t6-1", "topic": "t6"}],
"terms": [{"term": "Azeotrope", "def": "Board-ready one- or two-line definition, NCERT wording where it matters.", "topic": "t5"}],
"flashcards": [{"id": "fc-001", "front": "What is the van't Hoff factor of $\ce{K2SO4}$ for complete dissociation?", "back": "$i = 3$", "topic": "t7"}]
```
Flashcard `id`s are permanent; append new cards at the end. For non-numerical subjects, `formulas` can hold `"text"` instead of `"tex"` (e.g. accounting
formats, grammar rules) and set `meta.formulasLabel` (e.g. "Key dates & terms").

## 7. SVG diagrams

Diagrams sit on the page's surface colour (the theme is light only, but keep colours as classes):
* Use `stroke="currentColor"` / `fill="currentColor"` for ink, `fill="none"` for open shapes.
* Classes for colour: `tm-acc` (accent stroke), `tm-accf` (accent fill), `tm-soft` (pale accent fill),
  `tm-muted` / `tm-mutedf`, `tm-line` (light grid lines), `tm-good`/`tm-goodf`, `tm-bad`/`tm-badf`.
* `<text>` inherits the ink colour and UI font automatically; set `font-size` (12-14 in a 600-wide viewBox).
* Always give a `viewBox` and no fixed width so it scales on phones; keep labels inside the box.
* Prefer generating figures with a script and loading them with `"svg": "@file:figures/name.svg"`
  (any string value of the form `@file:<path relative to content/>` is replaced by that file's text).
* No `<script>`, no event handlers, no external images, no literal hex colours.
* Graphs must be to scale: if you draw $p$ vs $x_A$ for an ideal solution, the lines are straight and
  meet the axes at the stated values. Label axes with quantity and unit.
