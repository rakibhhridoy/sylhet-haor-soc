import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Figure 2 (REVISED) — Topsoil properties, 1985 baseline vs 2025, nine Sylhet haors.
Grouped bars per property; 1985 bars flagged as high-uncertainty (failing physical-plausibility
screening, Section 2.3) are HATCHED and asterisked, per the data-screening described in the text.
Data: data/TopSoil.csv. Output: REVISION/Fig2_SoilProperties.png
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches
import warnings; warnings.filterwarnings('ignore')

# [path set in paths.py] ROOT = "/Volumes/SSD Rx/Research/SOC"
ts = pd.read_csv(f"{FIELD}/TopSoil.csv")
ts["Location"] = ts["Location"].replace({"Goaninghat": "Goainghat"})
p85 = ts[ts.Year == 1985].set_index("Location")
p25 = ts[ts.Year == 2025].set_index("Location")
sites = p25.sort_values("Latitude").index.tolist()

# High-uncertainty 1985 topsoil cells (from REVISION/data_quality_flags.md)
FLAG = {
    "SOC%": {"Hakaluki", "Sarail", "Terchibari"},          # peat-like / >3%
    "SBD":  {"Phagu", "Terchibari", "Ajmiriganj", "Sulla", "Goainghat"},  # >2.0 g/cm3
    "TN":   {"Hakaluki"},                                   # >0.4%
}
props = [("SOC%", "SOC (%)"), ("TN", "Total N (%)"), ("Clay", "Clay (%)"),
         ("SBD", "Bulk density (g cm$^{-3}$)"), ("CEC", "CEC (cmol$_c$ kg$^{-1}$)"), ("pH", "pH")]
C85, C25 = "#0072B2", "#E69F00"

fig = plt.figure(figsize=(15, 8.5), dpi=300); fig.patch.set_facecolor("white")
gs = GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.25, left=0.06, right=0.98, top=0.90, bottom=0.16)
x = np.arange(len(sites)); w = 0.40

for k, (col, label) in enumerate(props):
    ax = fig.add_subplot(gs[k // 3, k % 3])
    v85 = p85.reindex(sites)[col].values.astype(float)
    v25 = p25.reindex(sites)[col].values.astype(float)
    b85 = ax.bar(x - w/2, v85, w, color=C85, edgecolor="white", linewidth=0.4, label="1985 baseline")
    b25 = ax.bar(x + w/2, v25, w, color=C25, edgecolor="white", linewidth=0.4, label="2025")
    # hatch + asterisk flagged 1985 bars
    flagged = FLAG.get(col, set())
    for i, s in enumerate(sites):
        if s in flagged:
            b85[i].set_hatch("///"); b85[i].set_edgecolor("#B22222"); b85[i].set_linewidth(0.9)
            ax.text(x[i] - w/2, v85[i], "*", ha="center", va="bottom",
                    fontsize=14, fontweight="bold", color="#B22222")
    ax.set_ylabel(label, fontsize=10.5, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(sites, rotation=55, ha="right", fontsize=8.5)
    ax.tick_params(axis="y", labelsize=9)
    ax.yaxis.grid(True, ls=":", lw=0.5, color="#ccc", alpha=0.8, zorder=0); ax.set_axisbelow(True)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    ax.text(-0.12, 1.04, f"({chr(97+k)})", transform=ax.transAxes, fontsize=12, fontweight="bold")

handles = [mpatches.Patch(color=C85, label="1985 baseline"),
           mpatches.Patch(color=C25, label="2025 (field)"),
           mpatches.Patch(facecolor=C85, hatch="///", edgecolor="#B22222",
                          label="1985 value flagged high-uncertainty (*)")]
fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=10.5, frameon=False,
           bbox_to_anchor=(0.5, 0.03))
fig.suptitle("Topsoil physicochemical properties: 1985 baseline vs 2025, Sylhet haors",
             fontsize=14, fontweight="bold", y=0.96)
out = f"{RESULTS}/Fig2_SoilProperties.png"
plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
print("Saved", out)
