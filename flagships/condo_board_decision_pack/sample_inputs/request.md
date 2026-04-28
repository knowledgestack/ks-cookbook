# Sample architectural request inputs

Use these with `make demo-condo-board`:

1. **Solar panels (common-element issue):**
   - `REQUEST="Unit 4B requests to install 12 solar panels on the roof terrace and a battery storage unit in the locker room"`
   - `UNIT=4B`

2. **Short-term rentals (rules + minutes precedent):**
   - `REQUEST="Unit 7A requests permission to list the unit on Airbnb for up to 90 days per year"`
   - `UNIT=7A`

3. **Exterior paint change (ACC guideline):**
   - `REQUEST="Unit 2F requests to repaint the balcony railings from white to matte black"`
   - `UNIT=2F`

All three hit different governing documents + precedents. The agent produces
a docx board-decision memo with the verdict, governing rules, precedents,
reserve-fund impact, conditions, rationale, and a formal motion.
