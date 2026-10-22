# Software test results

Executed on October 21, 2026 with `python3 -m unittest -v`.

Result: **11 tests passed**.

Checks: midpoint scores; score directions and endpoints; missing inputs; nonnumeric and nonfinite inputs; physical-range validation; year/geography/data-kind mismatches; visible reference-bound clipping; invalid weights/bounds/directions; tied ranks; expected demonstration counts and ranking reversal; duplicate area rejection.

The demonstration run processed seven synthetic rows: four received totals, and three were blocked. One scored edge-case row generated visible clipping warnings.

These tests verify specified software behavior. They do not validate real district scores, environmental effects, costs, model novelty or predictive accuracy.
