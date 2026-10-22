# This week's implemented work

We built a first Green Score scoring prototype in Python. It normalizes four inputs to 0–100, combines them with explicit weights, and exports scores and ranks. Missing or invalid inputs block the total instead of becoming zero.

We tested it using clearly labeled synthetic data. The examples check score direction, reference limits, missing values, invalid values, mismatched years and changes in ranking when weights change. These are software tests, not measured neighborhood results or evidence of predictive accuracy.

We have not yet joined the real district datasets or implemented the project-selection optimizer. The next step is to finish the data alignment and review, agree on reference bounds, and connect the scoring function to real compatible inputs. Project costs and environmental effect estimates are separate inputs still being prepared.

## Simple speaking notes

This week, we built a first working version of the Green Score calculation. It puts the four factors on the same scale and combines them, starting with equal weights.

We used made-up test data to check the code. If a value is missing or invalid, the program leaves the total blank and tells us what needs checking.

We also tried different weights. In our test examples, changing the weights could change the order of the scores. We still need to prepare compatible real data before showing actual neighborhood scores.

## What to show

Run `py green_score.py`. Open `demo_results/scores.csv` and show A versus B under equal and air-priority weights. Then show that D has no overall score because PM2.5 is missing. Keep the synthetic label visible.

Run `py -m unittest -v` to show the calculation and validation checks. Software test success only means those defined checks passed; it is not a real-world accuracy percentage.
