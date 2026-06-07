import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Mann-Kendall trends on ERA5-Land basin hydrology 1985-2025: does the basin actually dry?
Independent of optical NDWI. Output: REVISION/hydrology_results.md + REVISION/Fig14_hydrology.png
"""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
d=pd.read_csv(f"{DERIVED}/hydrology_era5_1985_2025.csv").dropna()

def mk(x):
    x=np.asarray(x,float); n=len(x)
    s=sum(np.sign(x[j]-x[i]) for i in range(n-1) for j in range(i+1,n))
    var=n*(n-1)*(2*n+5)/18.0; z=(s-np.sign(s))/np.sqrt(var) if s else 0.0
    p=2*(1-stats.norm.cdf(abs(z)))
    slopes=[(x[j]-x[i])/(j-i) for i in range(n-1) for j in range(i+1,n)]
    return z,p,np.median(slopes)

panels=[("sm_root","Root-zone soil moisture (0–100 cm, m³ m⁻³)","#0072B2"),
        ("precip_mm","Annual precipitation (mm)","#56B4E9"),
        ("t2m_C","2 m air temperature (°C)","#CC79A7"),
        ("pet_mm","Potential evaporation (mm)","#E69F00")]
out=["# Independent hydrology (ERA5-Land reanalysis, basin mean, 1985–2025)\n",
     "Tests the drying question without optical indices. Mann–Kendall + Sen's slope.\n"]
fig,ax=plt.subplots(2,2,figsize=(13,8),dpi=300); fig.patch.set_facecolor("white"); ax=ax.ravel()
for a,(c,lab,col) in zip(ax,panels):
    if c not in d: continue
    yr=d.year.values; v=d[c].values; z,p,sen=mk(v)
    sl,ic,r,pp,se=stats.linregress(yr,v)
    dec=sen*10; pstr="p < 0.001" if p<0.001 else f"p = {p:.3f}"
    sig = "significant" if p<0.05 else "no significant trend"
    out.append(f"- **{lab}**: MK {pstr} (Z={z:+.2f}); Sen {sen:+.4g}/yr ({dec:+.3g}/decade); "
               f"{v[0]:.3g} -> {v[-1]:.3g} [{sig}]")
    a.scatter(yr,v,s=22,color=col,alpha=0.8,edgecolors="white",linewidths=0.4,zorder=3)
    a.plot(yr,v,color=col,lw=1,alpha=0.5,zorder=2)
    a.plot(yr,sl*yr+ic,"k--",lw=1.7,zorder=4)
    a.text(0.96,0.06,f"{dec:+.3g}/dec | {pstr}",transform=a.transAxes,ha="right",va="bottom",
           fontsize=9.5,fontweight="bold",color=("#CC3333" if sen<0 else "#117733"),
           bbox=dict(boxstyle="round,pad=0.3",fc="white",ec="#999",alpha=0.9))
    a.set_title(lab,fontsize=10.5,fontweight="bold"); a.set_xlabel("Year",fontsize=10,fontweight="bold")
    a.tick_params(labelsize=9); a.grid(True,ls=":",lw=0.4,alpha=0.7)
    for s in ("top","right"): a.spines[s].set_visible(False)
fig.suptitle("Independent basin hydrology (ERA5-Land, 1985–2025): is the haor drying?",fontsize=13,fontweight="bold",y=1.0)
plt.tight_layout(); plt.savefig(f"{RESULTS}/Fig14_hydrology.png",dpi=300,bbox_inches="tight",facecolor="white")
txt="\n".join(out); open(f"{RESULTS}/hydrology_results.md","w").write(txt); print(txt); print("\nSaved Fig14.")
