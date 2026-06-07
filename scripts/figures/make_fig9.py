import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Figure 9 (REVISED) — Exploratory multivariate structure of 2025 soil properties (n=9).
(a) PCA score plot (sites), (b) PCA loading plot (variables) -- separated per comment 37;
(c) Pearson correlation heatmap with significance stars per comment 35/37.
Key corrected message: SOC% loads WITH TN on PC2, NOT with clay (clay loads on PC1 w/ CEC,pH).
Data: data/TopSoil.csv (2025). Output: REVISION/Fig9_SOC_PCA_Corr.png
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings; warnings.filterwarnings('ignore')

# [path set in paths.py] ROOT = "/Volumes/SSD Rx/Research/SOC"
ts = pd.read_csv(f"{FIELD}/TopSoil.csv")
ts["Location"] = ts["Location"].replace({"Goaninghat": "Goainghat"})
d = ts[ts.Year == 2025].set_index("Location")
sites = list(d.index)
vars = ["SOC%", "Clay", "pH", "CEC", "TN", "SBD"]
X = d[vars].astype(float)
Xs = StandardScaler().fit_transform(X)
pca = PCA().fit(Xs)
scores = pca.transform(Xs)
load = pca.components_.T  # (var, PC)
ev = pca.explained_variance_ratio_ * 100

fig = plt.figure(figsize=(16, 5.2), dpi=300); fig.patch.set_facecolor("white")
gs = GridSpec(1, 3, figure=fig, wspace=0.32, left=0.06, right=0.97, top=0.88, bottom=0.14)

# ---- (a) score plot ----
axa = fig.add_subplot(gs[0])
axa.axhline(0, color="#ccc", lw=0.7, zorder=0); axa.axvline(0, color="#ccc", lw=0.7, zorder=0)
axa.scatter(scores[:, 0], scores[:, 1], s=90, c="#0072B2", edgecolors="white", linewidths=1, zorder=3)
for i, s in enumerate(sites):
    axa.annotate(s, (scores[i, 0], scores[i, 1]), fontsize=8.5, fontweight="bold",
                 xytext=(4, 4), textcoords="offset points")
axa.set_xlabel(f"PC1 ({ev[0]:.1f}%)", fontsize=11.5, fontweight="bold")
axa.set_ylabel(f"PC2 ({ev[1]:.1f}%)", fontsize=11.5, fontweight="bold")
axa.set_title("(a) Site scores", fontsize=12, fontweight="bold", loc="left")
for sp in ("top", "right"): axa.spines[sp].set_visible(False)

# ---- (b) loading plot ----
axb = fig.add_subplot(gs[1])
axb.axhline(0, color="#ccc", lw=0.7); axb.axvline(0, color="#ccc", lw=0.7)
for i, v in enumerate(vars):
    axb.arrow(0, 0, load[i, 0], load[i, 1], head_width=0.03, color="#D55E00",
              lw=1.8, length_includes_head=True, zorder=3)
    axb.text(load[i, 0]*1.12, load[i, 1]*1.12, v, fontsize=10, fontweight="bold",
             ha="center", va="center", color="#7a3300")
axb.set_xlim(-1, 1); axb.set_ylim(-1, 1)
axb.set_xlabel(f"PC1 ({ev[0]:.1f}%)", fontsize=11.5, fontweight="bold")
axb.set_ylabel(f"PC2 ({ev[1]:.1f}%)", fontsize=11.5, fontweight="bold")
axb.set_title("(b) Variable loadings", fontsize=12, fontweight="bold", loc="left")
axb.text(0.5, -0.93, "SOC loads with TN (PC2),\nnot with clay (PC1)", fontsize=8.5,
         ha="center", style="italic", color="#444")
for sp in ("top", "right"): axb.spines[sp].set_visible(False)

# ---- (c) correlation heatmap with significance stars ----
axc = fig.add_subplot(gs[2])
n = len(vars); R = np.zeros((n, n)); P = np.ones((n, n))
for i in range(n):
    for j in range(n):
        R[i, j], P[i, j] = stats.pearsonr(X.iloc[:, i], X.iloc[:, j])
im = axc.imshow(R, cmap="RdBu_r", vmin=-1, vmax=1)
axc.set_xticks(range(n)); axc.set_yticks(range(n))
axc.set_xticklabels(vars, rotation=45, ha="right", fontsize=9.5, fontweight="bold")
axc.set_yticklabels(vars, fontsize=9.5, fontweight="bold")
def star(p): return "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
for i in range(n):
    for j in range(n):
        txt = f"{R[i,j]:.2f}\n{star(P[i,j])}" if i != j else "1"
        axc.text(j, i, txt, ha="center", va="center", fontsize=7.5,
                 color="white" if abs(R[i, j]) > 0.6 else "#222", fontweight="bold")
cb = fig.colorbar(im, ax=axc, fraction=0.046, pad=0.04); cb.set_label("Pearson r", fontsize=10, fontweight="bold")
axc.set_title("(c) Correlations (* p<.05, ** p<.01, *** p<.001)", fontsize=11, fontweight="bold", loc="left")

fig.suptitle("Exploratory multivariate structure of 2025 soil properties (n = 9)",
             fontsize=13.5, fontweight="bold", y=0.99)
out = f"{RESULTS}/Fig9_SOC_PCA_Corr.png"
plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
print("Saved", out, f"| PC1={ev[0]:.1f}% PC2={ev[1]:.1f}%")
