# Manhattan building energy preparation

Source: NYC Building Energy and Water Data Disclosure, Local Law 84, 2023 to Present (calendar years 2022 onward). https://data.cityofnewyork.us/d/5zyy-y8am

This preparation uses the supplied October 15, 2026 download. The original CSV remains unchanged in the repository as Manhattan_Building_Energy_Raw.csv.

## Files and method

- `Manhattan_Building_Energy_2024_Clean.csv`: all 11,937 Manhattan property records for calendar year 2024, with 16 selected source fields plus source-row number and quality flags. Identifiers remain text. Missing-value labels become empty fields. Numeric fields are parsed without filling missing values.
- `Manhattan_Building_Energy_2024_EUI_Eligible.csv`: subset requiring a unique, nonempty Property ID, positive finite Site EUI and a Community Board code from 101 to 112. This is an input subset for further review, not a validated district-level score dataset.
- `Manhattan_Building_Energy_2024_Issues.csv`: review flags. A record can have more than one flag. Source row numbers include the header as row 1.
- `cleaning_summary.json`: counts and original-file SHA-256 checksum.
- `clean_building_energy.py`: reproducible processing script using Python's standard library.

Run: `python clean_building_energy.py Manhattan_Building_Energy_Raw.csv output`

## Decisions and limitations

2024 is the latest calendar year in this supplied extract. Using one year avoids mixing annual observations of the same property. It does not mean the other project indicators are already aligned to 2024.

Site EUI measures annual energy use per unit floor area, in kBtu/ft². It is not total energy use or a complete measure of efficiency: property use types and operating conditions matter. Property types and national median reference EUI are retained for later comparison design. No normalized energy score or Green Score is calculated here.

The property ID is a reporting-property identifier, not necessarily an individual building. Parent-child/campus relationships may overlap. Do not sum or average these records into district totals without resolving those relationships and choosing an appropriate aggregation method. Positive extreme EUI values are retained, not silently trimmed or declared valid; outlier review is still needed. Community Board codes outside 101–112 are retained in the full clean file and excluded from the EUI subset pending review.

The four indicators still require compatible geographic boundaries and an explicit policy for differing years before they can be joined. This package does not implement the optimizer, cost estimates or environmental impact predictions.
