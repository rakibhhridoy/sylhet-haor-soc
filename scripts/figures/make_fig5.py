import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Figure 5 (REVISED) — LULC composition 2017-2024 as % of classified area (self-consistent;
avoids the absolute-area extent mismatch and includes the dominant wetland/haor class which is
absent from LULCAreaCover.csv). Composition from REVISION/diagnose_lulc_consistency.py.
 (a) open-water % vs combined water+wetland footprint % -> footprint flat, water swings (seasonal);
 (b) built-up % -> monotonic rise (robust urbanization);
 (c) vegetation % -> modest decline.
Output: REVISION/Fig5_LULCChange.png
"""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import warnings; warnings.filterwarnings("ignore")

# [path set in paths.py] ROOT = "/Volumes/SSD Rx/Research/SOC"
yr    = np.array([2017,2018,2019,2020,2021,2022,2023,2024])
water = np.array([33.6,19.6,16.9,23.0,12.4,21.4,13.0,18.9])
wet   = np.array([43.6,60.7,62.2,56.5,65.0,57.2,66.0,59.2])
veg   = np.array([9.1,8.0,7.8,7.3,7.0,6.7,6.2,7.1])
urban = np.array([7.2,9.0,10.2,10.9,12.4,12.8,12.8,12.7])
comb  = water + wet

fig, ax = plt.subplots(1, 3, figsize=(16, 4.6), dpi=300); fig.patch.set_facecolor("white")

# (a) water volatility vs stable footprint
ax[0].plot(yr, water, "o-", color="#0072B2", lw=1.8, label="Open-water class")
ax[0].plot(yr, comb, "s--", color="#117733", lw=2,
           label=f"Water+wetland footprint\n(mean {comb.mean():.0f}%, CV {100*comb.std()/comb.mean():.1f}%)")
ax[0].fill_between(yr, comb.mean()*np.ones_like(yr)-1.2, comb.mean()+1.2, color="#117733", alpha=0.15)
ax[0].set_title("(a) Open water is seasonal; footprint is stable", fontsize=10.5, fontweight="bold", loc="left")
ax[0].set_ylabel("% of classified area", fontsize=11, fontweight="bold")
ax[0].legend(fontsize=8.3, loc="center right"); ax[0].set_ylim(0, 90)
ax[0].text(0.03,0.06,"water swings 2.7$\\times$\n(trend n.s., p=0.13)",transform=ax[0].transAxes,
           fontsize=8.5,style="italic",color="#444")

# (b) urban monotonic
sl,ic,r,p,se = stats.linregress(yr, urban)
ax[1].bar(yr, urban, color="#D55E00", alpha=0.85, edgecolor="white")
ax[1].plot(yr, sl*yr+ic, "k--", lw=1.6)
ax[1].set_title("(b) Built-up: robust monotonic rise", fontsize=10.5, fontweight="bold", loc="left")
ax[1].set_ylabel("% of classified area", fontsize=11, fontweight="bold")
ax[1].text(0.96,0.08,f"7.2$\\to$12.7% (+76%)\nOLS p={p:.3f}",transform=ax[1].transAxes,
           ha="right",fontsize=9,fontweight="bold",color="#7a3300",
           bbox=dict(boxstyle="round,pad=0.3",fc="white",ec="#D55E00",alpha=0.9))

# (c) vegetation decline
sl2,ic2,r2,p2,se2 = stats.linregress(yr, veg)
ax[2].bar(yr, veg, color="#009E73", alpha=0.85, edgecolor="white")
ax[2].plot(yr, sl2*yr+ic2, "k--", lw=1.6)
ax[2].set_title("(c) Vegetation: modest decline", fontsize=10.5, fontweight="bold", loc="left")
ax[2].set_ylabel("% of classified area", fontsize=11, fontweight="bold")
ax[2].set_ylim(0, 11)
ax[2].text(0.96,0.92,f"9.1$\\to$7.1% (-22%)\nOLS p={p2:.3f}",transform=ax[2].transAxes,ha="right",va="top",
           fontsize=9,fontweight="bold",color="#0a5",
           bbox=dict(boxstyle="round,pad=0.3",fc="white",ec="#009E73",alpha=0.9))

for a in ax:
    a.set_xlabel("Year", fontsize=11, fontweight="bold"); a.tick_params(labelsize=9)
    for s in ("top","right"): a.spines[s].set_visible(False)
    a.yaxis.grid(True, ls=":", lw=0.5, color="#ccc", alpha=0.8); a.set_axisbelow(True)
fig.suptitle("LULC dynamics, Sylhet haors (2017--2024): seasonal water vs robust urban/vegetation change",
             fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
out = f"{RESULTS}/Fig5_LULCChange.png"
plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
print("Saved", out)
