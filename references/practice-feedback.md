# Practice, feedback and progress

How questions help the student practise and how the page records what they can do. The template
implements all of this; your job is the data that drives it.

## Contents
1. Answer checking for numericals
2. Mistake feedback
3. Graduated hints
4. MCQ and assertion-reason feedback
5. Written answers: value points and self-assessment
6. Interactive models
7. The progress model (what the page records)
8. Navigation and accessibility the template provides

---

## 1. Answer checking (`check`)

Give every numerical a `check` so the student can enter a final value and (optionally) intermediate
steps. They still work on paper; the box takes only the number and unit.

```json
"check": {"answer": 0.2, "units": ["M", "mol L-1", "mol/L", "mol dm-3", "molar"], "tol": 0.002,
          "prompt": "Enter (b), the molarity.",            // when the question has several parts
          "steps": [{"label": "Moles of NaCl", "unit": "mol", "answer": 0.1, "tol": 0.001, "expr": "5.85/58.5"}],
          "alts": [{"answer": 200, "units": ["mM"], "tol": 2}],   // other correct forms
          "mistakes": [{"answer": 0.0002, "tol": 0.000005, "msg": "Check the volume: 500 mL = 0.500 L."}],
          "note": "NCERT's key prints 0.459 (rounding)."}
```

* **Tolerance fits the quantity** - not a blanket percentage. Accept the values a careful student gets
  with the data's rounding (e.g. 0.458 and 0.459), and no wider. Temperatures: absolute tolerance in K.
  Over 5% needs `tolReason`. The build fails if `answer` is not within `tol` of an independent
  recomputation (`verify` or `check.expr`), or if a `mistakes` value falls inside the tolerance.
* **Units**: list every acceptable spelling. Case matters only for one-letter units (M ≠ m). `[]`
  means dimensionless. A right number with a missing unit is marked correct with a reminder.
* **Temperatures**: `"kind": "temperature", "scale": "K"|"C", "delta": ΔT` - the checker accepts the
  other scale automatically and recognises "you gave ΔT, not T" and K/°C slips.
* Give `steps` for 3-mark numericals so a student can find where they went wrong.

## 2. Mistake feedback

List the 2-4 wrong answers students actually reach and say what to check, specifically:
"Check whether you converted the solvent mass to kilograms" - not "Incorrect". The template also spots
×1000, ÷1000, ×2, ×½, ×3, sign errors and K/°C slips by itself. When the value matches nothing, the page
asks which step the student used instead of guessing their reasoning - do not write feedback that
claims to know their method from a final number alone.

## 3. Graduated hints (`hints`)

1-3 hints, gentlest first: (1) which idea or law applies, (2) the relationship and the first
conversion, (3) the set-up with numbers substituted. A hint never states the final answer. Using a hint
makes that attempt "solved with help".

## 4. MCQ and assertion-reason

* `explanation`: the correct reasoning.
* `optionNotes`: one entry per option, `""` for the correct one, otherwise the misconception that makes
  that option tempting ("0.0555 is 1/18: dividing by water's molar mass instead of total moles").
* Assertion-reason options are fixed (A-D); notes explain which statement fails and why.

## 5. Written answers

* `solution.points`: the value points an examiner looks for; `solution.steps[].m` only when the mark split
  comes from an official scheme (the page labels other splits "suggested").
* Optional `solution.rubric: [{t, m}]` for a custom self-assessment list; otherwise the page builds one
  from steps or points. Results are labelled **self-assessed** - never imply the page checked the
  student's writing. Drafts are optional and saved; paper is the expected medium.

## 6. Interactive models (`interactive`)

Use few, and only where moving a control explains the idea. Available widgets: `dilution`, `particles`
(dissociation/association and i), `vapour` (Raoult's law plot; deviation modes are labelled
illustration), `osmosis` (predict the direction of flow). Each asks for a prediction first, states its
assumptions, and labels itself "Calculated model" or "Illustration". New widgets need template code -
add them to `WIDGETS` in the template and to `WIDGETS` in `build.py`, with a static explanation and
keyboard-usable controls. Non-chemistry chapters often need none.

## 7. Progress model

The page keeps these apart (all per question id, so a question in a lesson and in Practice is one item):
* **Read** - lessons marked read. **Attempted** - any checked answer.
* **Solved with help** - correct after a hint, a revealed solution (in the attempt or the last 7 days),
  a second try, or a scaffold.
* **Solved independently** - correct at the first check with none of the above.
* **Self-assessed** - written answers scored against the rubric by the student.
* **Due** - missed, helped or below-full self-assessment comes back after a day; independent solves
  are spaced 1, 3, 7, 16, 35 days.
* Topic **Proficient** = all lessons read + 3 independent auto-checked solves + one independent solve a
  day or more later + nothing due. Shown with its criteria. Nothing is locked.
* Flashcards (Leitner boxes) are reported separately and never count as solving questions.
* Tests are untimed-study-separate; questions whose solution was viewed in the last 7 days are avoided.

Storage: browser `localStorage`, plus an optional private copy in the viewer's claude.ai account
(publish with capabilities `{db: {}, user: {}, downloads: true}`); export/import backup; honest messages
when storage is unavailable. See `updating-artifacts.md` before changing any id.

## 8. Navigation and accessibility (template)

Five sections (Learn, Practice, Revise, Test, Reference); "Continue studying" with the exact step;
desktop lesson sidebar and phone lesson menu; search (`/`) over lessons, worked steps, questions,
formulas, glossary and cards, opening at the matching block with a "Back to where you were" chip;
18-19 px lesson text in a ~72-character column; 44 px targets; visible focus; reduced motion; maths as
MathML (selectable, screen-reader readable); long equations scroll inside their row, never clipped.
Write content that keeps this working: give every figure `alt` text, keep tables narrow enough to scroll,
and put short labels on blocks you want findable.
