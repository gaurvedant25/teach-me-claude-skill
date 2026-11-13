# Official sources: where to look and what was true when this skill was written

Everything in a teach-me artifact must trace back to one of the official sources below.
Third-party sites (coaching blogs, "solutions" sites, YouTube) are allowed only to *find* things,
never as the authority for a fact, an answer or a PYQ attribution.

## Contents
1. Source hierarchy (which source wins)
2. CBSE academic portal: syllabus + sample papers
3. CBSE main site: past board papers + marking schemes
4. NCERT: textbooks, answers, exemplar
5. State of play, checked 19 Oct 2026 (re-verify every run)
6. When a source cannot be reached

---

## 1. Source hierarchy

When two sources disagree, the higher one wins. Note the disagreement in `verification.notes`.

1. **CBSE curriculum PDF for the current session** - decides what is in / out of the board exam,
   unit weightage, and topics that are "assessed only formatively" (i.e. NOT in the board paper).
2. **CBSE sample question paper (SQP) + marking scheme for the current session** - decides the paper
   pattern (sections, marks per question, number of MCQs / A-R / case-based) and answer style.
3. **Current NCERT textbook reprint** (the PDF says e.g. "Reprint 2026-27" in the footer) - the
   authority for definitions, values, data (e.g. $K_f$ of water = 1.86 K kg mol$^{-1}$), reactions,
   and wording. Board marking schemes follow NCERT. If a "standard" value elsewhere differs from
   NCERT's, use NCERT's and say so.
4. **CBSE board question papers + official marking schemes (2019 onward)** - the only source for PYQs.
   The marking scheme gives the expected answer and the split of marks.
5. **NCERT exemplar** - extra practice. Many exemplar questions are on topics later removed;
   check every one against (1) before using it.
6. CBSE circulars (cbseacademic.nic.in/circulars.html) - for scheme changes (two board exams,
   competency-based share, etc.).

## 2. CBSE academic portal - https://cbseacademic.nic.in/

* The certificate on this host has been expired at times; `scripts/cbse_fetch.py` relaxes
  verification for the official hosts only. Browsers / WebFetch may refuse it - use the script.
* Curriculum page for a session ending in year Y: `curriculum_Y.html` (2026-27 -> `curriculum_2027.html`).
  Sections: "Secondary Curriculum: Part - 1 (Class IX)", "... (Class X)", "Secondary Curriculum: Part - 2 (XI-XII)".
  PDFs look like `web_material/CurriculumMain27/SecPart2/Chemistry_SecP2_2026-27.pdf`.
  Some subjects also have a "Reading Material" PDF (`..._RM.pdf`) - for 2026-27 Chemistry this holds
  the NCERT text of the formative-only topics. Also read the "Introduction" PDF for scheme rules.
* Sample papers: `SQP_CLASSXII_2026-27.html`, `SQP_CLASSX_2026-27.html`; PDFs like
  `web_material/SQP/ClassXII_2026_27/Chemistry-SQP.pdf` and `...-MS.pdf` (Hindi versions end `_hi`).
* The curriculum says the detailed question-paper design is notified **with the SQP**, so read the SQP's
  general instructions for the section structure.

## 3. CBSE main site - https://www.cbse.gov.in/cbsenew/

* Index pages: `question-paper.html` and `marking-scheme.html` (2022 onward, including
  `YYYY-COMPTT` compartment papers and, from 2026, `Second_Board_X` for the Class X second exam).
  Needs a browser User-Agent (plain fetchers get 403); the script sends one.
* Zips by year/class/subject, e.g. `question-paper/2026/XII/Chemistry.zip`,
  `marking-scheme/2026/XII/Chemistry.zip`. File-name casing varies by year (CHEMISTRY, Chemistry,
  `086_Science`, `Math_S`) - the script matches loosely.
* 2019 and 2020 are not linked from the index but are still served at
  `question-paper/2019/XII/Chemistry.zip` style URLs (the script probes them). There was no regular
  board exam in 2021. 2022 was split into Term 1 (MCQ) and Term 2 (subjective) - the 2022 files
  online are Term 2; label them `kind: "term2"`.
* Set codes: Chemistry XII is paper 56; sets are written 56/1/1, 56/2/3 ...; visually impaired
  papers are 56(B); compartment sets use letters (56/C/1, 56/S/2). Cite the code exactly as printed
  on the paper.
* Papers are bilingual (Hindi page, then English page). Some sets are scanned images with no text;
  `papers` lists them. Use the marking scheme of the same set, or render the page to PNG
  (`cbse_fetch.py render`) and read it.
* Marking schemes are marked "Strictly confidential... for internal use" in their header even though
  CBSE publishes them. Use them to check answers and mark splits; do not copy their text into the
  artifact - write the solution in your own words following the same value points.

## 4. NCERT - https://ncert.nic.in/

* Book codes come from the picker script on `textbook.php`; `cbse_fetch.py ncert --list` reads it.
  Pattern: class letter (i=IX, j=X, k=XI, l=XII) + language (e=English, h=Hindi, u=Urdu) + subject
  + part. Examples: `lech1` (Class XII Chemistry Part I), `lech2` (Part II), `jesc1` (Class X Science),
  `iemh1` (Class IX Ganita Manjari).
* Chapter PDF: `textbook/pdf/<code><NN>.pdf` where NN is the chapter's position *within that book*
  (Part II of XII Chemistry starts again at 01 for Unit 6). Answers: `<code>an.pdf`.
  Prelims with the contents page: `<code>ps.pdf`.
* The first request to ncert.nic.in sometimes fails; the script retries.
* Exemplar problems: https://ncert.nic.in/exemplar-problems.php (check every question against the
  current syllabus; exemplar books predate the 2023 rationalisation).

## 5. State of play, checked 19 Oct 2026 - re-verify every run

These facts were verified from the official PDFs on 19 Oct 2026. Re-check them each time; if a
newer session's documents exist, they win.

* **Session 2026-27** (board exams Feb-Mar 2027). CBSE circular Acad-14/2026 (1 Apr 2026) released
  the curriculum: XI-XII on 1 Apr 2026, IX-X on 2 Apr 2026.
* **Class IX** moved to the NCF-SE 2023 scheme in 2026-27 with **new NCERT books** (e.g. Ganita
  Manjari Parts I-II for maths, Exploration for science, Kaveri for English) and Mathematics/Science
  offered at Standard and **Advanced** levels. There are no board PYQs for these new books - use
  CBSE/NCERT sample material and say so.
* **Classes X and XI** keep the existing (2023-rationalised) NCERT books in 2026-27; new books arrive
  from 2027-28 (NCERT advisory F.No.Secy/1-1/2026, 17 Mar 2026,
  https://ncert.nic.in/pdf/announcement/notices/Advisory_ncertbooks.pdf). The advisory does not mention
  **Class XII**; the CBSE 2026-27 curriculum still prescribes the existing XII books and their chapter
  PDFs are stamped "Reprint 2026-27". Re-check this every run - a new book changes the chapter list.
* **Class X has two board exams** since 2026: a compulsory first exam in February and an optional
  second (improvement) exam in May, only for subjects with more than 50% external assessment
  (2026 dates per news reports: from 17 Feb, and 15-21 May; second-exam results declared 18 Jul 2026).
  The 2026 second-exam papers are on the CBSE site under `question-paper/2026-COMPTT/Second_Board_X/`.
* **Class XII Chemistry 2026-27** (example of what to extract): theory 70 + practical 30; unit marks
  Solutions 7, Electrochemistry 9, Kinetics 7, d&f 7, Coordination 7, Haloalkanes 6, Alcohols 6,
  Aldehydes 8, Amines 6, Biomolecules 7. Formative-only (not in the board paper): Surface Chemistry,
  General Principles of Isolation of Elements, Polymers, Chemistry in Everyday Life. The SQP says
  "There is no change in the Question Paper Design and Assessment Pattern for Academic Session 2026-27":
  33 questions - A: 16 x 1 (MCQ incl. 4 A-R), B: 5 x 2, C: 7 x 3, D: 2 x 4 (case-based), E: 3 x 5;
  log tables and calculators not allowed. Typology: remembering/understanding 40%, applying 30%,
  analysing/evaluating/creating 30%; 33% internal choice.
* 9-point relative grading (A1 = top 1/8 of passed candidates ...) applies to Class XII board grades.

## 6. When a source cannot be reached

* Try the script first, then the built-in web tools, then a web search restricted to the official
  domain (`site:cbseacademic.nic.in`, `site:cbse.gov.in`, `site:ncert.nic.in`).
* If the current session's syllabus or SQP truly is not published yet, use the latest one that is,
  and put a visible note in `syllabus.note` and `verification.notes` ("2027-28 syllabus not yet
  released; based on 2026-27").
* If past papers cannot be fetched, do **not** fill the PYQ tab from memory or third-party lists.
  Leave it short, say why in the Sources tab, and tell the user. A wrong "CBSE 2023" label is worse
  than no label.
