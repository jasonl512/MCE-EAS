# Green Score prototype — first working version

This is working scoring code with **synthetic test data**, not measured Manhattan Green Scores. It tests normalization, weighted scoring, input checks and sensitivity to weights. It does not choose improvement projects or estimate costs.

## Run on Windows

Install Python 3 if it is not already available. No extra packages are needed.
Open this folder in File Explorer, type `cmd` in the address bar and press Enter.

```text
py green_score.py
py -m unittest -v
```

If your Python command is `python` instead of `py`, use `python` in both commands. The first command writes `demo_results/scores.csv` and `demo_results/run_summary.json`. Open scores.csv in Excel or Google Sheets. The second runs the automated software tests.

## What the code does

1. Checks the input columns, unique area IDs, reporting year, geography label and synthetic/real label.
2. Converts four raw indicators to scores from 0 to 100, with higher always meaning better. Tree cover points upward. PM2.5, HVI and Site EUI point downward.
3. Uses equal weights of 0.25 for the first baseline. Additional demonstration scenarios give one factor weight 0.55 and each other factor 0.15.
4. Leaves the overall score and rank blank when any factor is missing or invalid. It does not fill missing values or redistribute their weights.
5. Exports scores, ranks, errors, warnings and the complete configuration used.

For a higher-is-better factor: `100 * (value - minimum) / (maximum - minimum)`.
For a lower-is-better factor: `100 * (maximum - value) / (maximum - minimum)`.
The total is the sum of the four normalized scores times their weights.

The reference minimum and maximum are fixed in the configuration. Valid inputs outside them are capped at 0 or 100 and get a visible warning. This is a software rule, not evidence that an extreme observation is correct. Invalid physical ranges are blocked before scoring. Equal minimum and maximum are rejected.

## Read the demonstration

Every input row is invented and labeled synthetic. A, B and C illustrate different indicator combinations. D demonstrates a missing value, E a nonpositive EUI, F tests reference-bound clipping, and G tests a year mismatch. F is an edge-case test, not an example of an actual district.

At the equal weights, B scores above A. Under the air-priority weights, A scores above B. This is a controlled software example showing that weights can change rankings; it is not an NYC finding. Ties receive the same rank; ranks only include rows with a total.

## Before using real data

- Use one agreed geographic unit and document indicator years and units. Matching labels in a CSV are necessary checks, not proof that boundaries or units actually match.
- Resolve energy property overlaps and unusual values. Decide how property-level data should represent a district. Do not paste the existing property-level eligible CSV directly into this district input.
- Account for property type when designing the energy indicator. Raw Site EUI is not a complete efficiency measure. No district aggregation method is implemented here.
- Replace the demonstration bounds with documented, justified reference bounds. These numbers are not NYC standards or calibrated limits. Keep bounds fixed across compared weight scenarios.
- The HVI input assumes a 1–5 scale. Treating these ordered categories as equally spaced is a provisional simplification requiring justification. HVI may overlap conceptually with other indicators; check for double counting before treating the composite as validated.
- Record which areas are excluded due to missing data and assess whether exclusions bias comparisons. No imputation method has been selected.
- Baseline scores do not establish the causal benefits of planting trees, retrofits or other projects. Cost and effect evidence must be supplied separately.

After those decisions, make your own config and CSV and run:

```text
py green_score.py --input aligned_real_input.csv --config real_config.json --output real_results
```

Both config and row labels must say `real` for actual data. Do not simply relabel the synthetic examples. A future mixed-year policy would require code changes; this version deliberately requires one year.

## Files and current scope

- `green_score.py`: scoring and CSV command line interface.
- `demo_config.json`: explicit demonstration bounds, units and weights.
- `synthetic_input.csv`: seven invented software-test cases.
- `test_green_score.py`: automated tests, including known expected scores and rank reversal.
- `demo_results/`: generated outputs and test log.
- `WEEKLY_PROGRESS.md`: truthful progress notes and short presentation wording.

Completed here: scoring code, synthetic demonstrations and software tests.
Still planned: validated real district data, evidence-based bounds/weights, project costs/effects, budget and target-score optimization, equity rules, interactions and diminishing returns, and the map interface.

Method background: the existing repository note `Green_Score_Method_Research.md` describes the earlier rationale for testing normalization and equal weights. This package makes no new scientific-novelty or environmental-accuracy claim.
