import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

#!/usr/bin/env python3
"""Inventory every impossible / suspect value in the 1985 and 2025 soil data."""
import pandas as pd, numpy as np
# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
out=[]; w=lambda s="":out.append(str(s))

# Parse the tidy matrix from MainData.xlsx 'Format' sheet
fm=pd.read_excel(f"{FIELD}/MainData.xlsx",sheet_name="Format",header=None)
# header row 1 (0-indexed) has Present/Previous; row 0 has site names at even cols from col2
sites=["Ajmiriganj","Balaganj","Goaninghat","Hakaluki","Kanairghat","Phagu","Sarail","Sulla","Terchibari","Zakiganj","Kulaura","BRRI"]
site_pres_col={s:2+2*i for i,s in enumerate(sites)}   # Present col
site_prev_col={s:3+2*i for i,s in enumerate(sites)}   # Previous col
# variable rows: (label, depth, df_row)
rows=[("pH","Topsoil",2),("pH","Subsoil",3),("TN","Topsoil",4),("TN","Subsoil",5),
      ("Clay","Topsoil",6),("Clay","Subsoil",7),("SBD","Topsoil",8),("SBD","Subsoil",9),
      ("SOC%","Topsoil",10),("SOC%","Subsoil",11)]
recs=[]
for var,depth,r in rows:
    for s in sites:
        for period,col in [("2025",site_pres_col[s]),("1985",site_prev_col[s])]:
            v=fm.iloc[r,col]
            try: v=float(v)
            except: v=np.nan
            recs.append(dict(Var=var,Depth=depth,Site=s,Period=period,Value=v))
df=pd.DataFrame(recs)

def flag(row):
    v,var,depth=row.Value,row.Var,row.Depth
    if pd.isna(v): return ""
    if var=="pH":
        if v<=0: return "IMPOSSIBLE (pH<=0)"
        if v<3.5: return "suspect (pH<3.5)"
        if v>8.5: return "suspect (pH>8.5)"
    if var=="SBD":
        if v>2.65: return "IMPOSSIBLE (>quartz 2.65)"
        if v>2.0:  return "implausible (>2.0 g/cm3)"
        if v>1.85: return "high (>1.85)"
    if var=="SOC%":
        if v>8:  return "IMPOSSIBLE-for-mineral (>8%)"
        if v>5:  return "very suspect (>5%, peat-like)"
        if v>3:  return "suspect (>3%)"
    if var=="TN":
        if v>0.4: return "high (>0.4%)"
    if var=="Clay":
        if v<5 or v>95: return "suspect"
    return ""
df["Flag"]=df.apply(flag,axis=1)

w("# Data-quality flags — 1985 & 2025 soil values\n")
w("Source: data/MainData.xlsx 'Format' sheet (Present=2025, Previous=1985).")
w("Thresholds: pH valid 3.5-8.5 (0 impossible); SBD mineral soil <1.85 normal, >2.0 implausible, >2.65 impossible; "
  "SOC% topsoil mineral wetland typically 0.3-3%, >5% peat-like, >8% impossible; TN >0.4% high.\n")

study_sites=sites[:9]
w("## A. FLAGGED values (study's 9 sites)\n")
w("| Site | Variable | Depth | Period | Value | Flag |")
w("|---|---|---|---|---|---|")
fl=df[(df.Flag!="")&(df.Site.isin(study_sites))].sort_values(["Period","Site","Var"])
for _,r in fl.iterrows():
    w(f"| {r.Site} | {r.Var} | {r.Depth} | {r.Period} | {r.Value:g} | {r.Flag} |")

w("\n## B. Worst offenders by site (1985)\n")
bad=fl[fl.Period=="1985"]
for s in bad.Site.unique():
    items=bad[bad.Site==s]
    w(f"- **{s} (1985)**: "+"; ".join(f"{r.Var} {r.Depth}={r.Value:g} [{r.Flag}]" for _,r in items.iterrows()))

w("\n## C. Period comparison for the most affected sites (topsoil)\n")
w("| Site | var | 1985 | 2025 |")
w("|---|---|---|---|")
for s in ["Hakaluki","Sarail","Terchibari","Sulla","Phagu"]:
    for var in ["SOC%","SBD","pH","TN"]:
        v85=df[(df.Site==s)&(df.Var==var)&(df.Depth=="Topsoil")&(df.Period=="1985")].Value.values
        v25=df[(df.Site==s)&(df.Var==var)&(df.Depth=="Topsoil")&(df.Period=="2025")].Value.values
        w(f"| {s} | {var} | {v85[0] if len(v85) else '?':g} | {v25[0] if len(v25) else '?':g} |" if len(v85) and len(v25) else f"| {s} | {var} | ? | ? |")

# SOCT round-number check
w("\n## D. Other artifacts\n")
prev=pd.read_csv(f"{FIELD}/PreviousTopSoil.csv")
w("- Hakaluki 1985 SOCT = %.2f (recorded as round 200.00 in source); Stock = %.2f"%(
    prev[prev.Location=='Hakaluki'].SOCT.values[0], prev[prev.Location=='Hakaluki'].Stock.values[0]))
w("- 1985 SBD values (topsoil) by site: "+", ".join(
    f"{r.Location}={r.SBD:g}" for _,r in prev.iterrows()))

txt="\n".join(out)
open(f"{RESULTS}/data_quality_flags.md","w").write(txt)
print(txt)
