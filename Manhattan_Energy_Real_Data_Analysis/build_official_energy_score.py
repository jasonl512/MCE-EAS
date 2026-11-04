"""Create a reproducible energy-score summary from real LL84 records.

Use the reported ENERGY STAR score when available. Missing scores remain blank.
Run after analyze_energy.py: python build_official_energy_score.py
"""
from pathlib import Path
import base64
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
INPUT = OUT / "analysis_records.csv"

def save(frame, name):
    frame.to_csv(OUT / name, index=False, encoding="utf-8-sig", float_format="%.6f")

def html_table(frame):
    return frame.to_html(index=False, border=0, escape=True,
                         float_format=lambda x: f"{x:,.2f}")

df = pd.read_csv(INPUT, dtype={"community_board": str, "property_id": str})
df["site_eui_numeric"] = pd.to_numeric(df["site_eui_numeric"], errors="coerce")
df["official_energy_star_score"] = pd.to_numeric(df["energy_star_score"], errors="coerce")
valid = df["official_energy_star_score"].between(1, 100, inclusive="both")
df.loc[~valid, "official_energy_star_score"] = np.nan
df["official_score_available"] = valid
df["energy_score_method"] = np.where(
    valid,
    "Reported ENERGY STAR 1-100 score from NYC LL84 extract",
    "No official score available; left blank",
)

save(df[["property_id", "community_board", "property_type", "site_eui_numeric",
         "weather_normalized_site_eui_kbtu_ft2", "national_median_site_eui_kbtu_ft2",
         "official_energy_star_score", "official_score_available", "energy_score_method"]],
     "official_energy_score_records.csv")

rows = []
for cd in map(str, range(101, 113)):
    g = df[df.community_board.eq(cd)]
    s = g[g.official_score_available]
    rows.append({
        "boro_cd": cd,
        "district_number": int(cd) - 100,
        "analysis_records": len(g),
        "official_score_records": len(s),
        "official_score_coverage_pct": 100 * len(s) / len(g) if len(g) else np.nan,
        "median_official_energy_star_score": s.official_energy_star_score.median(),
        "q1_official_energy_star_score": s.official_energy_star_score.quantile(.25),
        "q3_official_energy_star_score": s.official_energy_star_score.quantile(.75),
        "median_site_eui_kbtu_ft2_year_all_analysis_records": g.site_eui_numeric.median(),
        "map_metric": "Exploratory district median of available property-level ENERGY STAR scores",
        "status": "Real reported scores; not an official district rating or complete Green Score",
    })
districts = pd.DataFrame(rows)
save(districts, "district_official_energy_score_for_map.csv")

rows = []
for typ, g in df.groupby("property_type", dropna=False):
    s = g[g.official_score_available]
    rows.append({"property_type": typ, "analysis_records": len(g),
                 "official_score_records": len(s),
                 "official_score_coverage_pct": 100 * len(s) / len(g),
                 "median_official_energy_star_score": s.official_energy_star_score.median(),
                 "median_site_eui_kbtu_ft2_year": g.site_eui_numeric.median()})
types = pd.DataFrame(rows).sort_values("analysis_records", ascending=False)
save(types, "property_type_official_score_coverage.csv")

summary = {
    "analysis_records": int(len(df)),
    "official_energy_star_score_records": int(valid.sum()),
    "official_energy_star_score_missing_records": int((~valid).sum()),
    "official_energy_star_score_coverage_pct": float(100 * valid.mean()),
    "median_available_official_energy_star_score": float(df.loc[valid, "official_energy_star_score"].median()),
    "method": "Use reported ENERGY STAR 1-100 score when available; leave missing scores blank.",
    "district_summary": "Median of available property scores; exploratory, not an official district rating.",
    "not_used": "No all-building EUI min-max score, no percentile cutoff score, and no imputation."
}
(OUT / "official_energy_score_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "axes.facecolor": "white",
                     "savefig.facecolor": "white"})
y = np.arange(12)
labels = [f"CD {n:02d}" for n in districts.district_number]
fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
axes[0].barh(y, districts.median_official_energy_star_score, color="white", edgecolor="black")
for i, r in districts.iterrows():
    axes[0].text(r.median_official_energy_star_score + 1, i,
                 f"{r.median_official_energy_star_score:.1f}", va="center", fontsize=9)
axes[0].set(xlim=(0, 105), xlabel="Median available ENERGY STAR score",
            title="Property-level score summary")
axes[0].set_yticks(y, labels)
axes[0].invert_yaxis()
axes[1].barh(y, districts.official_score_coverage_pct, color="white", edgecolor="black")
for i, r in districts.iterrows():
    axes[1].text(r.official_score_coverage_pct + 1, i,
                 f"{r.official_score_coverage_pct:.0f}% (n={int(r.official_score_records)})",
                 va="center", fontsize=8)
axes[1].set(xlim=(0, 110), xlabel="Included records with an official score (%)",
            title="Coverage shown with every result")
fig.suptitle("2024 Manhattan: available official ENERGY STAR scores by community district", fontsize=14)
fig.text(.5, -.01, "Real LL84 records after the documented analysis screen. District medians are exploratory, not official district ratings.", ha="center", fontsize=9)
fig.tight_layout()
fig.savefig(OUT / "04_official_energy_score_by_district.png", dpi=180, bbox_inches="tight")
plt.close(fig)

image = base64.b64encode((OUT / "04_official_energy_score_by_district.png").read_bytes()).decode()
show_d = districts[["boro_cd", "analysis_records", "official_score_records",
                    "official_score_coverage_pct", "median_official_energy_star_score"]].rename(columns={
    "boro_cd": "District code", "analysis_records": "Included records",
    "official_score_records": "Records with official score",
    "official_score_coverage_pct": "Coverage (%)",
    "median_official_energy_star_score": "Median available official score"})
show_t = types.head(12).rename(columns={
    "property_type": "Property type", "analysis_records": "Included records",
    "official_score_records": "Records with official score",
    "official_score_coverage_pct": "Coverage (%)",
    "median_official_energy_star_score": "Median official score",
    "median_site_eui_kbtu_ft2_year": "Median Site EUI"})
report = f"""<!doctype html><html lang='en'><meta charset='utf-8'><title>Energy score method using real Manhattan data</title>
<style>body{{font-family:Arial,sans-serif;color:#000;background:#fff;max-width:1050px;margin:36px auto;padding:0 24px;line-height:1.5}}h1{{font-size:30px}}h2{{font-size:22px;border-bottom:1px solid #000;padding-bottom:6px;margin-top:32px}}p,li{{font-size:16px}}table{{border-collapse:collapse;width:100%;font-size:13px;margin:16px 0}}th,td{{border:1px solid #000;padding:7px;text-align:left}}img{{width:100%;height:auto}}a{{color:#000}}</style>
<h1>Energy score method using real Manhattan data</h1>
<p><strong>Recommended current method:</strong> use the property-level ENERGY STAR score reported in the NYC LL84 extract when available. Leave the score blank when unavailable.</p>
<h2>Why this replaces the proposed EUI min-max conversion</h2>
<p>Site EUI describes energy use per square foot, but offices, hotels, schools, and housing operate differently. One Manhattan-wide minimum and maximum would compare unlike properties. The ENERGY STAR score is already a 1-100 comparison for eligible properties and is designed to compare a property with similar buildings while accounting for relevant operating and climate characteristics.</p>
<p>The proposed 5th/95th percentile EUI conversion is not used as a final energy score. Percentiles can flag records for review, but do not by themselves justify an efficiency score.</p>
<h2>Real-data coverage and district summary</h2>
<p>{summary['official_energy_star_score_records']:,} of {summary['analysis_records']:,} included records have a valid reported ENERGY STAR score ({summary['official_energy_star_score_coverage_pct']:.1f}% coverage). The remaining {summary['official_energy_star_score_missing_records']:,} scores stay blank.</p>
<img src='data:image/png;base64,{image}' alt='Official ENERGY STAR scores and coverage by district'>
{html_table(show_d)}
<p>The map file reports the median available property-level score and coverage. This is an exploratory district summary, not an official district ENERGY STAR rating. Lower-coverage districts need more caution.</p>
<h2>Coverage by property type</h2>{html_table(show_t)}
<p>Some property types are not eligible for an ENERGY STAR score or lack required information. Missing values are shown instead of replaced with a homemade score.</p>
<h2>Files</h2><ul><li><code>results/district_official_energy_score_for_map.csv</code></li><li><code>results/official_energy_score_records.csv</code></li><li><code>results/property_type_official_score_coverage.csv</code></li><li><code>results/04_official_energy_score_by_district.png</code></li></ul>
<h2>Sources and limits</h2><ol><li><a href='https://www.energystar.gov/buildings/benchmark/understand-metrics/score-criteria'>EPA ENERGY STAR: score eligibility</a></li><li><a href='https://www.energystar.gov/buildings/benchmark/understand-metrics/compare-performance'>EPA ENERGY STAR: compare performance</a></li><li><a href='https://www.nyc.gov/site/buildings/codes/ll84-benchmarking-law.page'>NYC DOB: LL84 benchmarking</a></li></ol>
<p>This is the energy component only. It does not represent every Manhattan building or produce the complete four-factor Green Score.</p></html>"""
(ROOT / "OPEN_ME_Energy_Score_Method.html").write_text(report, encoding="utf-8")

print(json.dumps(summary, indent=2))
print(districts[["boro_cd", "official_score_records", "official_score_coverage_pct", "median_official_energy_star_score"]].to_string(index=False))
