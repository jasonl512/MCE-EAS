# Energy score method using real Manhattan data

## Current recommendation

Use the **reported ENERGY STAR 1-100 score** when it is available in the NYC
Local Law 84 extract. Leave the value blank when an official score is not
available.

This replaces one inverted min-max formula across every property. Hotels,
offices, schools, and housing operate differently, so one Site EUI range would
compare unlike properties. EPA's ENERGY STAR score is designed to compare
eligible properties with similar buildings and account for relevant operating
and climate characteristics.

## Reproduce the output

Run from this folder:

```text
python analyze_energy.py
python build_official_energy_score.py
```

The second command creates the district map table, record-level score table,
property-type coverage table, summary JSON, chart, and HTML explanation.

## Important limits

- The district value is the median of available property-level scores. It is
  exploratory, not an official district ENERGY STAR rating.
- Coverage is reported for every district. Missing scores remain blank.
- No 5th/95th percentile EUI conversion is presented as a validated score.
- This is the energy component only, not the complete Green Score.

## Sources

- https://www.energystar.gov/buildings/benchmark/understand-metrics/score-criteria
- https://www.energystar.gov/buildings/benchmark/understand-metrics/compare-performance
- https://www.nyc.gov/site/buildings/codes/ll84-benchmarking-law.page
