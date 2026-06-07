import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Fig 13 (v2) — climate-restricted space-for-time. (a) SOC vs MAT (binned). (b) standardized
log-SOC regression coefficients for the GLOBAL gradient vs the Sylhet-like WARM&WET restriction,
showing the temperature effect shrinks and nitrogen dominates once the climate-zone confound is
removed. Output: Submission_JEM/Fig13_climate_soc.png
"""
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression; from sklearn.preprocessing import StandardScaler
import warnings; warnings.filterwarnings("ignore")
# [path set in paths.py] R="/Volumes/SSD Rx/Research/SOC/REVISION"; OUT="/Volumes/SSD Rx/Research/SOC/Submission_JEM"
agg=pd.read_parquet(f"{DERIVED}/wosis_topsoil_0_30.parquet"); clim=pd.read_csv(f"{DERIVED}/wosis_class_climate.csv")
d=agg[(agg.ph<6)&(agg.clay.between(30,75))].merge(clim,on="profile_id",how="left")
d=d[d.soc>0].dropna(subset=["soc","clay","mat"]); d["logsoc"]=np.log(d.soc)

def betas(dd):
    m=dd.dropna(subset=["logsoc","mat","n_total","map","clay"])
    X=StandardScaler().fit_transform(m[["mat","n_total","map","clay"]]); y=(m.logsoc-m.logsoc.mean())/m.logsoc.std()
    b=LinearRegression().fit(X,y); return b.coef_, len(m)
glob,ng=betas(d)
warm=d[(d.mat.between(20,30))&(d['map']>1200)]; ww,nw=betas(warm)

fig,ax=plt.subplots(1,2,figsize=(13,5),dpi=300); fig.patch.set_facecolor("white")
dd=d.dropna(subset=["mat","soc"])
ax[0].scatter(dd.mat,dd.soc.clip(upper=80),s=5,alpha=0.12,color="#CC79A7")
bins=np.linspace(dd.mat.min(),dd.mat.max(),12); dd["b"]=pd.cut(dd.mat,bins)
g=dd.groupby("b").agg(mat=("mat","mean"),soc=("soc","median")).dropna()
ax[0].plot(g.mat,g.soc,"o-",color="#7a1f5a",lw=2,label="binned median SOC")
ax[0].axvspan(20,30,color="#ffd166",alpha=0.15,label="Sylhet-like (20–30 °C)")
ax[0].set_xlabel("Mean annual temperature (°C)",fontsize=11.5,fontweight="bold")
ax[0].set_ylabel("Topsoil SOC (g kg$^{-1}$)",fontsize=11.5,fontweight="bold")
ax[0].set_title("(a) SOC vs temperature (Sylhet soil class)",fontsize=10.5,fontweight="bold",loc="left")
ax[0].legend(fontsize=9);
for s in ("top","right"): ax[0].spines[s].set_visible(False)

names=["MAT","Total N","MAP","Clay"]; x=np.arange(4); w=0.38
ax[1].bar(x-w/2,glob,w,label=f"Global gradient (n={ng:,})",color="#9aa7b8",edgecolor="white")
ax[1].bar(x+w/2,ww,w,label=f"Sylhet-like warm&wet (n={nw:,})",color="#117733",edgecolor="white")
for xi,v in zip(x-w/2,glob): ax[1].text(xi,v+(0.02 if v>=0 else -0.04),f"{v:+.2f}",ha="center",fontsize=8)
for xi,v in zip(x+w/2,ww): ax[1].text(xi,v+(0.02 if v>=0 else -0.04),f"{v:+.2f}",ha="center",fontsize=8,fontweight="bold")
ax[1].axhline(0,color="#333",lw=0.8); ax[1].set_xticks(x); ax[1].set_xticklabels(names,fontsize=10,fontweight="bold")
ax[1].set_ylabel("Standardized coefficient (logSOC)",fontsize=11.5,fontweight="bold")
ax[1].set_title("(b) Restricting to Sylhet-like climate: MAT effect shrinks, N dominates",fontsize=9.8,fontweight="bold",loc="left")
ax[1].legend(fontsize=8.5,loc="upper right")
for s in ("top","right"): ax[1].spines[s].set_visible(False)
fig.suptitle("Space-for-time: temperature lowers SOC, but nitrogen is the dominant control within Sylhet-like climates",fontsize=11.5,fontweight="bold",y=1.0)
plt.tight_layout(); plt.savefig(f"{RESULTS}/Fig13_climate_soc.png",dpi=300,bbox_inches="tight",facecolor="white")
print(f"Saved Fig13. global bMAT={glob[0]:+.2f} bN={glob[1]:+.2f} | warm&wet bMAT={ww[0]:+.2f} bN={ww[1]:+.2f} (n={nw})")
