import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

#!/usr/bin/env python3
"""
Recompute every core number in the Soil Security manuscript from the source data,
run proper statistical tests, and emit an authoritative reference file.
Foundation for the rejection revision. Outputs REVISION/corrected_numbers.md.
"""
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# [path set in paths.py] ROOT = "/Volumes/SSD Rx/Research/SOC"
out = []
def w(s=""): out.append(str(s))

# ----------------------------------------------------------------------
# 1. SOC and soil properties: 1985 vs 2025 (TopSoil.csv)
# ----------------------------------------------------------------------
ts = pd.read_csv(f"{FIELD}/TopSoil.csv")
ts["Location"] = ts["Location"].replace({"Goaninghat": "Goainghat"})
p85 = ts[ts.Year == 1985].set_index("Location")
p25 = ts[ts.Year == 2025].set_index("Location")
sites = sorted(set(p85.index) & set(p25.index))

w("# Corrected Numbers & Statistics — Sylhet SOC manuscript revision")
w(f"\n_Generated from source data. {len(sites)} sites: {', '.join(sites)}_\n")

w("## 1. SOC% change 1985 -> 2025 (per site)\n")
w("| Site | SOC% 1985 | SOC% 2025 | Change % |")
w("|---|---|---|---|")
chg = {}
for s in sites:
    a, b = p85.loc[s, "SOC%"], p25.loc[s, "SOC%"]
    pc = 100 * (b - a) / a
    chg[s] = pc
    w(f"| {s} | {a:.3f} | {b:.3f} | {pc:+.1f}% |")

soc85 = p85.loc[sites, "SOC%"]; soc25 = p25.loc[sites, "SOC%"]
mean_pc = 100 * (soc25.mean() - soc85.mean()) / soc85.mean()
med85, med25 = soc85.median(), soc25.median()
w(f"\n- **Mean SOC%**: 1985 = {soc85.mean():.3f}, 2025 = {soc25.mean():.3f}  -> change in means = {mean_pc:+.1f}%")
w(f"- **Median SOC%**: 1985 = {med85:.3f}, 2025 = {med25:.3f}  -> change in medians = {100*(med25-med85)/med85:+.1f}%")
w(f"- **Median of per-site % changes**: {np.median(list(chg.values())):+.1f}%")
# sensitivity: drop the two extreme 1985 sites
outl = ["Hakaluki", "Sarail"]
keep = [s for s in sites if s not in outl]
m85k = p85.loc[keep, "SOC%"].mean(); m25k = p25.loc[keep, "SOC%"].mean()
w(f"- **Sensitivity (excl. {', '.join(outl)})**: 1985 mean = {m85k:.3f}, 2025 mean = {m25k:.3f} -> {100*(m25k-m85k)/m85k:+.1f}%")
# paired tests on SOC%
t_t, t_p = stats.ttest_rel(soc25, soc85)
w_w, w_p = stats.wilcoxon(soc25, soc85)
w(f"- Paired t-test (2025 vs 1985 SOC%): t = {t_t:.2f}, p = {t_p:.3f}")
w(f"- Wilcoxon signed-rank (robust): W = {w_w:.1f}, p = {w_p:.3f}")
w(f"- Direction: {sum(v<0 for v in chg.values())} sites decline, {sum(v>0 for v in chg.values())} increase")

# ----------------------------------------------------------------------
# 2. Correlations among 2025 soil properties (n=9) with p-values
# ----------------------------------------------------------------------
w("\n## 2. Soil-property correlations, 2025 (n=9), Pearson r (p)\n")
props = ["SOC%", "Clay", "pH", "CEC", "TN", "SBD"]
d25 = p25.loc[sites, props].astype(float)
w("Correlations with SOC% (2025):")
w("\n| vs SOC% | Pearson r | p | Spearman rho | p |")
w("|---|---|---|---|---|")
for c in props[1:]:
    r, pr = stats.pearsonr(d25["SOC%"], d25[c])
    rho, ps = stats.spearmanr(d25["SOC%"], d25[c])
    w(f"| {c} | {r:+.2f} | {pr:.3f} | {rho:+.2f} | {ps:.3f} |")
# SBD vs clay (reviewer comment 19/20)
r, pr = stats.pearsonr(d25["SBD"], d25["Clay"])
w(f"\n- SBD vs Clay (2025): r = {r:+.2f}, p = {pr:.3f}")
r, pr = stats.pearsonr(d25["CEC"], d25["Clay"])
w(f"- CEC vs Clay (2025): r = {r:+.2f}, p = {pr:.3f}")

# SOC change vs drivers (reviewer comment 40: clay strongest predictor?)
w("\n## 2b. SOC% *change* vs 2025 soil drivers (n=9)\n")
chg_arr = np.array([chg[s] for s in sites])
w("| driver (2025) | Pearson r with SOC%-change | p |")
w("|---|---|---|")
for c in ["Clay", "pH", "CEC", "TN", "SBD"]:
    r, pr = stats.pearsonr(chg_arr, d25[c].values)
    w(f"| {c} | {r:+.2f} | {pr:.3f} |")

# ----------------------------------------------------------------------
# 3. LULC change 2017 -> 2024 (CORRECTED) from LULCAreaCover.csv
# ----------------------------------------------------------------------
w("\n## 3. LULC change 2017 -> 2024 (CORRECTED)\n")
lulc = pd.read_csv(f"{GEODATA}/LULCAreaCover.csv")
y0 = lulc[lulc.Year == 2017].iloc[0]; y1 = lulc[lulc.Year == 2024].iloc[0]
w("| Class | 2017 (m2) | 2024 (m2) | delta (m2) | delta % | manuscript said |")
w("|---|---|---|---|---|---|")
ms = {"Water Area (m²)": "+8.2% (WRONG, opposite)",
      "Flood Area (m²)": "-16.3% (wrong magnitude)",
      "Vegetation Area (m²)": "+10.2% (WRONG, opposite)",
      "Urban Area (m²)": "+12.5% (wrong magnitude)"}
for c in ["Water Area (m²)", "Flood Area (m²)", "Vegetation Area (m²)", "Urban Area (m²)"]:
    d = y1[c] - y0[c]; pc = 100 * d / y0[c]
    w(f"| {c} | {y0[c]:.3e} | {y1[c]:.3e} | {d:+.3e} | {pc:+.1f}% | {ms[c]} |")
# also full-series linear trend per class
w("\n_Linear trend across 2017-2024 (slope sign / Spearman p):_")
yrs = lulc.Year.values
for c in ["Water Area (m²)", "Flood Area (m²)", "Vegetation Area (m²)", "Urban Area (m²)"]:
    sl, ic, r, pv, se = stats.linregress(yrs, lulc[c].values)
    rho, ps = stats.spearmanr(yrs, lulc[c].values)
    w(f"- {c}: slope {sl:+.3e}/yr, linreg p={pv:.3f}, Spearman rho={rho:+.2f} p={ps:.3f}")

# ----------------------------------------------------------------------
# 4. Environmental index trends 1988-2025 (indices file) + NDVI changes
# ----------------------------------------------------------------------
w("\n## 4. Environmental index trends (CORRECTED)\n")
ix = pd.read_csv(f"{GEODATA}/indices_1985_2025.csv")
ix = ix[ix.mean_ndvi != -9999].copy()
w("**NB: `mean_lst` is byte-identical to `mean_bui` (corrupt). LST values below are INVALID.**\n")
w(f"- LST==BUI identical: {(ix.mean_lst.round(6)==ix.mean_bui.round(6)).all()}")

def trend(col, label):
    sl, ic, r, pv, se = stats.linregress(ix.year, ix[col])
    rho, ps = stats.spearmanr(ix.year, ix[col])
    v0, v1 = ix[ix.year==ix.year.min()][col].values[0], ix[ix.year==ix.year.max()][col].values[0]
    w(f"- **{label}**: {ix.year.min():.0f}={v0:.4f} -> {ix.year.max():.0f}={v1:.4f} "
      f"({100*(v1-v0)/abs(v0):+.1f}%); slope={sl:+.4g}/yr, linreg p={pv:.3f}, Spearman rho={rho:+.2f} p={ps:.3f}")
trend("mean_ndvi", "NDVI (indices file)")
trend("mean_ndwi", "NDWI")
trend("mean_bui", "BUI (raw units)")

# NDVI from ndvi_changes.csv (the one used for biomass)
nv = pd.read_csv(f"{GEODATA}/ndvi_changes.csv")
n88 = nv[nv.year==1988].mean_ndvi.values[0]; n23 = nv[nv.year==2023].mean_ndvi.values[0]
w(f"\n- NDVI (ndvi_changes.csv): 1988={n88:.4f}, 2023={n23:.4f} -> {100*(n23-n88)/n88:+.1f}% "
  f"(manuscript claims +202% using a WRONG 1988 baseline of 0.049)")
sl, ic, r, pv, se = stats.linregress(nv.year, nv.mean_ndvi)
rho, ps = stats.spearmanr(nv.year, nv.mean_ndvi)
w(f"- NDVI trend 1988-2024: slope={sl:+.4g}/yr, linreg p={pv:.4f}, Spearman rho={rho:+.2f} p={ps:.4f}")

# ----------------------------------------------------------------------
# 5. Biomass equation + ESA AGB
# ----------------------------------------------------------------------
w("\n## 5. Biomass\n")
bm = pd.read_csv(f"{GEODATA}/biomass_ndvi.csv")
w(f"- NDVI-biomass columns: {list(bm.columns)}")
w(f"- Biomass equation (per CLAUDE.md): AGB = 11.59*NDVI^2 - 4.96*NDVI + 0.76")
# verify against data if columns present
numcols = [c for c in bm.columns if bm[c].dtype != object]
if "mean_ndvi" in bm.columns:
    bb = bm.dropna(subset=["mean_ndvi"])
    pred = 11.59*bb.mean_ndvi**2 - 4.96*bb.mean_ndvi + 0.76
    bcol = [c for c in bb.columns if "biom" in c.lower()]
    if bcol:
        w(f"- check: corr(predicted, stored '{bcol[0]}') = {np.corrcoef(pred, bb[bcol[0]])[0,1]:.3f}")
        w(f"- stored biomass range: {bb[bcol[0]].min():.3f} - {bb[bcol[0]].max():.3f} t/ha/yr")
ag = pd.read_csv(f"{GEODATA}/biomass_agb.csv")
agcol = [c for c in ag.columns if ag[c].dtype != object and "year" not in c.lower()]
if agcol:
    w(f"- ESA CCI AGB range: {ag[agcol[0]].min():.2f} - {ag[agcol[0]].max():.2f} Mg/ha (years present: {sorted(ag[[c for c in ag.columns if 'year' in c.lower()]].iloc[:,0].unique()) if any('year' in c.lower() for c in ag.columns) else 'n/a'})")

# ----------------------------------------------------------------------
# 6. PCA loadings table (reviewer comment 36)
# ----------------------------------------------------------------------
w("\n## 6. PCA (proper loadings table)\n")
pca_vars = ["SOC%", "Clay", "pH", "CEC", "TN", "SBD"]
X = p25.loc[sites, pca_vars].astype(float)
Xs = StandardScaler().fit_transform(X)
pca = PCA().fit(Xs)
w("| PC | eigenvalue | % var | cumulative % |")
w("|---|---|---|---|")
cum = 0
for i, (ev, vr) in enumerate(zip(pca.explained_variance_, pca.explained_variance_ratio_), 1):
    cum += vr
    w(f"| PC{i} | {ev:.3f} | {100*vr:.1f}% | {100*cum:.1f}% |")
w("\nLoadings (first 3 PCs):\n")
w("| variable | PC1 | PC2 | PC3 |")
w("|---|---|---|---|")
for j, v in enumerate(pca_vars):
    w(f"| {v} | {pca.components_[0][j]:+.2f} | {pca.components_[1][j]:+.2f} | {pca.components_[2][j]:+.2f} |")
w("\n_Note: this PCA uses the 6 soil variables on 2025 data (n=9). The manuscript's "
  "PC1=40.4%/PC2=24.8% came from a wider variable set incl. LULC-change columns; "
  "rebuild with the agreed final variable set + report this table._")

txt = "\n".join(out)
open(f"{RESULTS}/corrected_numbers.md", "w").write(txt)
print(txt)
