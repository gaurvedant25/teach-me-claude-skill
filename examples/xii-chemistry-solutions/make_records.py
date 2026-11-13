"""Write content/01-records.json: coverage map, verification checks and corrections log.
Coverage 'where' ids are taken from the content itself (lessons that teach or use an item), so the
map cannot point at material that does not exist; build.py validates every id."""
import json, sys
from pathlib import Path

HERE = Path(__file__).parent
for up in [HERE] + list(HERE.parents):   # works in the project folder and inside the skill's examples/
    for cand in (up / "scripts" / "build.py", up / "teach-me" / "scripts" / "build.py"):
        if cand.exists():
            sys.path.insert(0, str(cand.parent)); break
    else:
        continue
    break
import build  # noqa: E402

base = HERE / "content"
d = build.load_content(base)
lessons = {l["id"]: l for t in d["topics"] for l in t["lessons"]}
qids = {q["id"] for q in build.all_questions(d)}

# question id -> lessons whose try/check blocks use it
used = {}
def walk(blocks, lid):
    for b in blocks:
        for q in b.get("questionIds") or []:
            used.setdefault(q, []).append(lid)
        walk(b.get("blocks") or [], lid)
for lid, l in lessons.items():
    walk(l["blocks"], lid)

def worked_in(src):
    out = []
    for lid, l in lessons.items():
        def w(bs):
            for b in bs:
                if b.get("type") == "worked" and b.get("source") == src:
                    out.append(lid)
                w(b.get("blocks") or [])
        w(l["blocks"])
    return out

cov = []
def add(kind, ref, where, status="covered", note=""):
    for x in where:
        assert x in lessons or x in qids, (ref, x)
    e = {"kind": kind, "ref": ref, "where": where, "status": status}
    if note:
        e["note"] = note
    cov.append(e)

S = "NCERT sections"
for ref, w in [("1.1 Types of solutions", ["t1-1"]), ("1.2 Expressing concentration (i)-(iv) percentages, ppm", ["t2-1"]),
               ("1.2 (v) Mole fraction", ["t2-2"]), ("1.2 (vi) Molarity", ["t2-3"]), ("1.2 (vii) Molality; temperature dependence", ["t2-4"]),
               ("1.2 Converting between units", ["t2-5"]), ("1.3.1 Solubility of a solid in a liquid", ["t3-1"]),
               ("1.3.2 Solubility of a gas in a liquid; Henry's law", ["t3-2"]), ("1.3.2 Effect of temperature; applications of Henry's law", ["t3-3"]),
               ("1.4.1 Vapour pressure of solutions of liquids in liquids", ["t4-1", "t4-2"]), ("1.4.2 Raoult's law as a special case of Henry's law", ["t4-3"]),
               ("1.4.3 Vapour pressure of solutions of solids in liquids", ["t4-3"]), ("1.5.1 Ideal solutions", ["t5-1"]),
               ("1.5.2 Non-ideal solutions (deviations)", ["t5-2"]), ("1.5.2 Azeotropes", ["t5-3"]), ("1.6 Colligative properties", ["t6-1"]),
               ("1.6.1 Relative lowering of vapour pressure", ["t6-1", "t6-2"]), ("1.6.2 Elevation of boiling point", ["t7-1", "t7-3"]),
               ("1.6.3 Depression of freezing point", ["t7-2", "t7-3"]), ("1.6.4 Osmosis and osmotic pressure", ["t8-1"]),
               ("1.6.4 Isotonic, hypertonic, hypotonic solutions", ["t8-2"]), ("1.6.5 Reverse osmosis and water purification", ["t8-2"]),
               ("1.7 Abnormal molar masses; van't Hoff factor", ["t9-1", "t9-2"]), ("1.7 Degree of dissociation and association", ["t9-3"])]:
    add(S, ref, w)

for n in range(1, 14):
    w = worked_in(f"NCERT Example 1.{n}")
    add("NCERT worked examples", f"Example 1.{n}", w, "covered" if w else "expand",
        "" if w else "Not taught as a worked example on this page.")
for ref, w, note in [("Fig. 1.1 Effect of pressure on gas solubility", ["t3-2"], "Redrawn as a schematic."),
                     ("Fig. 1.2 Henry's law plot (HCl in cyclohexane)", ["t3-2"], ""),
                     ("Fig. 1.3 Vapour pressure vs mole fraction, ideal solution", ["t4-1"], "Plus the interactive vapour-pressure model."),
                     ("Fig. 1.4 Decrease of vapour pressure by a non-volatile solute", ["t4-3"], "Redrawn as a schematic."),
                     ("Fig. 1.5 p₁ against x₁ for a non-volatile solute", ["t4-3", "t4-q7"], "Described in words and tested in a question; not drawn."),
                     ("Fig. 1.6 Positive and negative deviations", ["t5-2"], ""),
                     ("Fig. 1.7 Elevation of boiling point", ["t7-1"], ""), ("Fig. 1.8 Depression of freezing point", ["t7-2"], ""),
                     ("Fig. 1.9 Osmosis (thistle funnel)", ["t8-1"], "Plus the interactive osmosis model."),
                     ("Fig. 1.10 Osmotic pressure stops osmosis", ["t8-1"], "Shown in the same figure as 1.9."),
                     ("Fig. 1.11 Reverse osmosis", ["t8-2"], "Redrawn as a schematic.")]:
    add("NCERT figures", ref, w, "covered", note)
for ref, w in [("Table 1.1 Types of solutions", ["t1-1"]), ("Table 1.2 Henry's law constants", ["t3-2"]),
               ("Table 1.3 Kb and Kf values", ["t7-3"]), ("Table 1.4 van't Hoff factors", ["t9-1"])]:
    add("NCERT tables", ref, w)

def qcov(kind, prefix, n, label):
    for k in range(1, n + 1):
        qid = f"{prefix}-1-{k}"
        if qid not in qids:
            add(kind, f"{label} 1.{k}", [], "expand", "Missing from this page.")
            continue
        add(kind, f"{label} 1.{k}", [qid] + sorted(set(used.get(qid, []))))
qcov("NCERT in-text questions", "nc-in", 12, "Intext")
qcov("NCERT exercises", "nc-ex", 41, "Exercise")

for ref, w in [("Types of solutions", ["t1-1"]), ("Expressing concentration (mass %, volume %, mass by volume %, ppm, mole fraction, molarity, molality)", ["t2-1", "t2-2", "t2-3", "t2-4", "t2-5"]),
               ("Solubility of solids and gases; Henry's law", ["t3-1", "t3-2", "t3-3"]), ("Vapour pressure of liquid solutions; Raoult's law", ["t4-1", "t4-2", "t4-3"]),
               ("Ideal and non-ideal solutions; azeotropes", ["t5-1", "t5-2", "t5-3"]), ("Colligative properties and determination of molar mass", ["t6-1", "t6-2", "t7-1", "t7-2", "t7-3", "t8-1", "t8-2"]),
               ("Abnormal molar masses; van't Hoff factor", ["t9-1", "t9-2", "t9-3"])]:
    add("CBSE 2026-27 syllabus lines", ref, w)
add("Other", "NCERT Exemplar problems", [], "expand", "Not included on this page; practice comes from NCERT, past papers and original questions.")

n_verify = sum(1 for q in build.all_questions(d) if q.get("verify"))
n_check = sum(1 for q in build.all_questions(d) if q.get("check"))
checks = [
    {"what": "Numerical answers recomputed", "how": "Every numerical question and worked example carries a Python expression built from its own data; the build fails if any stored answer differs by more than its tolerance.", "status": "done", "result": f"{n_verify} questions plus all worked examples recompute correctly."},
    {"what": "Answer-checker values", "how": "Each answer box's accepted value must agree with an independent recomputation (build-time check).", "status": "done", "result": f"{n_check} answer boxes agree."},
    {"what": "Past-paper MCQ and assertion-reason keys", "how": "scripts/ms_crosscheck.py located each key in the same set's marking scheme; the two it could not parse were read by hand.", "status": "done", "result": "52 of 52 keys match the official scheme."},
    {"what": "Past-paper numerical and written answers", "how": "Compared with the same set's marking scheme: 32 numbers found automatically; the rest read in the scheme text or, where equations were images, in rendered page images.", "status": "done", "result": "80 of 80 agree. Small rounding differences are noted on 8 questions."},
    {"what": "Past-paper provenance", "how": "Year, set, question number and marks for every item; each labelled restated or adapted.", "status": "done", "result": "127 restated, 5 adapted (case-study passages summarised)."},
    {"what": "Facts against the NCERT chapter (Reprint 2026-27)", "how": "Line-by-line check when the page was first built (19 Oct 2026); items changed in this review were re-checked against the NCERT text.", "status": "done", "result": "One wording issue found and explained (sucrose 373.52 K)."},
    {"what": "Syllabus scope (CBSE 2026-27)", "how": "Unit content compared with the 2026-27 curriculum PDF.", "status": "done", "result": "Nothing in this unit is excluded this session."},
    {"what": "Maths rendering", "how": "Every TeX string test-rendered with the same KaTeX build the page uses.", "status": "done", "result": "0 failures."},
    {"what": "Nothing lost in the upgrade", "how": "scripts/preserve_check.py compared the previous version with this one.", "status": "done", "result": "0 items removed; 255 original questions and 67 flashcards kept with the same ids; reworded lesson text was restructured into the new worked-example format."},
    {"what": "Independent second review", "how": "A separate reviewer re-reading the content against NCERT and the schemes.", "status": "open", "result": "Not done. Treat any remaining slip as possible and report it."},
]
corrections = [
    {"item": "Sucrose boiling point (lesson 7.1)", "change": "NCERT's 373.52 K for 1 mol sucrose in 1 kg water equals 373 + 0.52; with 373.15 K the equation gives 373.67 K. Added an explanation, the dilute-solution caveat, and the 2024 compartment scheme that accepts both 373 and 373.15 K. Flashcard fc-048 now carries the same note.", "status": "Clarified"},
    {"item": "'Every step carries half a mark' and 'missing units always cost half a mark'", "change": "Replaced with question-specific evidence: named schemes that state the unit deduction; mark splits shown per question; practice splits labelled as suggestions.", "status": "Corrected"},
    {"item": "NCERT Example 1.9 (antifreeze)", "change": "Kept precision to the end: 2.25 K and 270.90 K. NCERT's 2.2 K / 270.95 K come from rounding the molality early; both are explained.", "status": "Corrected"},
    {"item": "Freezing-point rankings (py09, py20, py34 and lesson 9.2)", "change": "Taught as i × molality; the assumption that molarity ≈ molality for dilute aqueous solutions is now stated, and equal-mass-% comparisons use i/M.", "status": "Clarified"},
    {"item": "Formula labels", "change": "Every formula is labelled exact, definition, experimental law, ideal or dilute-solution approximation, with conditions.", "status": "Added"},
    {"item": "Notation M", "change": "Molarity no longer shares the symbol M with molar mass in lesson formulas; a notation note explains both uses.", "status": "Clarified"},
    {"item": "py54 (KCl vs methyl alcohol)", "change": "Added the marking scheme's own reason (methanol disrupts water-water hydrogen bonding).", "status": "Added"},
    {"item": "Rounding differences with marking schemes", "change": "py91, py93, py95, py97, py100, py105, py113 and py86 now note the scheme's printed value; both are accepted by the answer checker.", "status": "Clarified"},
    {"item": "Verification claim", "change": "The general statement that every past-paper answer was compared has been replaced by the counted record above.", "status": "Corrected"},
    {"item": "Case-study passages", "change": "Five case studies whose passages are summarised are labelled 'adapted' instead of being presented as original text.", "status": "Relabelled"},
    {"item": "Missing figures", "change": "Schematics added for NCERT Figs 1.1, 1.4 and 1.11.", "status": "Added"},
]
out = {"coverage": cov, "verification": {"checks": checks}, "corrections": corrections}
(base / "01-records.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
from collections import Counter
print(len(cov), Counter(c["status"] for c in cov))
