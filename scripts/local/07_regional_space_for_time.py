import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
(A) Regional space-for-time: re-test temperature->SOC WITHIN climate analogs of Sylhet,
removing the global climate-zone confound (earlier MAT span -12..+30 C).
Sylhet ~ MAT 24-25 C, MAP ~2000-4000 mm, tropical monsoon. Restrict the WoSIS Sylhet soil class
(acidic pH<6, clay 30-75%) to warm/wet analogs and re-estimate.
Uses files already on disk (no GEE). Output: regional_sft_results.md
"""
import pandas as pd, numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings; warnings.filterwarnings("ignore")
# [path set in paths.py] R="/Volumes/SSD Rx/Research/SOC/REVISION"
agg=pd.read_parquet(f"{DERIVED}/wosis_topsoil_0_30.parquet")
clim=pd.read_csv(f"{DERIVED}/wosis_class_climate.csv")
lc=pd.read_csv(f"{DERIVED}/wosis_class_landcover.csv")
d=agg[(agg.ph<6)&(agg.clay.between(30,75))].merge(clim,on="profile_id",how="left").merge(lc[["profile_id","lc"]],on="profile_id",how="left")
d=d[(d.soc>0)].dropna(subset=["soc","clay","mat"]); d["logsoc"]=np.log(d.soc)

def partial(dd,x,y,ctrl):
    dd=dd.dropna(subset=[x,y]+ctrl)
    if len(dd)<40: return np.nan,len(dd)
    import numpy.linalg as la
    Rk=dd[[x,y]+ctrl].rank(); C=np.corrcoef(Rk.values,rowvar=False); P=la.pinv(C)
    return -P[0,1]/np.sqrt(P[0,0]*P[1,1]), len(dd)

def report(dd,label):
    out=[f"\n## {label} (n={len(dd)}; MAT {dd.mat.min():.1f}-{dd.mat.max():.1f} C, MAP {dd['map'].min():.0f}-{dd['map'].max():.0f} mm)"]
    r=stats.spearmanr(dd.mat,dd.soc)[0]
    pN,n1=partial(dd,"mat","soc",["n_total"])
    pNM,n2=partial(dd,"mat","soc",["n_total","map"])
    out.append(f"- SOC vs MAT: rho={r:+.2f}; | N partial={pN:+.2f}; | N,MAP partial={pNM:+.2f} (n={n2})")
    m=dd.dropna(subset=["logsoc","mat","n_total","map","clay"])
    if len(m)>=40:
        X=StandardScaler().fit_transform(m[["mat","n_total","map","clay"]]); y=(m.logsoc-m.logsoc.mean())/m.logsoc.std()
        b=LinearRegression().fit(X,y)
        out.append(f"- std reg logSOC~MAT,N,MAP,clay (n={len(m)}, R2={b.score(X,y):.2f}): "
                   f"bMAT={b.coef_[0]:+.2f}, bN={b.coef_[1]:+.2f}, bMAP={b.coef_[2]:+.2f}, bClay={b.coef_[3]:+.2f}")
    return out

res=["# Regional / climate-restricted space-for-time (temperature -> SOC)\n",
     "Tightening the MAT gradient toward Sylhet-like conditions removes the global climate-zone confound.\n",
     f"Sylhet reference: MAT ~24-25 C, MAP ~2000-4000 mm, tropical monsoon."]
res+=report(d,"Global class (reference)")
res+=report(d[(d.lat.abs()<23.5)],"Tropical (|lat|<23.5)")
res+=report(d[(d.mat.between(20,30))],"Warm band (MAT 20-30 C)")
res+=report(d[(d.mat.between(20,30))&(d['map']>1200)],"Warm & wet (MAT 20-30, MAP>1200 mm)")
res+=report(d[(d.lon.between(60,110))&(d.lat.between(5,35))],"Monsoon Asia (lon 60-110, lat 5-35)")
res+=report(d[(d.lon.between(60,110))&(d.lat.between(5,35))&(d.lc==40)],"Monsoon-Asia cultivated/paddy")
txt="\n".join(res); open(f"{RESULTS}/regional_sft_results.md","w").write(txt); print(txt)
