import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path
from green_score import evaluate, normalize, rank_values, run, validate_config

BASE = Path(__file__).resolve().parent


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((BASE / "demo_config.json").read_text())
        self.row = dict(area_id="TEST", year="2024", geography="synthetic_district",
                        data_kind="synthetic", pm25="10", tree_cover="25", hvi="3", site_eui="110")

    def test_midpoints(self):
        result = evaluate(self.row, self.config)
        self.assertEqual(set(result["totals"].values()), {50})

    def test_directions_and_endpoints(self):
        for name, item in self.config["indicators"].items():
            with self.subTest(name=name):
                expected = (0, 100) if name == "tree_cover" else (100, 0)
                self.assertEqual((normalize(item["minimum"], item), normalize(item["maximum"], item)), expected)

    def test_missing_blocks_total_without_reweighting(self):
        for value in ("", "Not Available", "N/A"):
            self.row["pm25"] = value
            self.assertFalse(evaluate(self.row, self.config)["totals"])

    def test_bad_numbers(self):
        for value in ("NaN", "inf", "-inf", "bad"):
            self.row["site_eui"] = value
            self.assertIn("site_eui_invalid_number", evaluate(self.row, self.config)["errors"])

    def test_physical_ranges(self):
        for name, value in (("pm25", -1), ("tree_cover", 101), ("hvi", 0), ("hvi", 6), ("site_eui", 0), ("site_eui", -3)):
            row = dict(self.row, **{name: str(value)})
            self.assertFalse(evaluate(row, self.config)["totals"])

    def test_context_mismatch(self):
        for key, value in (("year", "2023"), ("geography", "zip"), ("data_kind", "real")):
            self.assertFalse(evaluate(dict(self.row, **{key: value}), self.config)["totals"])

    def test_clipping_is_visible(self):
        result = evaluate(dict(self.row, pm25="4"), self.config)
        self.assertEqual(result["scores"]["pm25"], 100)
        self.assertTrue(result["warnings"])

    def test_invalid_config(self):
        for kind in ("sum", "negative", "constant", "direction"):
            config = copy.deepcopy(self.config)
            if kind == "sum":
                config["scenarios"]["equal"]["pm25"] = 0.5
            elif kind == "negative":
                config["scenarios"]["equal"].update(pm25=-0.25, tree_cover=0.75)
            elif kind == "constant":
                config["indicators"]["pm25"]["maximum"] = 5
            else:
                config["indicators"]["pm25"]["direction"] = "higher"
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                validate_config(config)

    def test_tied_ranks(self):
        self.assertEqual(rank_values({"a": 80, "b": 80, "c": 50}), {"a": 1, "b": 1, "c": 3})

    def test_demo_and_sensitivity(self):
        with tempfile.TemporaryDirectory() as temp:
            summary = run(BASE / "synthetic_input.csv", self.config, temp)
            self.assertEqual((summary["input_rows"], summary["scored_rows"], summary["blocked_rows"]), (7, 4, 3))
            with (Path(temp) / "scores.csv").open(newline="") as handle:
                rows = {r["area_id"]: r for r in csv.DictReader(handle)}
            self.assertEqual(rows["DEMO_D_MISSING"]["equal_score"], "")
            self.assertGreater(float(rows["DEMO_B"]["equal_score"]), float(rows["DEMO_A"]["equal_score"]))
            self.assertGreater(float(rows["DEMO_A"]["air_priority_score"]), float(rows["DEMO_B"]["air_priority_score"]))

    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "duplicate.csv"
            with source.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(self.row))
                writer.writeheader()
                writer.writerows([self.row, self.row])
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                run(source, self.config, Path(temp) / "out")


if __name__ == "__main__":
    unittest.main(verbosity=2)
