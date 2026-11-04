"""Reproduce an exploratory analysis of the repository's 2024 Manhattan extract.
Run: python analyze_energy.py
Dependencies: pandas, numpy, matplotlib. No network calls; input file is bundled.
"""
from pathlib import Path
import base64, collections, hashlib, html, json, re, statistics
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
SRC = ROOT / 'input/Manhattan_Building_Energy_2024_Clean.csv'
COMMIT = '51c434f931c2b0f0ba0aff11484038c28106a441'
SOURCE_URL = f'https://github.com/jasonl512/MCE-EAS/blob/{COMMIT}/energy_cleaning/Manhattan_Building_Energy_2024_Clean.csv'
NYC = 'https://www.nyc.gov/site/buildings/codes/ll84-benchmarking-law.page'
EPA = 'https://www.energystar.gov/buildings/benchmark/understand-metrics/what-eui'
d = pd.read_csv(SRC, dtype=str, keep_default_na=False)
assert len(d) == 11937 and set(d.calendar_year) == {'2024'} and set(d.borough) == {'MANHATTAN'}
eui = pd.to_numeric(d.site_eui_kbtu_ft2, errors='coerce')
valid_eui = np.isfinite(eui) & eui.gt(0)
valid_cd = d.community_board.isin([str(n) for n in range(101,113)])
valid_id = d.property_id.ne('') & ~d.property_id.duplicated(keep=False)
initial = valid_eui & valid_cd & valid_id
assert int(initial.sum()) == 10537

# Parent links and shared physical identifiers are review signals, not proof of duplicates.
parents = set(d.loc[d.parent_property_id.ne(''), 'parent_property_id'])
has_parent = d.parent_property_id.ne('')
is_parent = d.property_id.isin(parents)
def identifier_tokens(s, digits):
    # Semicolon-separated identifiers are documented by NYC DOB.
    # Tokenize other separators as well; never invent or repair an identifier.
    return set(t for t in re.split(r'[^0-9]+', s) if len(t)==digits and set(t)!={'0'})
def shared_identifiers(column, digits):
    tokens = [identifier_tokens(v,digits) for v in d[column]]
    owners = collections.defaultdict(set)
    for pid,ts in zip(d.property_id,tokens):
        for t in ts: owners[t].add(pid)
    shared = {t for t,ids in owners.items() if len(ids)>1}
    flags = pd.Series([bool(ts & shared) for ts in tokens], index=d.index)
    return flags, shared
shared_bbl, bbls = shared_identifiers('bbl',10)
shared_bin, bins = shared_identifiers('bin',7)
relationship_review = has_parent | is_parent
overlap_review = relationship_review | shared_bbl | shared_bin
# DOB recommends investigating EUI below 5 or above 1000. This is a review
# screen, not a scoring range, universal physical bound, or proof of an error.
dob_review = valid_eui & (eui.lt(5) | eui.gt(1000))
screened = initial & ~overlap_review & ~dob_review
d['site_eui_numeric'] = eui
d['initial_eligible'] = initial
d['has_parent_link'] = has_parent
d['referenced_as_parent_in_extract'] = is_parent
d['shared_bbl_review'] = shared_bbl
d['shared_bin_review'] = shared_bin
d['dob_eui_review_below_5_above_1000'] = dob_review
d['analysis_included'] = screened

def reasons(i):
    x=[]
    if not valid_eui[i]: x.append('missing_nonfinite_or_nonpositive_site_eui')
    if not valid_cd[i]: x.append('community_board_outside_101_112')
    if not valid_id[i]: x.append('missing_or_duplicate_property_id')
    if has_parent[i]: x.append('parent_link_pending_review')
    if is_parent[i]: x.append('referenced_parent_pending_review')
    if shared_bbl[i]: x.append('shared_bbl_pending_review')
    if shared_bin[i]: x.append('shared_bin_pending_review')
    if dob_review[i]: x.append('dob_eui_range_pending_review')
    return ';'.join(x)
d['analysis_exclusion_reasons'] = [reasons(i) for i in d.index]
a=d.loc[screened].copy()
assert len(a)>0 and a.property_id.is_unique
assert a.parent_property_id.eq('').all() and a.site_eui_numeric.between(5,1000).all()
assert not a.property_id.isin(parents).any()
for col,digits in [('bbl',10),('bin',7)]:
    counts=collections.Counter(t for v in a[col] for t in identifier_tokens(v,digits))
    assert not counts or max(counts.values())==1

# Within-type Tukey fences only identify a queue for review. They do not remove
# records from the primary screened analysis or establish a scientific cutoff.
a['within_type_iqr_review'] = False
fences=[]
for typ,g in a.groupby('property_type'):
    if len(g)<20: continue
    q1,q3=g.site_eui_numeric.quantile([.25,.75]);iqr=q3-q1
    if iqr<=0: continue
    lo,hi=q1-1.5*iqr,q3+1.5*iqr
    f=g.site_eui_numeric.lt(lo)|g.site_eui_numeric.gt(hi)
    a.loc[g.index,'within_type_iqr_review']=f
    fences.append({'property_type':typ,'n':len(g),'q1':q1,'q3':q3,'lower_review_fence':lo,'upper_review_fence':hi,'flagged_for_review':int(f.sum())})
d['within_type_iqr_review']=False
d.loc[a.index,'within_type_iqr_review']=a.within_type_iqr_review

stages=[]
def stage(label,mask): stages.append({'stage':label,'records':int(mask.sum())})
stage('All 2024 Manhattan records',pd.Series(True,index=d.index))
stage('Initial positive EUI, district and ID checks',initial)
stage('After setting aside parent-linked and shared-ID records',initial & ~overlap_review)
stage('After setting aside DOB EUI review-range records',screened)
pd.DataFrame(stages).to_csv(OUT/'record_flow.csv',index=False)
def save(frame,name): frame.to_csv(OUT/name,index=False,encoding='utf-8-sig',float_format='%.6f')
save(d,'record_audit.csv')
save(a,'analysis_records.csv')
save(d.loc[~screened | d.within_type_iqr_review],'review_queue.csv')
save(pd.DataFrame(fences),'within_type_review_fences.csv')

types=a.groupby('property_type').site_eui_numeric.agg(n='size',median_site_eui='median',q1_site_eui=lambda s:s.quantile(.25),q3_site_eui=lambda s:s.quantile(.75),min_site_eui='min',max_site_eui='max').reset_index().sort_values('n',ascending=False)
save(types,'property_type_summary.csv')
districts=[]
for cd in map(str,range(101,113)):
    allg=d[d.community_board.eq(cd)];g=a[a.community_board.eq(cd)]
    mf=g[g.property_type.eq('Multifamily Housing')]
    reduced=g[~g.within_type_iqr_review]
    districts.append({'boro_cd':cd,'district_number':int(cd)-100,'calendar_year':2024,'all_extract_records':len(allg),'initial_eligible_records':int((initial & d.community_board.eq(cd)).sum()),'analysis_records':len(g),'analysis_share_of_extract':len(g)/len(allg) if len(allg) else np.nan,'median_site_eui_kbtu_ft2_year':g.site_eui_numeric.median(),'q1_site_eui':g.site_eui_numeric.quantile(.25),'q3_site_eui':g.site_eui_numeric.quantile(.75),'iqr_review_records':int(g.within_type_iqr_review.sum()),'sensitivity_n_without_iqr_flags':len(reduced),'sensitivity_median_without_iqr_flags':reduced.site_eui_numeric.median(),'multifamily_records':len(mf),'multifamily_median_site_eui':mf.site_eui_numeric.median(),'metric':'Unweighted median reported Site EUI; screened reporting properties','status':'Exploratory; not a Green Score or district efficiency rating'})
districts=pd.DataFrame(districts)
save(districts,'district_energy_for_map.csv')
bytype=a.groupby(['community_board','property_type']).site_eui_numeric.agg(n='size',median_site_eui='median').reset_index().rename(columns={'community_board':'boro_cd'})
save(bytype,'district_by_property_type.csv')

# Exact independent spot checks for numerical summaries and denominator accounting.
assert stages[0]['records']-stages[1]['records']==1400
assert len(d)==len(a)+int((~screened).sum())
assert districts.analysis_records.sum()==len(a)
assert districts.all_extract_records.sum()+int((~valid_cd).sum())==len(d)
for r in districts.to_dict('records'):
    v=[float(x) for x in a.loc[a.community_board.eq(r['boro_cd']),'site_eui_kbtu_ft2']]
    if v: assert abs(statistics.median(v)-r['median_site_eui_kbtu_ft2_year'])<1e-9

summary={'source_commit':COMMIT,'source_url':SOURCE_URL,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'source_rows':len(d),'missing_site_eui':int(eui.isna().sum()),'nonpositive_site_eui':int((np.isfinite(eui)&eui.le(0)).sum()),'invalid_district':int((~valid_cd).sum()),'initial_eligible_records':int(initial.sum()),'initial_excluded_unique_records':int((~initial).sum()),'has_parent_link_all_records':int(has_parent.sum()),'referenced_as_parent_all_records':int(is_parent.sum()),'initial_eligible_with_relationship_or_shared_identifier':int((initial & overlap_review).sum()),'additional_dob_eui_screen_excluded_after_overlap_screen':int((initial & ~overlap_review & dob_review).sum()),'screened_analysis_records':len(a),'within_type_iqr_review_retained_records':int(a.within_type_iqr_review.sum()),'screened_median_site_eui':float(a.site_eui_numeric.median()),'screened_eui_min':float(a.site_eui_numeric.min()),'screened_eui_max':float(a.site_eui_numeric.max()),'all_positive_eui_max':float(eui[valid_eui].max()),'record_flow':stages,'verification':'Eligibility counts and district medians checked independently; parent/shared-identifier exclusion is provisional, not confirmed deduplication.'}
(OUT/'analysis_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
def finish(fig,name):
    fig.text(.5,-.02,'Screened reporting properties only; preliminary energy results, not Green Scores. Source: NYC LL84, 2024.',ha='center',fontsize=10)
    fig.savefig(OUT/name,dpi=180,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(10,5))
ax.hist(a.site_eui_numeric,bins=np.geomspace(5,1000,36),color='white',edgecolor='black',linewidth=.8)
ax.set_xscale('log');ax.set_xticks([5,10,20,50,100,200,500,1000]);ax.set_xticklabels(['5','10','20','50','100','200','500','1,000'])
ax.axvline(a.site_eui_numeric.median(),color='black',linestyle='--',label=f'Median: {a.site_eui_numeric.median():.1f}')
ax.set(xlabel='Site EUI (kBtu/ft²/year), logarithmic horizontal axis',ylabel='Reporting-property records',title=f'2024 Manhattan: reported energy-use intensity (n = {len(a):,})')
ax.legend(frameon=False);fig.tight_layout();finish(fig,'01_energy_distribution.png')

top=types[types.n.ge(30)].head(8).sort_values('median_site_eui')
fig,ax=plt.subplots(figsize=(11,6))
ax.barh(top.property_type,top.median_site_eui,color='white',edgecolor='black')
for y,(_,r) in enumerate(top.iterrows()):
    ax.plot([r.q1_site_eui,r.q3_site_eui],[y,y],color='black',linewidth=1)
    ax.plot(r.median_site_eui,y,'ko',markersize=4)
    ax.text(max(r.median_site_eui,r.q3_site_eui)+2,y,f'{r.median_site_eui:.1f}; n={int(r.n):,}',va='center',fontsize=10)
ax.set_xlim(0,float(top.q3_site_eui.max())*1.6)
ax.set(xlabel='Site EUI (kBtu/ft²/year); line = middle 50% of records',title='Property types differ: eight most represented types with n ≥ 30')
fig.tight_layout();finish(fig,'02_property_type_comparison.png')

fig,axes=plt.subplots(1,2,figsize=(12,6),sharey=True)
y=np.arange(12); labels=[f'CD {n:02d}' for n in range(1,13)]
for ax,col,ncol,title in [(axes[0],'median_site_eui_kbtu_ft2_year','analysis_records','All property types (mixed composition)'),(axes[1],'multifamily_median_site_eui','multifamily_records','Multifamily Housing only')]:
    ax.barh(y,districts[col],color='white',edgecolor='black')
    for i,r in districts.iterrows():
        ax.text(r[col]+1,i,f'{r[col]:.1f} (n={r[ncol]})',va='center',fontsize=9)
    ax.set(xlabel='Median Site EUI (kBtu/ft²/year)',title=title)
    ax.set_xlim(0,float(districts[col].max())*1.6)
axes[0].set_yticks(y,labels);axes[0].invert_yaxis()
fig.suptitle('2024 Manhattan community districts: descriptive comparisons',fontsize=15)
fig.tight_layout();finish(fig,'03_district_comparison.png')

def table(frame):
    labels={'boro_cd':'District code','all_extract_records':'Extract records','analysis_records':'Included records','median_site_eui_kbtu_ft2_year':'Median Site EUI','multifamily_records':'Multifamily n','multifamily_median_site_eui':'Multifamily median','iqr_review_records':'IQR review n','sensitivity_n_without_iqr_flags':'Sensitivity n','sensitivity_median_without_iqr_flags':'Sensitivity median','source_row':'Original source row','property_id':'Property ID','property_type':'Property type','site_eui_numeric':'Site EUI'}
    return frame.rename(columns=labels).to_html(index=False,border=0,float_format=lambda x:f'{x:,.2f}',escape=True)
def img(name):return '<img src="data:image/png;base64,'+base64.b64encode((OUT/name).read_bytes()).decode()+'" alt="'+html.escape(name)+'">'
example_cd='101';g=a[a.community_board.eq(example_cd)].sort_values(['site_eui_numeric','property_id'])
mid=[len(g)//2] if len(g)%2 else [len(g)//2-1,len(g)//2]
example=g.iloc[mid][['property_id','source_row','property_type','site_eui_numeric']]
example_text=f'CD 01 contains {len(g)} included reporting-property records. Sort Site EUI from low to high. '+(f'The middle value (position {mid[0]+1}) is the median.' if len(mid)==1 else f'Average positions {mid[0]+1} and {mid[1]+1} to obtain the median.')+f' Result: {g.site_eui_numeric.median():.2f} kBtu/ft²/year. This is a measured-data summary, not a converted Green Score.'
save(example,'worked_median_example.csv')
topfacts=types.head(3)
facts=' '.join(f"{r.property_type}: median {r.median_site_eui:.1f}, n={int(r.n):,}." for r in topfacts.itertuples())
body=f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Manhattan energy: real-data analysis</title><style>
body{{font-family:Arial,sans-serif;color:#000;background:#fff;max-width:1100px;margin:36px auto;padding:0 24px;line-height:1.5}}h1{{font-size:30px}}h2{{font-size:23px;border-bottom:1px solid #000;padding-bottom:7px;margin-top:34px}}p,li{{font-size:16px}}table{{border-collapse:collapse;width:100%;font-size:13px;margin:16px 0}}th,td{{border:1px solid #000;padding:7px;text-align:left}}img{{width:100%;height:auto}}a{{color:#000}}code{{font-size:13px}}@media print{{body{{margin:0}}h2{{break-after:avoid}}img,table{{break-inside:avoid}}}}</style>
<h1>Manhattan building energy: real-data analysis</h1><p>Calendar year 2024 · NYC Local Law 84 reporting-property records · Preliminary descriptive results</p>
<p><strong>No synthetic inputs, normalized energy scores, or Green Scores are used in this analysis.</strong> The results describe a conservatively screened subset of the repository extract. They do not represent all Manhattan buildings or establish district efficiency rankings.</p>
<h2>1. What changed since the first cleaning pass?</h2>{table(pd.DataFrame(stages))}
<p>The initial 1,400 exclusions include 1,360 missing Site EUI values, 28 nonpositive values, and 12 invalid community-board codes. Flags may overlap in general; exclusions are counted once per record. Missing values stay missing.</p>
<p>For this preliminary analysis, we set aside records with parent links, records referenced as parents elsewhere in this extract, or physical BBL/BIN identifiers shared with another property ID. These are unresolved relationships, not confirmed errors or duplicates. This conservative screen reduces coverage and may systematically exclude campuses and complex properties.</p>
<p>We then set aside otherwise eligible records with Site EUI below 5 or above 1,000, following NYC DOB's advice to investigate those values. This is a data-review screen, not a Green Score conversion range. All excluded records and reasons are retained in record_audit.csv.</p>
<h2>2. What do the real values show?</h2><p>{html.escape(facts)} These differences describe reported energy use per floor area; they do not establish that one property type is more efficient.</p>
{img('01_energy_distribution.png')}{img('02_property_type_comparison.png')}
<p>The distribution plot includes all screened records on a logarithmic horizontal axis. Property-type lines show the interquartile range, not confidence intervals. The eight most represented types with at least 30 records are shown; the full table includes every type.</p>
<h2>3. District results for the map</h2>{img('03_district_comparison.png')}
<p>District values are unweighted medians of included reporting properties. They are not floor-area-weighted energy intensity, district total energy, or causal measures of neighborhood performance. The multifamily-only comparison reduces one source of property-mix differences, but does not adjust for age, occupancy, fuel, or operating hours.</p>
{table(districts[['boro_cd','all_extract_records','analysis_records','median_site_eui_kbtu_ft2_year','multifamily_records','multifamily_median_site_eui']])}
<p>Map join: use boro_cd strings 101–112 if the boundary layer uses borough-plus-district codes. If it uses 1–12 instead, use district_number after filtering the boundary layer to Manhattan. Validate one-to-one district matches and unmatched districts before displaying results. Boundary geometry has not been supplied or independently verified here.</p>
<h2>4. A reproducible calculation with real records</h2><p>{html.escape(example_text)}</p>{table(example)}
<p>Source-row numbers refer to the original download retained by the earlier cleaning script. This analysis starts from the committed prepared extract; it does not independently re-run the original large raw-file cleaning.</p>
<h2>5. Remaining reviews and sensitivity</h2><p>Within each property type with at least 20 included records and a positive interquartile range, values beyond Q1 − 1.5×IQR or Q3 + 1.5×IQR are flagged for review. {int(a.within_type_iqr_review.sum())} screened records receive this statistical flag and remain in the primary results. The threshold is an exploratory analyst choice, not a validated error test.</p>
{table(districts[['boro_cd','iqr_review_records','median_site_eui_kbtu_ft2_year','sensitivity_n_without_iqr_flags','sensitivity_median_without_iqr_flags']])}
<p>Sensitivity medians show the effect of additionally setting aside IQR-flagged values. Neither version proves which records are correct. Relationships undetectable from the retained identifiers, inaccurate self-reports, geographic miscoding, and differences between reporting properties remain possible. Do not call this a fully validated or completely deduplicated dataset.</p>
<h2>6. Sources and reproducibility</h2><ol><li><a href="{SOURCE_URL}">Repository input at fixed commit {COMMIT}</a>. SHA-256: <code>{summary['source_sha256']}</code>.</li><li><a href="https://data.cityofnewyork.us/d/5zyy-y8am">NYC Open Data LL84 dataset 5zyy-y8am</a>; source of the earlier October 15, 2026 extract.</li><li><a href="{EPA}">EPA ENERGY STAR: What is EUI?</a> Definition, units, and why property types differ.</li><li><a href="{NYC}">NYC DOB: LL84 Benchmarking</a>. Review advice for EUI below 5 or above 1,000; multi-property and semicolon-delimited identifier guidance. Guidance consulted November 3, 2026.</li></ol>
<p>Run <code>python -m pip install -r requirements.txt</code>, then <code>python analyze_energy.py</code> from this folder. All outputs regenerate from the bundled input. The program checks original eligibility counts, subset accounting, physical-identifier overlap screens, and district medians against independent calculations.</p></html>'''
(ROOT/'OPEN_ME_Real_Data_Report.html').write_text(body,encoding='utf-8')
print(json.dumps(summary,indent=2))
print(types.head(8).to_string(index=False))
print(districts[['boro_cd','analysis_records','median_site_eui_kbtu_ft2_year','multifamily_records','multifamily_median_site_eui']].to_string(index=False))
