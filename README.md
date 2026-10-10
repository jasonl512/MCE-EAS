# MCE-EAS

**A Multi-Criteria Decision-Making Spatial Optimization Engine for Municipal Environmental Interventions**

Manhattan pilot | CSCI 49900-03 Capstone, Hunter College (CUNY), Fall 2026

Authors: Jovanny Guzman, Jason Lu

---

## Overview

New York City publishes environmental data across separate portals, but the data does not tell planners which projects to fund. MCE-EAS is a decision-support prototype that:

1. Harmonizes four district-level factors for the 12 Manhattan Community Districts: fine-particle air pollution (PM2.5), tree cover, heat vulnerability (HVI), and building energy performance.
2. Computes a transparent baseline **Green Score** (0-100) per district using min-max normalization and user-adjustable weights.
3. Uses a **0-1 integer linear program** (PuLP + CBC) to select a feasible portfolio of discrete environmental projects under a user-defined budget, with an optional **equity constraint** that reserves a minimum spending share for high-HVI districts.
4. Compares the optimized portfolio against greedy benefit-per-cost and equal-district baselines, and presents results in a WebGIS dashboard.

**Scope note:** project effects are estimates drawn from agency records or published studies. This prototype does not claim causal forecasts of real-world outcomes. If defensible impact estimates cannot be obtained, any synthetic catalog used for algorithm testing will be clearly labeled and kept separate from real-data findings.

## Research Questions

- **RQ1:** Can a reproducible spatial ETL pipeline align the four datasets to Manhattan Community Districts with complete and auditable outputs?
- **RQ2:** Under the same budget, how much improvement does the ILP portfolio achieve relative to greedy benefit-per-cost and equal-district baselines?
- **RQ3:** How do catalog size, budget level, and an equity constraint affect solution quality and solver latency?

## Project Status

> Keep this table up to date. It should always reflect what is actually in the repository.

| Component | Status | Notes |
|---|---|---|
| HVI data (Manhattan, NTA level) | Done (prototype) | `Manhattan_HVI_NTA_2020_Clean.csv` |
| HVI data (Manhattan, Community District level) | Done (prototype) | `Manhattan_HVI_CD_2020_Prototype.csv` |
| PM2.5 data (Manhattan) | In progress | Raw filtered export + analysis workbook |
| Tree cover (2017 land cover raster) | Planned | Zonal summary per Community District |
| Building energy (Local Law 84) | Planned | Join by building identifiers, aggregate by district |
| Spatial ETL pipeline (GeoPandas) | Planned | Reproject, join, aggregate, quality report |
| Baseline Green Score module | Planned | Equations (1)-(3) in the proposal |
| Intervention catalog (cost, factor, impact, source) | Planned | Next milestone |
| ILP optimization module (PuLP/CBC) | Planned | Plus greedy and equal-district baselines |
| FastAPI backend | Planned | |
| WebGIS dashboard (React + Leaflet/Mapbox GL + Chart.js) | Planned | |
| Experiments and evaluation report | Planned | |

## Repository Contents

| File | Description |
|---|---|
| `Manhattan_HVI_NTA_2020_Clean.csv` | Cleaned Manhattan Heat Vulnerability Index values at the neighborhood (NTA) level |
| `Manhattan_HVI_CD_2020_Prototype.csv` | Prototype HVI aggregated to Manhattan Community Districts |
| `NYC EH Data Portal - Fine particles (PM 2.5) (filtered).csv` | Filtered PM2.5 export from the NYC Environment & Health Data Portal |
| `Manhattan_PM25_2025_Analysis.xlsx` | PM2.5 analysis workbook for Manhattan |

TODO: describe columns, units, years, and any cleaning steps for each file.

## Data Sources

| Factor | Source |
|---|---|
| PM2.5 | NYC Community Air Survey (NYC DOHMH) - https://www.nyc.gov/site/doh/data/data-publications/air-quality-nyc-community-air-survey.page |
| Heat vulnerability | Interactive Heat Vulnerability Index (NYC DOHMH) - https://a816-dohbesp.nyc.gov/IndicatorPublic/data-features/hvi/ |
| Tree cover | Land Cover Raster Data (2017), 6 in. resolution (NYC Open Data, `he6d-2qns`) |
| Building energy | NYC Building Energy and Water Data Disclosure for Local Law 84 (NYC Open Data, `5zyy-y8am`) |
| Boundaries | Community Districts (NYC Open Data, `5crt-au7u`) |

## Method Summary

**Normalization.** For district *j* and factor *i*, with raw value `a_ij` and baseline limits `L_i`, `U_i`:

- Benefit factors: `F+_ij = 100 (a_ij - L_i) / (U_i - L_i)`
- Risk factors (PM2.5, HVI): `F-_ij = 100 (U_i - a_ij) / (U_i - L_i)`
- Green Score: `G_j = sum_i w_i F_ij`, with `w_i >= 0` and `sum w_i = 1` (default 0.25 each)

**Optimization.** Each candidate project *k* has cost `c_k`, district `d(k)`, and estimated score improvement `DeltaF_ik`. Weighted benefit is `v_k = sum_i w_i DeltaF_ik`.

```
maximize    sum_k v_k x_k
subject to  sum_k c_k x_k <= B,   x_k in {0, 1}
(equity)    sum_{k: d(k) in H} c_k x_k >= eta * sum_k c_k x_k
```

`H` is the set of high-HVI districts (prototype policy threshold, not an official classification) and `eta` in [0, 1] is the minimum protected spending share.

**Known limitations (by design in the first model):** project benefits are assumed additive and independent (no overlap or diminishing returns); HVI is treated as a composite index that interventions do not change without supporting evidence; HVI partly reflects heat and green-space conditions, so factor correlations will be inspected for possible double counting; Joint Interest Areas such as Central Park are reported separately rather than assigned to a district.

## Planned Technology Stack

- **Backend:** Python, FastAPI, GeoPandas, Shapely, pyproj, PuLP with CBC
- **Storage:** CSV/GeoJSON (PostGIS if time permits)
- **Frontend:** React, Leaflet or Mapbox GL JS, Chart.js

## Reproducing the Prototype

TODO: fill in as the pipeline is implemented.

```bash
# Example (update when code exists)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # note: install PuLP with CBC support, e.g. pip install "pulp[cbc]"
```

## Evaluation Plan (summary)

- **RQ1:** valid-row retention, unmatched records, missing values, spatial-join correctness on a manually checked sample, ETL time.
- **RQ2:** ILP vs. greedy benefit-per-cost vs. equal-district heuristics at budgets of 10%, 25%, and 50% of total catalog cost; objective gain, budget utilization, project distribution; separate equity analysis (constrained vs. unconstrained ILP).
- **RQ3:** catalog sizes K = 50, 100, 250, 500, with and without the equity constraint; median and worst-case solve time, optimality status or gap, infeasible cases.

## Acknowledgments

Course: CSCI 49900-03 Advanced Applications - Capstone Major, Hunter College, Department of Computer Science. Instructor: Sourya Saha.
