import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Fig 14 (v2) — converging multi-source hydrology. Top row: ERA5-Land (root-zone soil moisture,
precipitation, 2m temperature, 1985-2025). Bottom row: GLDAS-2.1 (root-zone soil moisture, ET,
2000-2025) and GRACE/GRACE-FO terrestrial water storage (2003-2016). Independent products agree
the basin is drying + warming. Output: Submission_JEM/Fig14_hydrology.png
"""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
import warnings; warnings.filterwarnings("ignore")
# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
era=pd.read_csv(f"{DERIVED}/hydrology_era5_1985_2025.csv").dropna()
con=pd.read_csv(f"{DERIVED}/converging_hydrology.csv")
def mk(x):
    x=np.asarray(x,float); n=len(x)
    s=sum(np.sign(x[j]-x[i]) for i in range(n-1) for j in range(i+1,n))
    var=n*(n-1)*(2*n+5)/18.0; z=(s-np.sign(s))/np.sqrt(var) if s else 0
    return 2*(1-stats.norm.cdf(abs(z))), np.median([(x[j]-x[i])/(j-i) for i in range(n-1) for j in range(i+1,n)])
panels=[(era,"sm_root","ERA5 root-zone soil moisture (m³ m⁻³)","#0072B2"),
        (era,"precip_mm","ERA5 precipitation (mm)","#56B4E9"),
        (era,"t2m_C","ERA5 air temperature (°C)","#CC79A7"),
        (con,"gldas_rootmoist","GLDAS root-zone soil moisture (kg m⁻²)","#0072B2"),
        (con,"gldas_et","GLDAS evapotranspiration (mm d⁻¹)","#E69F00"),
        (con,"grace_tws_cm","GRACE water storage anomaly (cm)","#999999")]
fig,ax=plt.subplots(2,3,figsize=(15,8),dpi=300); fig.patch.set_facecolor("white"); ax=ax.ravel()
for a,(df,c,lab,col) in zip(ax,panels):
    s=df.dropna(subset=[c]).sort_values("year"); yr=s.year.values; v=s[c].values
    if len(v)<4: a.axis("off"); continue
    p,sen=mk(v); sl,ic,r,pp,se=stats.linregress(yr,v)
    a.scatter(yr,v,s=20,color=col,alpha=0.8,edgecolors="white",linewidths=0.4,zorder=3)
    a.plot(yr,v,color=col,lw=1,alpha=0.5,zorder=2); a.plot(yr,sl*yr+ic,"k--",lw=1.6,zorder=4)
    pstr="p < 0.001" if p<0.001 else f"p = {p:.3f}"
    sig="#CC3333" if (sen<0 and p<0.05) else ("#117733" if (sen>0 and p<0.05) else "#888")
    a.text(0.96,0.06,f"{sen*10:+.3g}/dec | {pstr}",transform=a.transAxes,ha="right",va="bottom",
           fontsize=9.5,fontweight="bold",color=sig,bbox=dict(boxstyle="round,pad=0.3",fc="white",ec="#ccc",alpha=0.9))
    a.set_title(lab,fontsize=10,fontweight="bold"); a.set_xlabel("Year",fontsize=9.5,fontweight="bold")
    a.tick_params(labelsize=8.5); a.grid(True,ls=":",lw=0.4,alpha=0.7)
    for sp in ("top","right"): a.spines[sp].set_visible(False)
fig.text(0.5,0.965,"Converging multi-source evidence: the Sylhet basin is drying and warming",
         ha="center",fontsize=13,fontweight="bold")
fig.text(0.5,0.94,"Top: ERA5-Land reanalysis (1985–2025).  Bottom: GLDAS-2.1 land model (2000–2025) and GRACE/GRACE-FO (2003–2016).",
         ha="center",fontsize=9.5,color="#555")
plt.tight_layout(rect=[0,0,1,0.93])
plt.savefig(f"{RESULTS}/Fig14_hydrology.png",dpi=300,bbox_inches="tight",facecolor="white")
print("Saved Fig14 (converging).")
