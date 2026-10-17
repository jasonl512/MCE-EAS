"""Reproduce the 2024 Manhattan energy preparation using Python's standard library.
Usage: python clean_building_energy.py INPUT.csv [OUTPUT_DIRECTORY]
"""
import csv
import collections
import hashlib
import json
import math
import pathlib
import sys

source = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path('energy_cleaning_output')
out.mkdir(parents=True, exist_ok=True)
fields = {
    'Calendar Year': 'calendar_year', 'Property ID': 'property_id',
    'Property Name': 'property_name', 'Parent Property ID': 'parent_property_id',
    'NYC Borough, Block and Lot (BBL)': 'bbl',
    'NYC Building Identification Number (BIN)': 'bin',
    'Address 1': 'address', 'Postal Code': 'postal_code', 'Borough': 'borough',
    'Community Board': 'community_board',
    'Primary Property Type - Portfolio Manager-Calculated': 'property_type',
    'Number of Buildings': 'number_of_buildings',
    'Site EUI (kBtu/ft²)': 'site_eui_kbtu_ft2',
    'Weather Normalized Site EUI (kBtu/ft²)': 'weather_normalized_site_eui_kbtu_ft2',
    'National Median Site EUI (kBtu/ft²)': 'national_median_site_eui_kbtu_ft2',
    'ENERGY STAR Score': 'energy_star_score',
}
missing = {'', 'not available', 'n/a', 'na', 'null', 'none', 'not applicable: standalone property'}
numeric = {v for v in fields.values() if 'eui' in v or v in {'energy_star_score', 'number_of_buildings'}}
def number(value):
    try:
        n = float(value.replace(',', ''))
        return n if math.isfinite(n) else None
    except (ValueError, AttributeError):
        return None
def write(name, rows, columns):
    with (out / name).open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)
with source.open(encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    absent = set(fields) - set(reader.fieldnames)
    if absent:
        raise ValueError(f'Missing columns: {absent}')
    raw = list(reader)
selected = [(i + 2, x) for i, x in enumerate(raw)
            if x['Calendar Year'].strip() == '2024' and x['Borough'].strip().upper() == 'MANHATTAN']
ids = collections.Counter(x['Property ID'].strip() for _, x in selected)
clean, ready, issues = [], [], []
for row_number, x in selected:
    d = {}
    flags = []
    for original, renamed in fields.items():
        value = x[original].strip()
        if value.lower() in missing:
            value = ''
        if renamed in numeric and value:
            parsed = number(value)
            if parsed is None:
                flags.append(f'invalid_numeric:{renamed}')
                issues.append({'source_row': row_number, 'property_id': x['Property ID'], 'issue': f'invalid_numeric:{renamed}', 'original_value': x[original]})
            value = parsed if parsed is not None else ''
        d[renamed] = value
    d['source_row'] = row_number
    eui = d['site_eui_kbtu_ft2']
    if eui == '': flags.append('missing_site_eui')
    elif eui <= 0: flags.append('nonpositive_site_eui')
    if not d['property_id']: flags.append('missing_property_id')
    elif ids[d['property_id']] > 1: flags.append('duplicate_property_id')
    if d['community_board'] not in {str(i) for i in range(101, 113)}:
        flags.append('community_board_requires_review')
    score = d['energy_star_score']
    if score != '' and not 1 <= score <= 100: flags.append('energy_star_outside_1_100')
    if d['parent_property_id']: flags.append('parent_relationship_review_before_aggregation')
    d['quality_flags'] = ';'.join(flags)
    clean.append(d)
    blockers = {'missing_site_eui', 'nonpositive_site_eui', 'missing_property_id', 'duplicate_property_id', 'community_board_requires_review'}
    if not blockers.intersection(flags): ready.append(d.copy())
    for flag in flags:
        if not flag.startswith('invalid_numeric:'):
            issues.append({'source_row': row_number, 'property_id': d['property_id'], 'issue': flag, 'original_value': ''})
columns = list(fields.values()) + ['source_row', 'quality_flags']
write('Manhattan_Building_Energy_2024_Clean.csv', clean, columns)
write('Manhattan_Building_Energy_2024_EUI_Eligible.csv', ready, columns)
write('Manhattan_Building_Energy_2024_Issues.csv', issues, ['source_row', 'property_id', 'issue', 'original_value'])
stats = {'source_filename': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
         'source_rows': len(raw), 'selected_2024_manhattan_rows': len(clean),
         'eui_eligible_property_records': len(ready), 'issue_counts': dict(collections.Counter(x['issue'] for x in issues)),
         'year_counts': dict(collections.Counter(x['Calendar Year'] for x in raw))}
(out / 'cleaning_summary.json').write_text(json.dumps(stats, indent=2), encoding='utf-8')
print(json.dumps(stats, indent=2))
