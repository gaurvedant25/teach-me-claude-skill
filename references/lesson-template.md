# Lessons, prerequisites and worked examples

Read before writing `topics`. The goal: a student who has never seen the topic can learn it from the
page alone, and can see *why* every step is taken, not only what to write.

## Contents
1. Prerequisites ("Before you start")
2. Splitting topics into lessons
3. The lesson pattern (and when to drop parts of it)
4. The worked-example structure
5. Partly worked, independent and application questions
6. Writing for understanding
7. A complete example to copy from

---

## 1. Prerequisites

Before the first lesson, list the tools the chapter silently assumes (earlier-class maths, units,
vocabulary, a law from a previous chapter). Write them as an optional `prereq` sequence:

* 3-6 short refresher units (`prereq.units`, same shape as a lesson), each 5-10 minutes, each with one
  worked example and one `try` question.
* A diagnostic of 5-8 auto-checked questions (`prereq.diagnostic`), each with `unit` pointing at the
  refresher that fixes it, specific mistake feedback and 1-2 hints.
* The student can skip or return at any time; nothing is locked.

What to cover depends on the chapter. Chemistry numericals: moles and molar mass, reading formulas and
counting atoms, g→kg and mL→L, °C→K, powers of ten, rearranging equations, density, solute/solvent/
solution. Physics: units and prefixes, vectors, rearranging, graphs. Maths: the algebra the chapter
uses. Theory subjects (history, English) usually need a short vocabulary or timeline refresher instead,
or none - do not invent a prerequisite unit just to have one.

## 2. Splitting topics into lessons

A topic follows an NCERT section. Split it into lessons (`topics[].lessons[]`) of 10-25 minutes, one
idea each. Signs a lesson is too long: more than one new formula, more than one worked example of a
different kind, or the student would need a break in the middle. Lesson ids are `<topic>-<n>` and must
never change once published (progress is keyed by them).

## 3. The lesson pattern

Each lesson, in this order:

| Part | Block(s) | Notes |
|---|---|---|
| 1. Learning objective | `objective` (lesson field) | "Calculate X from Y and explain each step" - an action the student can check |
| 2. Plain-English explanation | `p` | The idea in everyday words before any symbols |
| 3. Reasoning (why it happens) | `callout kind: "why"` | Molecular / physical / historical cause - the part that makes answers make sense |
| 4. Formula with every symbol, unit, condition | `formula` with `symbols[]`, `conditions`, `status` | `status`: exact, definition, empirical (experimental law), ideal, dilute, approx |
| 5. Fully explained worked example | `worked` (section 4) | Every number's origin and every operation explained |
| 6. Partly completed problem | `try role: "partial"` + question with `scaffold` | First step(s) given; the student finishes |
| 7. Independent problem | `try role: "independent"` | Same idea, new numbers, no scaffold |
| 8. Conceptual or unfamiliar application | `try role: "apply"` | MCQ/A-R on the concept, a PYQ, or a twist |
| 9. Recap and next step | `recap` with `items[]`, `next` | 3-4 bullets; name the next lesson |

When to adapt (do not force every lesson into an identical shape):
* **Conceptual lessons** (definitions, classifications, theory answers): part 4 may be absent; part 5
  becomes a worked *written answer* (`worked` with `steps` and `answer`, no `calc`); part 6 is optional.
* **Short lessons** (one definition and a table) may merge parts 2-3.
* **Non-numerical subjects**: part 5 is a model answer with the value points and why each earns credit;
  part 6 can be a partly written answer to complete.
Keep essential reasoning visible. Put extra detail, alternative methods and edge cases in at most one
`details` block per idea - never a `details` inside a `details`.

Also use: `callout kind: "notation"` where a symbol means different things in different places (M for
molarity vs molar mass), `interactive` when a model genuinely explains something (section 6 of
`practice-feedback.md`), `svg` for every diagram NCERT asks students to draw or read.

## 4. The worked-example structure

Every calculation example (`type: "worked"`) follows:

**Given → Find → Relationship and why → Convert units → Substitute and calculate → Interpret and check**,
then a concise **board-exam answer**.

```json
{"type": "worked", "title": "...", "source": "NCERT Example 1.2",
 "problem": "...",
 "given": ["5 g NaOH", "450 mL of solution", "Na = 23, O = 16, H = 1"],
 "find": "Molarity",
 "relation": "Molarity = moles of solute ÷ litres of solution",
 "why": "The question gives grams and millilitres; molarity needs moles and litres.",
 "convert": [{"t": "M(NaOH) = 23 + 16 + 1 = 40 g mol$^{-1}$", "why": "one Na, one O, one H - so 40 g is 1 mol"},
             {"t": "moles = 5 g ÷ 40 g mol$^{-1}$ = 0.125 mol", "why": "**Why divide 5 by 40?** ..."},
             {"t": "450 mL ÷ 1000 = 0.450 L", "why": "1 L = 1000 mL"}],
 "calc": [{"t": "0.125 ÷ 0.450 = 0.278 mol L$^{-1}$", "why": "divide by the final volume of the solution"}],
 "check": "Sense check and units",
 "answer": "0.278 M",
 "board": [{"t": "..."}, {"t": "..."}],
 "boardNote": "What to write in the exam vs what is for understanding",
 "verify": [{"expr": "23+16+1", "expected": 40}, {"expr": "(5/40)/0.450", "expected": 0.278}]}
```

Rules:
* Never start with a bare "5/40". Say where each number comes from and why we multiply, divide, add
  or subtract. Show unit cancellation when it helps.
* A `why` that starts with `**Why ...?**` is shown as that question; otherwise it is labelled "Why this
  step?". Give one wherever a step is a choice: choosing a 100 g basis, solvent vs solution mass, which
  value of R, rounding, dropping a small term (and say it is an approximation).
* Keep full precision through the working; round once at the end, to the data's precision.
* `board` is the short answer a student writes: formula, substitution with units, result with unit.
  Show `m` (marks) only when they come from an official marking scheme for that question.
* The build requires `given`, `find`, `relation`, `calc`, `answer` and `verify` on calculation examples.

## 5. Partly worked, independent and application questions

* Partial: a normal question with `scaffold: [{t: ...}]` holding the first step(s). It is recorded as
  "solved with help" even when correct, because part of the working was given.
* Independent: same skill, different numbers or context; give it `check`, `hints`, and mistake feedback.
* Apply: concept MCQs with `optionNotes`, an A-R, a PYQ, or an unfamiliar context.
* Reuse existing question ids in `try` blocks rather than duplicating questions; one question appearing
  in a lesson and in Practice is the same item and its progress is shared.

## 6. Writing for understanding

* Introduce a term before you use it; define it in plain words, then the board wording.
* Respectful, simple English; short sentences; no filler or motivational fluff.
* Say what is approximate: "for dilute solutions", "assuming complete dissociation", "1 L of water ≈ 1 kg".
* Where a textbook figure looks inconsistent, explain the discrepancy rather than copying or silently
  "fixing" it, and log it in `corrections` (see `verification-checklist.md`).

## 7. Complete example

`examples/xii-chemistry-solutions/content/10-lessons-t1-t2.json`, lesson `t2-3` (Molarity and dilution):
objective, explanation, reasoning callout, formula with symbols and status, notation callout, the NaOH
worked example in full, a dilution formula marked exact, the dilution interactive, a partial problem
(`t2-3-p`, defined in the same file), an independent problem (`t2-q2`, upgraded through
`70-patches-t2.json`), application questions and a recap. Copy its shape, not its content.
