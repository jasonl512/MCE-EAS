"""MCE-EAS scoring prototype. Standard library only; no fitted/predicted effects."""
import argparse
import csv
import json
import math
from pathlib import Path

INDICATORS = ("pm25", "tree_cover", "hvi", "site_eui")
DIRECTIONS = {"pm25": "lower", "tree_cover": "higher", "hvi": "lower", "site_eui": "lower"}
MISSING = {"", "na", "n/a", "not available", "null", "none"}


def finite(value):
    try:
        result = float(value)
    except (ValueError, TypeError):
        raise ValueError("must be numeric") from None
    if not math.isfinite(result):
        raise ValueError("must be finite")
    return result


def validate_config(config):
    if config.get("data_kind") not in ("synthetic", "real"):
        raise ValueError("data_kind must be synthetic or real")
    for key in ("year", "geography", "bounds_note"):
        if not str(config.get(key, "")).strip():
            raise ValueError(f"Missing config: {key}")
    if not isinstance(config.get("scenarios"), dict) or not config["scenarios"]:
        raise ValueError("Provide at least one weight scenario")
    if set(config.get("indicators", {})) != set(INDICATORS):
        raise ValueError("Config must define exactly four indicators")
    for name in INDICATORS:
        item = config["indicators"][name]
        lo, hi = finite(item["minimum"]), finite(item["maximum"])
        if lo >= hi:
            raise ValueError(f"{name}: minimum must be below maximum")
        if item.get("direction") != DIRECTIONS[name] or not item.get("unit"):
            raise ValueError(f"{name}: invalid direction or missing unit")
    for scenario, weights in config["scenarios"].items():
        if not scenario or set(weights) != set(INDICATORS):
            raise ValueError("Each scenario must name all four weights")
        values = [finite(weights[n]) for n in INDICATORS]
        if min(values) < 0 or not math.isclose(sum(values), 1, abs_tol=1e-9, rel_tol=0):
            raise ValueError(f"{scenario}: nonnegative weights must sum to one")


def normalize(value, item):
    lo, hi = finite(item["minimum"]), finite(item["maximum"])
    position = (value - lo) / (hi - lo)
    if item["direction"] == "lower":
        position = 1 - position
    return 100 * min(1, max(0, position))


def evaluate(row, config):
    """Fail closed: any missing/invalid indicator or context blocks all totals."""
    errors, warnings, scores = [], [], {}
    for key in ("year", "geography", "data_kind"):
        if str(row.get(key, "")).strip() != str(config[key]):
            errors.append(f"{key}_mismatch")
    if not str(row.get("area_id", "")).strip():
        errors.append("missing_area_id")
    for name in INDICATORS:
        raw = str(row.get(name, "")).strip()
        if raw.lower() in MISSING:
            errors.append(f"{name}_missing")
            continue
        try:
            value = finite(raw)
        except ValueError:
            errors.append(f"{name}_invalid_number")
            continue
        if (name == "pm25" and value < 0 or
            name == "tree_cover" and not 0 <= value <= 100 or
            name == "hvi" and not 1 <= value <= 5 or
            name == "site_eui" and value <= 0):
            errors.append(f"{name}_invalid_range")
            continue
        item = config["indicators"][name]
        if not finite(item["minimum"]) <= value <= finite(item["maximum"]):
            warnings.append(f"{name}_outside_reference_bounds_clipped")
        scores[name] = normalize(value, item)
    totals = {}
    if not errors:
        totals = {label: sum(scores[n] * finite(w[n]) for n in INDICATORS)
                  for label, w in config["scenarios"].items()}
    return {"errors": errors, "warnings": warnings, "scores": scores, "totals": totals}


def rank_values(values):
    """Descending competition ranks; ties compared at exported 6-place precision."""
    rounded = {key: round(value, 6) for key, value in values.items()}
    return {key: 1 + sum(other > value for other in rounded.values())
            for key, value in rounded.items()}


def run(input_path, config, output_path):
    validate_config(config)
    with Path(input_path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"area_id", "year", "geography", "data_kind", *INDICATORS}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Input CSV is missing required columns")
        rows = list(reader)
    ids = [r["area_id"].strip() for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate area IDs: resolve overlaps before scoring")
    results = [(row, evaluate(row, config)) for row in rows]
    rankings = {label: rank_values({r["area_id"]: e["totals"][label]
                                  for r, e in results if e["totals"]})
                for label in config["scenarios"]}
    destination = Path(output_path)
    destination.mkdir(parents=True, exist_ok=True)
    fields = ["area_id", "year", "geography", "data_kind", "status", "issues", "warnings"]
    fields += [f"{n}_score" for n in INDICATORS]
    fields += [f"{label}_{suffix}" for label in config["scenarios"] for suffix in ("score", "rank")]
    with (destination / "scores.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row, result in results:
            out = {k: row[k] for k in ("area_id", "year", "geography", "data_kind")}
            out.update(status="incomplete_or_invalid" if result["errors"] else "scored",
                       issues=";".join(result["errors"]), warnings=";".join(result["warnings"]))
            out.update({f"{n}_score": round(v, 6) for n, v in result["scores"].items()})
            for label, value in result["totals"].items():
                out[f"{label}_score"] = round(value, 6)
                out[f"{label}_rank"] = rankings[label][row["area_id"]]
            writer.writerow(out)
    summary = {"data_kind": config["data_kind"], "input_rows": len(rows),
               "scored_rows": sum(bool(e["totals"]) for _, e in results),
               "blocked_rows": sum(bool(e["errors"]) for _, e in results),
               "warning_rows": sum(bool(e["warnings"]) for _, e in results),
               "bounds_note": config["bounds_note"],
               "limitations": "Prototype only; no optimizer, causal effects or accuracy validation. Rankings only cover scored rows.",
               "config_used": config}
    (destination / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    try:
        config = json.loads((args.config or base / "demo_config.json").read_text(encoding="utf-8"))
        summary = run(args.input or base / "synthetic_input.csv", config, args.output or base / "demo_results")
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print(f"{summary['data_kind'].upper()} data: {summary['scored_rows']} scored; {summary['blocked_rows']} blocked. See scores.csv and run_summary.json.")


if __name__ == "__main__":
    main()
