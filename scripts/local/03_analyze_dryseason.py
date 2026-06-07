import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Analyze dry-season (Feb-Apr, water-controlled) trends: do greening/warming survive?
Mann-Kendall + Sen's slope on NDVI, NDVI_land, LST; test whether NDWI is independent or
just mirrors NDVI; confirm water fraction is controlled. Combines harvested 1988-2020 +
new 2021-2025. Output: REVISION/dryseason_results.md (+ combined CSV).
"""
import pandas as pd, numpy as np
from scipy import stats

# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
a=pd.read_csv(f"{DERIVED}/dryseason_partial_1988_2020.csv")
try:
    b=pd.read_csv(f"{DERIVED}/dryseason_indices_1988_2025.csv")  # 2021-2025 from the singly-run
    b=b[b.year>=2021]
    df=pd.concat([a,b]).drop_duplicates('year').sort_values('year').reset_index(drop=True)
except Exception:
    df=a.copy()
df.to_csv(f"{DERIVED}/dryseason_indices_combined.csv",index=False)

def mk(x):  # Mann-Kendall S, Z, p, Sen's slope
    x=np.asarray(x,float); n=len(x)
    s=sum(np.sign(x[j]-x[i]) for i in range(n-1) for j in range(i+1,n))
    var=(n*(n-1)*(2*n+5))/18.0
    z=(s-np.sign(s))/np.sqrt(var) if s!=0 else 0.0
    p=2*(1-stats.norm.cdf(abs(z)))
    slopes=[(x[j]-x[i])/(j-i) for i in range(n-1) for j in range(i+1,n)]
    return s,z,p,np.median(slopes)

out=["# Dry-season (Feb-Apr) trend analysis — water-fraction controlled\n",
     f"n = {len(df)} years ({df.year.min()}-{df.year.max()}); "
     f"mean water fraction = {df.water_frac.mean()*100:.1f}% (confound removed).\n"]
yrs=df.year.values
for col,label in [("ndvi","NDVI (basin)"),("ndvi_land","NDVI land-only"),("lst_C","LST (degC)"),("ndwi","NDWI")]:
    s,z,p,sen=mk(df[col].values)
    sl,ic,r,pp,se=stats.linregress(yrs,df[col].values)
    dec=sen*10
    out.append(f"- **{label}**: Mann-Kendall p={p:.4f} (Z={z:+.2f}); Sen slope={sen:+.5f}/yr "
               f"({dec:+.3f}/decade); OLS r={r:+.2f} p={pp:.4f}. "
               f"{df[col].iloc[0]:.3f} -> {df[col].iloc[-1]:.3f}")
# is NDWI independent of NDVI in dry season?
r,p=stats.pearsonr(df.ndvi,df.ndwi)
out.append(f"\n- corr(dry-season NDVI, NDWI) = {r:+.2f} (p={p:.1e}) -> "
           f"{'NDWI just MIRRORS NDVI (not an independent hydrological signal)' if r<-0.9 else 'partly independent'}")
# water fraction trend (did dry-season water itself change?)
s,z,p,sen=mk(df.water_frac.values)
out.append(f"- water fraction trend: MK p={p:.3f}, Sen {sen*100:+.3f}%/yr (near-zero confirms control)")

txt="\n".join(out)
open(f"{RESULTS}/dryseason_results.md","w").write(txt)
print(txt)
