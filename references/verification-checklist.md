# Verification, traceability and honest claims

The page is a student's primary source. A confident error costs marks; an unchecked claim that says
"verified" is worse. Run these checks, record what you did with counts, and say plainly what you did not.

## Contents
1. Rules for claims
2. Checks to run (with the tool for each)
3. Past-paper labels (form and marking-scheme status)
4. Coverage map
5. Corrections log
6. What goes in Reference → Sources & checks

---

## 1. Rules for claims

* Never invent a source, paper code, date, mark split or "checked" status. A source link is not proof
  that each answer was checked.
* Distinguish *verified* (you compared it, and can say how) from *reasoned* (worked out independently)
  from *open* (not checked). Use those words in the page.
* Prefer question-specific evidence to blanket rules: not "every step carries half a mark" but "the
  2019 Set 56/3/1 scheme deducts ½ mark for a missing unit on this question".
* Historical frequency is information, not a prediction: "appeared in 2023, 2025 and 2026", never
  "will come".

## 2. Checks to run

| Check | How | Tool |
|---|---|---|
| Numericals | `verify` expressions recompute every numerical answer and worked example from its own data | `build.py` (fails on mismatch) |
| Answer boxes | every `check.answer` agrees with a recomputation; mistakes lie outside tolerance | `build.py` |
| PYQ keys | each MCQ/A-R key found in the same set's marking scheme | `scripts/ms_crosscheck.py` |
| PYQ numericals and theory | final values found in the same set's scheme text; anything not found is read by hand (render scheme pages whose equations are images) | `ms_crosscheck.py` + `cbse_fetch.py render` |
| NCERT facts | every definition, value, table and example against the current reprint | read the chapter `.txt` |
| Syllabus scope | nothing out of syllabus taught as examined | curriculum PDF |
| Maths | every TeX string renders | `build.py` (Node KaTeX) |
| Nothing lost (updates) | old ids, wording, flashcards, figures still present | `scripts/preserve_check.py` |
| Second review | a separate reviewer hunts for errors with evidence | subagent if available, else a slow re-read |

`ms_crosscheck.py` handles combined-set files (2020: "56/5/1,2,3"), blind-candidate sets ("56(B)") and
(i)-(iv) keyed options, but schemes vary: treat "not located" as "read it yourself", never as "fine".
When a scheme rounds early and prints a slightly different value, accept both in `check` (`alts`) and
note the scheme's figure on the question.

## 3. Past-paper labels

Every PYQ carries:
* `form`: `original` (verbatim - rarely appropriate; copyright), `restated` (own words, every number
  and demand kept), or `adapted` (anything changed, including a summarised case passage) with `adaptNote`.
* `ms.status`: `checked` (answer/value points compared with that set's scheme in this build), `key`
  (MCQ/A-R key matched), `computed` (worked out independently, no scheme available), `unavailable`
  (scheme unreadable). `ms.note` records rounding differences and the scheme's own wording when it
  differs from yours.
Add these with a `patches` file so the original question text stays untouched (see `data-schema.md`).

## 4. Coverage map (`coverage`)

One entry per NCERT section, worked example, figure, table, in-text question and exercise, plus each
line of the CBSE syllabus. `where` lists the lesson or question ids that actually teach or solve it -
generate them from the content so the map cannot point at something missing. Status:
* `covered` - taught or solved on the page (not merely named in a heading).
* `expand` - present but thin, or missing (say what is missing in `note`).
* `verify` - present but not yet checked.
The build rejects ids that do not exist and `covered` with no `where`.
Make sure derivations, graph reading, written answers and applications are covered, not only numericals.

## 5. Corrections log (`corrections`)

Every deliberate change to earlier content or to a textbook figure: `item`, `change` (what and why),
`status` (Corrected, Clarified, Added, Relabelled). `preserve_check.py` lists every changed string; each
should match an entry here or be a pure restructuring.

## 6. Reference → Sources & checks

`sources` (official URLs with what each was used for), `verification.checks` (`what`, `how`, `status`:
done/partial/open, `result` with counts), `verification.notes` for anything else, and `corrections`.
Include at least one `open` item if any check was not done - an all-green table invites over-trust.
