# What a finished chapter contains

The student uses this page as their *primary* source for the board exam. Judge every section by one
question: if this were the only thing they studied, would they walk into the exam able to answer
anything CBSE could ask from this chapter, in the way the marking scheme rewards?

## Contents
0. How the page is organised
1. Teaching notes (Learn)
2. Formulas & terms
3. NCERT solutions
4. Past papers
5. Practice bank
6. Flashcards
7. Chapter test, Revise, Overview, Sources
8. Quantity guide
9. Writing standards

---

## 0. How the page is organised

Five sections, all built by the template from your data: **Learn** (continue studying, optional
"Before you start" prerequisites, chapter map, lessons), **Practice** (recommended next question, NCERT,
past papers, more questions, mixed practice), **Revise** (flashcards, review queue, saved items,
summaries), **Test** (timed papers, separate from untimed study) and **Reference** (formulas, glossary,
syllabus and exam pattern, coverage map, sources and checks, progress and backup). Every resource must
be reachable from one of them.

Companion files: `lesson-template.md` (lessons, prerequisites, worked examples), `practice-feedback.md`
(answer checking, hints, feedback, progress), `verification-checklist.md` (checks, labels, coverage,
corrections), `chemistry-guidance.md` (numerical sciences), `qa-checklist.md` (before finishing).

## 1. Teaching notes (Learn)

* **Cover every sub-topic in the official syllabus for this chapter, in NCERT order.** Use the NCERT
  section headings as the topic spine (one topic per NCERT section, split a long section, merge
  very short ones). Map each topic to its NCERT section in `ncertRef`.
* Teach, don't summarise. Split each topic into lessons and follow the lesson pattern in
  `lesson-template.md` (objective, plain explanation, reasoning, formula with symbols/units/conditions,
  worked example, partly worked problem, independent problem, application, recap). Adapt it for
  conceptual lessons rather than forcing an identical layout. A student who has never seen the topic
  should be able to learn it from this page alone.
* Start with an optional "Before you start" set of refreshers and a diagnostic when the chapter relies
  on earlier skills (`lesson-template.md` §1).
* Every definition, law statement, value, reaction, exception and named example that NCERT gives
  must appear - board answers are marked against NCERT. Where NCERT's exact phrase is what earns the
  mark (e.g. a law's statement), keep the key words and highlight them with `==...==`.
* Every NCERT worked example appears as a `worked` block (`source: "NCERT Example x.y"`), explained
  Given → Find → Relationship and why → Convert → Calculate → Check, then a concise board answer.
* Diagrams: draw every diagram / graph NCERT uses that a student may be asked to draw or interpret
  (as SVG, to scale), plus any that make an idea click. Label exactly as a board answer would.
* Use `flow` blocks for reaction sequences, conversions, processes, cause-effect chains.
* Use `compare` / `table` for every "differentiate between" pair that NCERT or PYQs touch.
* Callouts: `exam` for what PYQs repeatedly ask from this topic (name the years), `mistake` for
  errors that lose marks (sign conventions, units, significant figures, missing conditions),
  `mnemonic` only when a genuinely useful one exists, `beyond` for interesting non-examined context
  (keep these rare and clearly separated).
* Each lesson ends with `try` blocks (partial / independent / apply) and a `recap`.
* Content listed under `syllabus.notForExam` is either omitted or, if a short mention helps
  understanding, put in a `beyond` callout. Never teach it as if it were examined.

## 2. Formulas & terms

* Every formula in the chapter with: what each symbol means, units, conditions of validity, and the
  common alternate forms (e.g. $\Delta T_f = K_f m$ and $M_2 = \dfrac{1000\,K_f w_2}{\Delta T_f\, w_1}$).
* Every defined term with a board-ready definition (one to two lines).
* Constants and standard values the chapter uses, exactly as NCERT states them.

## 3. NCERT solutions

* **All** in-text questions and **all** end-of-chapter exercise questions that are still in the
  syllabus. If NCERT's rationalised book dropped a question, it is not in the PDF - don't add it back.
  If an exercise question is on a topic now formative-only, keep it but mark it in `solution.notes`.
* Full step-by-step solutions in board style. Numerical answers verified (`verify`) and answer-checked
  in the page (`check` with units, tolerance, step checks, mistake feedback) plus graduated `hints`. Compare with NCERT's own answer key (`<code>an.pdf`) and note any disagreement in
  `solution.notes` (explaining which is right and why).
* Exemplar: include a selection (aim for 15-30) of the best exemplar questions that are in the
  current syllabus, especially MCQs, A-R and HOTS. Mark their source.

## 4. Past papers (PYQs)

* Mine **every** board paper and compartment paper you can fetch from 2019 to the latest
  (all sets), plus the current and previous year's SQP, for questions from this chapter.
* One entry per distinct question; identical / near-identical questions across sets go in `repeats`.
* Keep each question's data and demand exact; restate the wording in your own words.
* Skip questions whose topic is no longer examined (check against `syllabus.notForExam` and the
  current syllabus text) - or, if a question is mostly valid, adapt it and say so in `notes`.
* Solutions follow the official marking scheme's value points and mark split (`steps[].m`),
  written in your own words. Label every PYQ with `form` and `ms.status` from the checks you actually
  ran (`verification-checklist.md` §3); describe how often a topic appeared as history, not prediction. If you think the marking scheme is wrong, say so in `notes` with the
  reason, and give the correct answer.
* Questions with figures: re-draw the figure in SVG (render the page to PNG to see it).
* The Overview tab's trend table is computed from these entries - tag `topic` accurately.

## 5. Practice bank

Original board-style questions covering every topic and every question type the paper uses for
this subject (see the SQP): MCQ, assertion-reason, case/source-based (with a realistic passage or
data table/graph), 2-mark, 3-mark, 5-mark, numericals at graded difficulty, competency-based items.
* Spread across topics in proportion to their PYQ weight; every topic gets at least 3 questions.
* MCQ distractors should be the actual wrong answers students reach (wrong $i$, forgotten unit
  conversion, sign error); `optionNotes` explains each one's misconception.
* Numericals use calculator-free numbers when the board paper bans calculators (it does for
  Chemistry / Physics / Maths), or supply log values in the question as CBSE does.
* Mark `competency: true` on application / analysis / data-interpretation items.

## 6. Flashcards

Atomic, one fact per card: definitions, laws, formulas (front: name/situation; back: formula),
units, exceptions, examples, "why" questions, reagent -> product, graph shapes. Cover every topic.

## 7. Revise, Reference and records

* **Reference → Syllabus & exam**: `meta.summary`, syllabus in/out lists, `meta.pattern` (how it is
  examined, from SQP + PYQ evidence; frequency as history, not a forecast).
* **Revise → Summaries**: key points (the whole chapter in ~15-25 bullets), mistakes, mnemonics, exam
  tips specific to this chapter, last-minute checklist. Exam tips about marks must cite the scheme
  (e.g. "the 2019 Set 56/3/1 scheme deducts ½ mark for a missing unit") - never blanket rules.
* **Reference → Coverage map, Sources & checks**: `coverage`, `sources`, `verification.checks`,
  `corrections` - see `verification-checklist.md`.

## 8. Quantity guide (a typical science / maths chapter)

The build warns below the minimums; most chapters should land well above them.

| Section | Minimum | Typical |
|---|---|---|
| Topics | 4 | 6-12 |
| Formulas + terms | 8 | 15-40 |
| NCERT | all in-syllabus intext + exercise | 20-60 |
| PYQs (distinct) | 15 if the papers have them | 25-80 |
| Practice | 40 | 60-120 |
| of which MCQ + A-R | 15 | 25-50 |
| Flashcards | 30 | 40-90 |

For short chapters (a poem, a small SST chapter) lower `meta.targets` and say why in `verification.notes`.

## 9. Writing standards

* Accuracy over volume: a question you are not sure of is left out, not guessed. Every claim must be
  checkable against NCERT or an official CBSE document.
* Plain, direct English a 16-year-old reads easily. Short sentences. Indian English conventions
  (vapour, colour, litre) and SI units as NCERT uses them.
* Two layers for calculations: the teaching layer (every number's origin and every operation's reason)
  and the board layer (formula, substitution with units, result with unit and sensible significant
  figures). For theory, the value points in the order examiners expect.
* State approximations and idealisations where they are used.
* No filler, no motivational fluff, no emojis.
