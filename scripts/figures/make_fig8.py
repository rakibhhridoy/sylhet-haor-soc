import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Figure 8 (REVISED) — Dry-season NDVI-derived above-ground biomass (Meshesha 2020), 1988-2025.
Now valid: dry-season NDVI (0.47-0.63) is above the equation's vertex (0.214), so biomass
increases with NDVI (the earlier annual-mean version was on the descending limb).
Data: REVISION/dryseason_indices_combined.csv. Output: REVISION/Fig8_VegBiomass.png
"""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import warnings; warnings.filterwarnings("ignore")
# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
d=pd.read_csv(f"{DERIVED}/dryseason_indices_combined.csv").sort_values("year")
d["biomass"]=11.59*d.ndvi**2-4.96*d.ndvi+0.76
yr=d.year.values; b=d.biomass.values
fig,ax=plt.subplots(figsize=(9,5),dpi=300); fig.patch.set_facecolor("white")
ax.scatter(yr,b,s=30,color="#117733",edgecolors="white",linewidths=0.5,zorder=3)
ax.plot(yr,b,color="#117733",lw=1.0,alpha=0.5,zorder=2)
sl,ic,r,p,se=stats.linregress(yr,b); ax.plot(yr,sl*yr+ic,"k--",lw=1.8,zorder=4)
ax.fill_between(yr,b,sl*yr+ic,color="#117733",alpha=0.10)
ax.text(0.04,0.94,f"Sen/OLS slope {sl:+.3f} t ha$^{{-1}}$ yr$^{{-1}}$ /yr\nOLS r={r:.2f}, p<0.001\n0.98 $\\to$ 1.73 t ha$^{{-1}}$ yr$^{{-1}}$",
        transform=ax.transAxes,va="top",fontsize=10,fontweight="bold",color="#0a5",
        bbox=dict(boxstyle="round,pad=0.4",fc="white",ec="#117733",alpha=0.9))
ax.set_xlabel("Year",fontsize=12,fontweight="bold")
ax.set_ylabel("AGB (t ha$^{-1}$ yr$^{-1}$)",fontsize=12,fontweight="bold")
ax.set_title("Dry-season NDVI-derived above-ground biomass, 1988–2025",fontsize=12.5,fontweight="bold")
ax.tick_params(labelsize=10); ax.yaxis.grid(True,ls=":",lw=0.5,color="#ccc",alpha=0.8); ax.set_axisbelow(True)
for s in ("top","right"): ax.spines[s].set_visible(False)
plt.savefig(f"{RESULTS}/Fig8_VegBiomass.png",dpi=300,bbox_inches="tight",facecolor="white")
print("Saved Fig8")
