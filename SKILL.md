---
name: teach-me
description: Build a complete, exam-accurate interactive study artifact for one CBSE chapter (Classes 9-12) - step-by-step lessons with prerequisites, NCERT solutions, real past board questions (PYQs) with marking-scheme solutions, answer-checked practice with hints and feedback, flashcards, timed tests and a coverage map - researched from the official CBSE syllabus, sample papers, board papers and the current NCERT book. Use this whenever the user names a CBSE / NCERT chapter and wants to learn, study, revise or prepare it ("teach me Solutions from class 12 chemistry", "/teach-me electrochemistry", "make notes and PYQs for Nationalism in Europe", "I have boards, help me with Light - Reflection and Refraction"), even if they don't say "artifact" or "teach me". Also use it to update or upgrade a study page it built earlier.
---

# teach-me

The user gives a chapter (and usually class + subject). You produce one interactive study page they
will use as their **primary source for CBSE board exams**. That sets the bar:

* **Nothing wrong, nothing outdated.** Facts from the official sources for the *current* session,
  every numerical recomputed, every past-paper question traceable to a real paper and checked against
  its marking scheme. Say what you verified and what you did not; never claim a check you didn't run.
* **Nothing missing.** Everything CBSE can ask from this chapter this year is taught and practised,
  shown in a coverage map.
* **Teach, don't summarise.** Prerequisites first, small lessons, worked examples that explain where
  every number comes from, practice with honest feedback.
* **Take the time it needs.** This is a long job. Do not sample a few papers or thin out sections to
  finish sooner. Keep the user posted with one-line progress notes.

Bundled files (paths relative to this skill's folder):

| File | Read when |
|---|---|
| `references/sources.md` | Before research - official URLs, source priority, facts to re-check |
| `references/content-spec.md` | Before writing - what each section contains, quantity guide |
| `references/lesson-template.md` | Before writing lessons - prerequisites, lesson pattern, worked-example structure |
| `references/practice-feedback.md` | Before writing questions - answer checking, hints, feedback, progress model |
| `references/data-schema.md` | Before writing JSON - exact data format |
| `references/subjects.md` | Before writing - the section for this subject |
| `references/chemistry-guidance.md` | Chemistry / numerical-science chapters only |
| `references/verification-checklist.md` | Before Step 7 - checks, PYQ labels, coverage map, corrections |
| `references/qa-checklist.md` | Before Step 9 - functional checks |
| `references/updating-artifacts.md` | When changing a page that already exists |
| `scripts/cbse_fetch.py` | Research - downloads + text-extracts syllabus, SQP, past papers, NCERT; renders pages |
| `scripts/build.py` | Build - validates, recomputes numericals, checks answer boxes, test-renders math, writes the page |
| `scripts/ms_crosscheck.py` | Verify - finds each PYQ's key / final value in the same set's marking scheme |
| `scripts/preserve_check.py` | Updates - proves nothing was dropped or silently reworded |
| `assets/template.html` | Never edit per chapter; the build fills it |
| `assets/qa.js` | QA probe loaded into the local preview |
| `examples/xii-chemistry-solutions/` | A complete chapter built with this skill. Skim lesson `t2-3` in `10-lessons-t1-t2.json`, one patches file and `make_records.py` to calibrate depth and style. Its facts were checked for session 2026-27 only - never reuse them without re-checking. |

## Step 0 - Pin down the request

Identify class, subject (and paper variant: Maths Standard/Basic, Science Standard/Advanced in IX),
and the chapter. Infer the obvious; ask only if genuinely ambiguous. One chapter per artifact.
If the user wants an existing page changed, follow `references/updating-artifacts.md` first (back up,
keep ids, migrate progress).

Make a working folder (e.g. `teachme/<class>-<subject>-<chapter-slug>/`) with `cache/` for downloads
and `content/` for the JSON parts. Run scripts from there; pass paths as arguments.

## Step 1 - What is true *now*

```bash
python <skill>/scripts/cbse_fetch.py --out cache session
```
Prints today's session and the URLs to use. Read `references/sources.md` §5 as a list of things to
**re-check**, not as truth.

## Step 2 - Official syllabus for this session

```bash
python <skill>/scripts/cbse_fetch.py --out cache syllabus --cls XII --subject chemistry
```
Read the subject PDF's `.txt` fully: units and marks, this chapter's content line, anything deleted or
formative-only, the typology table. Record `syllabus.inSyllabus`, `syllabus.notForExam`, `meta.weightage`.

## Step 3 - The current NCERT chapter (the content authority)

```bash
python <skill>/scripts/cbse_fetch.py --out cache ncert --cls 12 --subject chemistry --list
python <skill>/scripts/cbse_fetch.py --out cache ncert --cls 12 --subject chemistry --book 1 --chapter 1
python <skill>/scripts/cbse_fetch.py --out cache render --pdf cache/ncert/lech101.pdf --pages 12,13
```
Confirm "Reprint <current session>". Read the whole chapter and the answers PDF: every heading,
definition, value, table, figure, example, in-text question and exercise. Note what the chapter
silently assumes from earlier classes - that becomes the "Before you start" sequence.

## Step 4 - Paper pattern from this session's sample paper

```bash
python <skill>/scripts/cbse_fetch.py --out cache sqp --cls XII --subject chemistry
```
(Class X and XII.) Read the general instructions and find every SQP question on this chapter
(`kind: "sqp"`), with its marking scheme. Also fetch the previous session's SQP.

## Step 5 - Past board papers (PYQs)

```bash
python <skill>/scripts/cbse_fetch.py --out cache papers --cls XII --subject chemistry --years 2019-2026
python <skill>/scripts/cbse_fetch.py --out cache search --dir cache/papers/XII_chemistry --only _QP \
    --terms "raoult" "osmo" ... --require "raoult" "osmo" ... --chars 3000 --group cache/groups.txt
```
`groups.txt` is the PYQ worklist (one block per distinct question with every set it appeared in;
discard false positives). For each real question record year, kind, set, number, marks, type, OR
choice and repeats. Take answers from the **same set's marking scheme**; render pages when text
extraction fails or the paper is scanned. Drop or adapt (and label) questions on topics no longer examined.

## Step 6 - Write the content

Read `content-spec.md`, `lesson-template.md`, `practice-feedback.md`, `data-schema.md` and your
subject's section of `subjects.md` (plus `chemistry-guidance.md` for numerical sciences). Write the JSON
parts into `content/` in several files.

* Optional prerequisites (`prereq`) with a diagnostic, then topics split into lessons following the
  lesson pattern - adapted, not forced, for conceptual lessons.
* Worked examples: Given → Find → Relationship and why → Convert → Calculate → Check, then a concise
  board answer. Never start a calculation with an unexplained "5/40".
* Questions: `check` (units, tolerances, step checks, specific mistake feedback) and graduated
  `hints` on numericals; `optionNotes` on MCQs; value points and self-assessment for written answers.
  Mark splits only where an official scheme gives them.
* Own words throughout; restate questions faithfully with their source code. Figures: generate SVG
  with a script, to scale, `@file:` references.

## Step 7 - Verify

Follow `references/verification-checklist.md`: recompute numericals (`verify`), run
`scripts/ms_crosscheck.py` and read by hand whatever it cannot locate, label every PYQ (`form`,
`ms.status`), check facts against NCERT and scope against the syllabus, get an independent review if you
can, then write `coverage` (generated from the content), `verification.checks` and `corrections`.

## Step 8 - Build

```bash
python <skill>/scripts/build.py content/ --out "<Chapter> - Class <N> <Subject>.html" --strict
```
Fix every error (structure, provenance, numericals, answer boxes that disagree with recomputation,
unknown ids in the coverage map, TeX that does not render) and rebuild until clean.

## Step 9 - Check it works, then publish

Run `references/qa-checklist.md` on the `.preview.html` through a local server: widths 320, 390, 768
and 1280, maths not clipped, feedback and progress labels honest, search and return, persistence,
backup restore, hidden test answers, keyboard. Fix and re-run.

Publish the built `.html` (not the preview twin) with the Artifact tool, `icon: "book"`, capabilities
`{"db": {}, "user": {}, "downloads": true}` (private progress copy in the student's account, backup file
download), and a one-sentence description. For an existing page publish to its `url`. Without an
Artifact tool, give the user the HTML file.

Then tell the user: what's inside (counts per section), which session's syllabus and which years of
papers, what was verified and how, what is still open, and that progress is saved in the browser (with
an optional account copy and a backup button). For an update, report page changes and anything else
changed separately.

## If something can't be fetched

Follow `references/sources.md` §6. Never fill the PYQ section from memory or third-party lists, and
never present a question as "CBSE 20xx" unless you have seen it in that paper. Say plainly what is missing.
