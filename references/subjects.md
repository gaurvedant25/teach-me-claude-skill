# Subject-specific guidance

Read the section for the chapter's subject. Always confirm the paper pattern from the current SQP;
the notes below describe what to emphasise, not the pattern itself.

## Contents
- Chemistry
- Physics
- Mathematics (incl. Class X Standard / Basic, Applied Maths)
- Biology
- Science (Class IX-X)
- Social Science (History, Geography, Political Science / Civics, Economics)
- English (and other language literature)
- Commerce: Accountancy, Business Studies, Economics (XI-XII)
- Computer Science / Informatics Practices
- Class IX (new NCF books, 2026-27)

## Chemistry
* Physical chemistry: every formula with units; numericals in board style with calculator-free numbers;
  include log tables values in the question when needed (e.g. "log 2 = 0.3010"). Watch significant
  figures and unit conversions (g -> kg of solvent, mL -> L, atm vs bar, $R$ = 0.083 L bar K$^{-1}$ mol$^{-1}$
  vs 0.0821 L atm K$^{-1}$ mol$^{-1}$ vs 8.314 J K$^{-1}$ mol$^{-1}$).
* Inorganic: trends with the reason (electronic configuration first), exceptions as flashcards,
  balanced equations with states where NCERT gives them.
* Organic: name reactions with full equations and conditions (`flow` blocks), mechanisms as steps
  (SN1/SN2, nucleophilic addition) with SVG where arrows matter, conversions (the board's favourite
  2-3 mark item: build a conversions bank), distinction tests (reagent -> observation table),
  IUPAC naming practice, order-of-reactivity / acidity / basicity questions with reasons.
* Use `$\ce{...}$` for every formula and equation.
* Physical chemistry chapters: follow `chemistry-guidance.md` (relationship labels, temperature and
  rounding traps, molarity vs molality, i x m comparisons, prerequisites).

## Physics
* Derivations are 3-5 mark staples: give each NCERT derivation as `steps` with a labelled SVG figure,
  stating assumptions. Ray diagrams and circuit diagrams to scale and labelled.
* Numericals: SI units, sign conventions (optics), vector directions. Graph-based questions
  (V-I, stopping potential vs frequency, etc.) with correctly shaped SVG graphs.
* Experiments listed in the syllabus: aim, principle, diagram, observation.
* The accuracy traps in `chemistry-guidance.md` (units, rounding, labelling approximations) apply here too.

## Mathematics
* Teaching = concept -> standard result -> method recipe ("how to recognise and attack this type")
  -> fully worked examples of every NCERT exercise type.
* Solutions: every line of working, the way the marking scheme awards step marks; final answer boxed.
* Class X: Standard and Basic papers differ - build for the one the student named (default Standard),
  and mark Basic-only / Standard-only questions. PYQs come from the matching paper.
* Applied Mathematics (XI-XII) is a different subject from Mathematics; do not mix sources.
* `verify` every computed answer, including definite integrals, probabilities, matrix results
  (write the arithmetic in Python).

## Biology
* Diagrams are marks: draw every NCERT diagram students must label (as SVG with leader lines) and
  ask labelling questions. Flowcharts for processes (`flow`).
* Exact terminology and spelling of scientific names; differences tables; examples NCERT names.
* Case-based questions from experiments / data tables (CBSE favours these).

## Science (Class IX-X)
* Treat the chapter by its discipline (chemistry / physics / biology rules above).
* Class X has two board exams (February main, optional May second exam) - PYQs from both are valid;
  label `kind: "second"` for the May paper.
* Activities from NCERT are examinable as "what would you observe / why" questions - include them.

## Social Science
* History: timeline (table), key people / terms, sources (`quote` blocks) with source-based questions,
  causes -> events -> consequences (`flow`), map items listed in the syllabus.
* Geography: map work (list every map item in the syllabus for this chapter; describe locations
  precisely; SVG sketch maps only if accurate - otherwise describe and link to official maps),
  data/graph interpretation, distribution and factors.
* Political Science / Civics and Economics: definitions, features, examples from India, case
  studies, data-based questions; economics numericals verified.
* Answers: point-wise, the number of points the marks demand (3 marks -> 3 developed points).

## English (and other language literature)
* Never reproduce the text of the lesson / poem beyond very short quotations. Teach through summary,
  themes, character sketches, literary devices (with the brief quote that shows each), and the
  author's message.
* Questions: extract-based (use a short, clearly cited extract of a few lines at most, or describe
  the extract's context), short and long answers with value points, and the textbook's
  "Think about it" questions. Writing / grammar sections belong to separate skills chapters - only
  include them if the requested chapter is one of those.

## Commerce
* Accountancy: formats (journal, ledger, P&L appropriation, balance sheet) as tables; every
  adjustment worked step by step; totals verified with `verify` (sum the columns in Python).
* Business Studies: features / importance / principles with examples; case-based questions
  ("identify the principle and quote the lines") are the core - build many.
* Economics (XI-XII): diagrams (demand-supply, cost curves, PPC) as accurate SVG; numericals verified.

## Computer Science / Informatics Practices
* Code in `` `code` `` or a `table` with one line per row; every output question must be checked by
  actually running the code (Python) before you state the output.

## Class IX in 2026-27
* New NCF-SE 2023 books (e.g. Ganita Manjari, Exploration) - the chapter names and content differ
  from older Class IX books, and many websites still show the old books. Use only the current
  NCERT PDFs.
* There is no board exam in Class IX and no PYQ archive for the new books: drop the Past papers tab
  (leave `pyqs` empty), and strengthen practice + NCERT sections instead. Say so on the Overview.
* Check whether the student is in the Standard or Advanced level for Maths/Science.
