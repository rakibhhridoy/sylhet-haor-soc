import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Figure 12 (NEW) — External benchmarking against WoSIS soils of the Sylhet class.
(a) SOC-property effect sizes (N-SOC, clay-SOC, clay-SOC|N partial) across the Sylhet soil
    class and its TRUE land-cover subsets (cultivated/paddy n=2425; herbaceous wetland n=96,
    Copernicus CGLS-LC100 sampled in GEE): N governs SOC; clay is weak and vanishes given N.
(b) Topsoil SOC distribution of cultivated/paddy Sylhet-class soils (n=2425) with the 9 Sylhet
    sites overlaid.
Output: REVISION/Fig12_WoSIS_benchmark.png
"""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import warnings; warnings.filterwarnings("ignore")
# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
agg=pd.read_parquet(f"{DERIVED}/wosis_topsoil_0_30.parquet")
lc=pd.read_csv(f"{DERIVED}/wosis_class_landcover.csv")
cls=agg[(agg.ph<6)&(agg.clay.between(30,75))].dropna(subset=["soc","clay"]).merge(lc[["profile_id","lc"]],on="profile_id",how="left")

def metrics(d):
    d=d.dropna(subset=["clay","soc"]); rc=stats.spearmanr(d.clay,d.soc)[0]
    dn=d.dropna(subset=["n_total"]); rn=stats.spearmanr(dn.n_total,dn.soc)[0]
    p=d.dropna(subset=["clay","soc","n_total"]); R=p[["clay","soc","n_total"]].rank(); c=np.corrcoef(R.values,rowvar=False)
    pr=(c[0,1]-c[0,2]*c[1,2])/np.sqrt((1-c[0,2]**2)*(1-c[1,2]**2))
    return rn,rc,pr,len(d)
groups=[("Sylhet class\n(all, n=9,676)",cls),
        ("Cultivated/paddy\n(n=2,425)",cls[cls.lc==40]),
        ("Herb. wetland\n(n=96)",cls[cls.lc==90])]
M=[metrics(g[1]) for g in groups]

fig,ax=plt.subplots(1,2,figsize=(14,5.2),dpi=300); fig.patch.set_facecolor("white")
metr=["N–SOC","clay–SOC","clay–SOC | N"]; colors=["#117733","#88CCAA","#DDCC77"]
x=np.arange(3); w=0.26
for j,(lab,_) in enumerate(groups):
    vals=[M[j][0],M[j][1],M[j][2]]
    bars=ax[0].bar(x+(j-1)*w,vals,w,label=lab,color=colors[j],edgecolor="white")
    for b,v in zip(bars,vals): ax[0].text(b.get_x()+b.get_width()/2,v+0.02,f"{v:+.2f}",ha="center",fontsize=7.5,fontweight="bold")
ax[0].set_xticks(x); ax[0].set_xticklabels(metr,fontsize=10,fontweight="bold")
ax[0].axhline(0,color="#333",lw=0.8); ax[0].set_ylim(-0.05,1.0)
ax[0].set_ylabel("Spearman $\\rho$",fontsize=11.5,fontweight="bold")
ax[0].set_title("(a) N governs SOC; clay vanishes once N is controlled",fontsize=10.5,fontweight="bold",loc="left")
ax[0].legend(fontsize=8.3,loc="upper right")
for s in ("top","right"): ax[0].spines[s].set_visible(False)

cul=cls[cls.lc==40].soc; syl=np.array([2.63,0.96,1.10,1.32,1.22,0.64,1.03,1.42,1.14])*10
ax[1].hist(cul.clip(upper=60),bins=30,color="#56B4E9",alpha=0.7,edgecolor="white")
ax[1].axvline(cul.median(),color="#0072B2",lw=2,ls="--",label=f"Paddy-class median {cul.median():.1f}")
for s in syl: ax[1].axvline(s,color="#D55E00",lw=1.1,alpha=0.8)
ax[1].plot([],[],color="#D55E00",lw=1.1,label="Sylhet sites (n=9)")
ax[1].axvline(syl.mean(),color="#7a3300",lw=2.2,label=f"Sylhet mean {syl.mean():.1f} ({100*(cul<syl.mean()).mean():.0f}th pct)")
ax[1].set_xlabel("Topsoil SOC (g kg$^{-1}$, 0–30 cm)",fontsize=11.5,fontweight="bold")
ax[1].set_ylabel("WoSIS profiles",fontsize=11.5,fontweight="bold")
ax[1].set_title("(b) Sylhet vs cultivated/paddy soils of its class (n=2,425)",fontsize=10.5,fontweight="bold",loc="left")
ax[1].legend(fontsize=8.3,loc="upper right")
for s in ("top","right"): ax[1].spines[s].set_visible(False)
fig.suptitle("External benchmarking of Sylhet SOC against WoSIS soils of the same class (acidic, clay-rich, 0–30 cm)",
             fontsize=12.5,fontweight="bold",y=1.01)
plt.tight_layout()
plt.savefig(f"{RESULTS}/Fig12_WoSIS_benchmark.png",dpi=300,bbox_inches="tight",facecolor="white")
print("Saved Fig12; groups:",[(g[0].split(chr(10))[0],M[i][3]) for i,g in enumerate(groups)])
