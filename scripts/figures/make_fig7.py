import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Figure 7 (REVISED v2) — DRY-SEASON (Feb-Apr), water-fraction-controlled environmental trends,
1988-2025. Panels: (a) NDVI greening  (b) LST warming  (c) NDWI mirrors NDVI (not hydrological).
Replaces annual-mean indices (which were confounded by seasonal water fraction; NDVI~NDWI r=-0.89).
Data: REVISION/dryseason_indices_combined.csv. Output: REVISION/Fig7_EnvIndices.png
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import warnings; warnings.filterwarnings("ignore")

# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
d=pd.read_csv(f"{DERIVED}/dryseason_indices_combined.csv").sort_values("year")
yr=d.year.values
panels=[("ndvi","NDVI (dry season)","Vegetation greenness / productivity","#009E73","(a)","frac"),
        ("lst_C","LST (°C)","Land surface temperature","#CC79A7","(b)","temp"),
        ("ndwi","NDWI (dry season)","Water index = inverse of greenness","#0072B2","(c)","frac")]
fig=plt.figure(figsize=(15,4.6),dpi=300); fig.patch.set_facecolor("white")
ax=[fig.add_subplot(1,3,i+1) for i in range(3)]
for a,(col,short,long,color,pl,kind) in zip(ax,panels):
    x=yr.astype(float); y=d[col].values.astype(float)
    a.scatter(x,y,s=24,color=color,alpha=0.78,edgecolors="white",linewidths=0.4,zorder=3)
    a.plot(x,y,color=color,lw=1.0,alpha=0.5,zorder=2)
    sl,ic,r,p,se=stats.linregress(x,y); a.plot(x,sl*x+ic,"k--",lw=1.9,zorder=4)
    a.fill_between(x,y,sl*x+ic,color=color,alpha=0.10,zorder=1)
    pstr="p < 0.001" if p<0.001 else f"p = {p:.3f}"
    if kind=="temp": msg=f"+{sl*10:.2f} °C/decade  |  {pstr}"; ann="#CC3333"
    else:
        arrow="▲" if sl>0 else "▼"; msg=f"{arrow} {sl*10:+.3f}/decade  |  {pstr}"
        ann="#117733" if sl>0 else "#0072B2"
    a.text(0.96,0.06,msg,transform=a.transAxes,fontsize=10.5,fontweight="bold",ha="right",va="bottom",
           color=ann,bbox=dict(boxstyle="round,pad=0.3",fc="white",ec=ann,lw=0.8,alpha=0.92))
    a.set_xlabel("Year",fontsize=11.5,fontweight="bold"); a.set_ylabel(short,fontsize=11.5,fontweight="bold")
    a.tick_params(labelsize=9.5); a.set_xlim(1987,2026); a.xaxis.set_major_locator(plt.MultipleLocator(10))
    a.yaxis.grid(True,ls=":",lw=0.5,color="#ccc",alpha=0.8,zorder=0); a.set_axisbelow(True)
    for s in ("top","right"): a.spines[s].set_visible(False)
    a.text(0.03,0.96,f"  {long}  ",transform=a.transAxes,fontsize=10,fontweight="bold",ha="left",va="top",
           color="white",bbox=dict(boxstyle="round,pad=0.3",fc=color,ec="none",alpha=0.92))
    a.text(-0.10,1.06,pl,transform=a.transAxes,fontsize=13,fontweight="bold",va="bottom")
ax[2].text(0.5,0.04,"corr with NDVI = -0.97\n(mirrors greenness, not water)",transform=ax[2].transAxes,
           ha="center",fontsize=8,style="italic",color="#444")
fig.suptitle("Dry-season (Feb–Apr) environmental trends, Sylhet haors (1988–2025); water fraction controlled (~1.3%)",
             fontsize=13,fontweight="bold",y=1.02)
plt.tight_layout()
plt.savefig(f"{RESULTS}/Fig7_EnvIndices.png",dpi=300,bbox_inches="tight",facecolor="white")
print("Saved Fig7")
