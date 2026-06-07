import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Focused WoSIS comparison: the SYLHET SOIL CLASS only (acidic, clay-rich), depth-weighted 0-30 cm.
Class defined by Sylhet's PREDICTOR envelope (pH < 6, clay 30-75%) -- NOT by SOC (avoid
conditioning on the response). Within that class: which properties govern SOC? Does clay?
And where do the 9 Sylhet sites sit? Uses saved REVISION/wosis_topsoil_0_30.parquet.
Output: REVISION/sylhet_class_results.md
"""
import pandas as pd, numpy as np
from scipy import stats
# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
agg=pd.read_parquet(f"{DERIVED}/wosis_topsoil_0_30.parquet")

# Sylhet 2025 envelope: pH 4.0-5.86, clay 31.7-72.2
def syl_class(d, tropical=False, asia=False):
    m=(d.ph<6.0)&(d.clay.between(30,75))
    if tropical: m&=d.lat.abs()<35
    if asia: m&=d.lon.between(60,110)&d.lat.between(5,35)
    return d[m].dropna(subset=["soc","clay"])

def corrs(d,label):
    out=[f"\n### {label} (n={len(d)})"]
    for c in ["clay","sand","ph","bd","cec","n_total"]:
        dd=d.dropna(subset=[c,"soc"])
        if len(dd)<30: out.append(f"- SOC vs {c:7s}: n={len(dd)} too few"); continue
        rho,p=stats.spearmanr(dd[c],dd.soc)
        out.append(f"- SOC vs {c:7s}: rho={rho:+.2f} (p={p:.0e}, n={len(dd)})")
    return out

res=["# Sylhet soil-class (acidic pH<6, clay 30-75%) — what governs SOC within the class?\n",
     "Depth-weighted 0-30 cm WoSIS topsoil. Class set by pH+clay (predictors), not SOC.\n",
     "Sylhet 2025 for reference: SOC vs TN rho=+0.68; vs clay +0.04(ns); vs pH -0.60; vs CEC -0.50; vs SBD -0.20."]
gC=syl_class(agg); tC=syl_class(agg,tropical=True); aC=syl_class(agg,asia=True)
res+=corrs(gC,"GLOBAL Sylhet-class")
res+=corrs(tC,"TROPICAL (|lat|<35) Sylhet-class")
res+=corrs(aC,"SOUTH/SE ASIA Sylhet-class")

# Sylhet placement within the class
syl=np.array([2.63,0.96,1.10,1.32,1.22,0.64,1.03,1.42,1.14])*10
res.append("\n## Sylhet placement within the soil class (topsoil SOC g/kg)")
for d,nm in [(gC,"global class"),(tC,"tropical class"),(aC,"Asian class")]:
    if len(d)>=20:
        res.append(f"- {nm}: median={d.soc.median():.1f}, Sylhet-mean({syl.mean():.1f}) percentile={100*(d.soc<syl.mean()).mean():.0f} (n={len(d)})")

# Within-class: is clay's weak effect robust to N? (partial clay-SOC | n_total)
d=gC.dropna(subset=["clay","soc","n_total"])
if len(d)>=30:
    R=d[["clay","soc","n_total"]].rank(); c=np.corrcoef(R.values,rowvar=False)
    rcs,rcn,rsn=c[0,1],c[0,2],c[1,2]; pr=(rcs-rcn*rsn)/np.sqrt((1-rcn**2)*(1-rsn**2))
    res.append(f"\n## Within global class: SOC-N rho={stats.spearmanr(d.n_total,d.soc)[0]:+.2f}; "
               f"clay-SOC|N partial={pr:+.2f} (n={len(d)})")
txt="\n".join(res); open(f"{RESULTS}/sylhet_class_results.md","w").write(txt); print(txt)
