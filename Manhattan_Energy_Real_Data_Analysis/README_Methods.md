# 2024 Manhattan reported building energy: exploratory analysis

## Scope

This package analyzes real property-report records from the team's prepared 2024 Manhattan LL84 extract. It does not calculate a Green Score, use synthetic observations, estimate intervention benefits, or implement planning optimization. The input is frozen at repository commit 51c434f931c2b0f0ba0aff11484038c28106a441. The original large raw download was not independently reprocessed in this analysis.

## Input and sources

1. Prepared input: https://github.com/jasonl512/MCE-EAS/blob/51c434f931c2b0f0ba0aff11484038c28106a441/energy_cleaning/Manhattan_Building_Energy_2024_Clean.csv
2. Dataset origin: https://data.cityofnewyork.us/d/5zyy-y8am (team download of October 15, 2026).
3. NYC DOB guidance: https://www.nyc.gov/site/buildings/codes/ll84-benchmarking-law.page
4. EPA EUI definition: https://www.energystar.gov/buildings/benchmark/understand-metrics/what-eui

NYC DOB recommends checking reported EUI below 5 or above 1,000 kBtu/ft²/year and documents semicolon-separated BBL/BIN entries. This supports a review screen, not an automatic conclusion that a value is wrong. Guidance checked November 3, 2026. EPA defines EUI as annual energy divided by floor area and explains why property types have different intensities.

## Inclusion and audit

Start with 11,937 Manhattan reporting-property records from 2024. Reproduce the initial eligibility checks: positive finite Site EUI, nonempty unique Property ID, and Community Board 101–112. This yields 10,537 records. Missing Site EUI: 1,360; nonpositive: 28; invalid district: 12. Unique initial exclusions total 1,400. Do not call 1,360 the total number excluded.

For a provisional conservative analysis, set aside initially eligible records if they have a parent ID, are referenced as a parent by another record in this extract, or share any valid 10-digit BBL or 7-digit BIN with another Property ID in the full extract. Identifiers are not repaired. This removes 2,709 initially eligible records from this analysis, leaving 7,828. Shared lots or buildings and parent links may be legitimate. Exclusion is a temporary choice pending record-level investigation and introduces selection bias.

Set aside a further 39 records outside the DOB EUI review range, leaving 7,789. Values equal to 5 or 1,000 are included. The old input remains unchanged. All review flags, reasons, and inclusion decisions are saved in results/record_audit.csv. Blank values remain blank. No imputation or zero substitution is used.

Within-type IQR flags use n >=20 and Q1−1.5×IQR / Q3+1.5×IQR with positive IQR. They are exploratory flags only. All 301 flagged screened records remain in primary summaries. Separate district medians without these flags provide a sensitivity comparison; this does not validate either version.

## Summaries

Each observation is a reporting property, which may contain multiple buildings. District medians are unweighted medians of Site EUI for included records. They are not district total energy, area-weighted intensity, adjusted efficiency ratings, or representative statistics for every district building. No floor-area field is retained in this prepared extract, so area-weighted intensity cannot be calculated here.

Property-type summaries and a multifamily-only district comparison help expose property-mix differences. They do not control for operating hours, occupancy, fuel mix, weather, property age, or every source of selection bias. The map should show measured EUI units and n rather than converting these medians to an unsupported green score.

## Map handoff

Use results/district_energy_for_map.csv. boro_cd is the existing energy Community Board code (101–112); district_number is 1–12 for Manhattan only. The boundary dataset, code field, vintage, and unmatched features must be verified by the map author. Do not join the energy data to arbitrary street segments or infer street-level energy from a district statistic. District statistics apply only to their stated reporting sample.

Suggested displayed fields: calendar_year, median_site_eui_kbtu_ft2_year, analysis_records, multifamily_median_site_eui, multifamily_records, analysis_share_of_extract. The last field is retention within the supplied extract, not coverage of all physical buildings.

## Reproduction and checks

Run python -m pip install -r requirements.txt then python analyze_energy.py. Source hash and record flow are in results/analysis_summary.json. Program assertions check the initial counts, subset accounting, absence of flagged parent/shared physical identifiers within the screened sample, district record reconciliation, and district medians independently using Python's statistics.median.

Chart 01 includes the whole screened EUI range on a logarithmic x-axis. Chart 02 shows the eight most common property types with at least 30 records; horizontal lines are Q1–Q3, not confidence intervals. Chart 03 compares district medians for mixed property types and multifamily-only records. All charts are black and white. The report includes a traceable CD 01 median calculation using actual records, not an arbitrary 0–100 conversion.

## Remaining work

Review excluded relationships and extreme values, assess coverage bias, confirm geographic joins and other indicator vintages, and justify any later normalization, weighting, and aggregation. The present summaries are suitable as honestly labeled preliminary results and inputs for a map prototype, not a validated four-indicator assessment.
