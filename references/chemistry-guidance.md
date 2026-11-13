# Chemistry (and numerical science) guidance

Applies to Chemistry chapters, and to Physics where the same issues arise. Skip for theory subjects.
These are rules about *how to be accurate*, not facts to copy: check every value against the current
NCERT chapter and the question's own data.

## Label every relationship

Use `formula.status` and say the condition in `conditions`:
* `definition` - molarity, molality, mole fraction, van't Hoff factor as a ratio.
* `exact` - follows by bookkeeping (dilution $M_1V_1 = M_2V_2$, degree of dissociation from particle counts, Dalton's law for vapour composition).
* `ideal` - holds for ideal solutions/gases (Raoult's law, $\Delta_{mix}H = 0$).
* `dilute` - dilute-solution approximations ($\Delta T_b = K_bm$, $\Delta T_f = K_fm$, $\pi = CRT$, relative lowering ≈ $n_2/n_1$).
* `empirical` - experimental laws (Henry's law).
State idealised assumptions: whole-number $i$ assumes complete dissociation and independent ions.

## Common accuracy traps

* **Temperatures**: kelvin in every formula. Use the reference value the question or NCERT's worked
  examples use (water: 373.15 K / 273.15 K) and note when a textbook sentence rounds (e.g. NCERT's
  373.52 K for 1 m sucrose equals 373 + 0.52). Check how schemes treat it - some accept both.
* **Rounding**: keep full precision until the end; when NCERT or a scheme rounds early, show both values
  and say why they differ.
* **Molarity vs molality**: colligative $\Delta T$ formulas use molality, osmotic pressure uses molarity.
  M ≈ m only for dilute aqueous solutions - state that assumption whenever a question mixes them.
* **Comparisons**: rank by $i \times m$ (or $i \times C$ for $\pi$); for equal mass %, compare $i/M$.
* **Units of R**: 0.0821 L atm, 0.083 L bar, 8.314 J (= Pa m³) K⁻¹ mol⁻¹ - match the pressure unit;
  explain the choice the first time it arises.
* **Notation**: M (molarity unit) vs M (molar mass) vs m (molality) vs m (mass) - add a notation note.
* **Solvent vs solution**: molality and colligative formulas use the solvent's mass; mass % and
  density use the solution's.
* **Association**: molality uses the normal molar mass; do not use the dimer's molar mass and $i$ together.
* **Significant figures**: match the data; board schemes rarely penalise one extra figure but do
  penalise missing or wrong units on some questions (check the scheme).
* **Answer keys**: NCERT answer keys and schemes sometimes round differently or contain slips - recompute,
  accept both readings in `check.alts`, and explain in `notes`.

## Prerequisites usually needed

Moles and molar mass; counting atoms in formulas (brackets, hydrates); g↔kg, mL↔L, °C↔K; powers of
ten; rearranging $A = BC$; density as mass↔volume; solute/solvent/solution. See `lesson-template.md` §1.

## Diagrams

Generate graphs with a script so they are to scale (straight Raoult lines meet the axes at the stated
pressures; vapour-pressure curves for $\Delta T_b$ and $\Delta T_f$ in the right order). Schematics
(particles, apparatus) must say "schematic, not to scale".
