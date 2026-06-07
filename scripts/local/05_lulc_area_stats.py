"""
LULC composition statistics, 2017-2024 (Section 3.3 / Figs 5-6 of the manuscript).

Reproduces the percent-of-area, fold-range and footprint-stability numbers cited in the
text directly from the cached per-year 8-class composition table
(data/derived/lulc_composition_2017_2024.csv). That table was produced from the classified
Sentinel-2 rasters by scripts/raster/diagnose_lulc_consistency.py (the rasters, ~6.5 GB, are
not redistributed here -- see DATA_SOURCES.md); the composition percentages are the cached
intermediate so these numbers reproduce offline.

Reproduces:
  - Built-up 7.2 -> 12.7% of area (+76% relative)
  - Vegetation class 9.1 -> 7.1% (-22% relative)
  - Open water 12.4-33.6% of area (2.7-fold swing)
  - Water + wetland footprint ~78.7 +/- 1.0% (CV ~1.3%)
  - Water + wetland + flood-prone footprint ~80.6 +/- 1.1% (CV ~1.4%)
Outputs: results/lulc_area_stats.md (also printed).
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import DERIVED, RESULTS  # noqa: E402

import pandas as pd, numpy as np  # noqa: E402

df = pd.read_csv(f"{DERIVED}/lulc_composition_2017_2024.csv").set_index("year")

def rel(a, b):       # relative change a->b in %
    return 100 * (b - a) / a

def cv(x):           # coefficient of variation in %
    return 100 * np.std(x, ddof=0) / np.mean(x)

urb = df["Urban"]; veg = df["Vegetation"]; wat = df["Water"]
foot2 = df["Water"] + df["Wetland"]
foot3 = df["Water"] + df["Wetland"] + df["Flood"]

out = ["# LULC composition statistics, 2017-2024 (percent of always-valid classified area)\n",
       "Source: data/derived/lulc_composition_2017_2024.csv (cached 8-class composition from",
       "the Sentinel-2 rasters; see scripts/raster/diagnose_lulc_consistency.py).\n",
       "## Robust signals",
       f"- **Built-up**: {urb.iloc[0]:.1f}% (2017) -> {urb.iloc[-1]:.1f}% (2024) = {rel(urb.iloc[0],urb.iloc[-1]):+.0f}% relative",
       f"- **Built-up excl. 2017**: {urb.iloc[1]:.1f}% (2018) -> {urb.iloc[-1]:.1f}% (2024) = {rel(urb.iloc[1],urb.iloc[-1]):+.0f}% relative",
       f"- **Vegetation class**: {veg.iloc[0]:.1f}% -> {veg.iloc[-1]:.1f}% = {rel(veg.iloc[0],veg.iloc[-1]):+.0f}% relative\n",
       "## Seasonal (not land-use) signals",
       f"- **Open water**: range {wat.min():.1f}-{wat.max():.1f}% of area = {wat.max()/wat.min():.1f}-fold swing",
       f"- **Open water 2017 vs 2024 (endpoint)**: {wat.iloc[0]:.1f}% -> {wat.iloc[-1]:.1f}% = {rel(wat.iloc[0],wat.iloc[-1]):+.1f}% (endpoint artifact)\n",
       "## Footprint stability (the key reconciliation)",
       f"- **Water + wetland footprint**: {foot2.mean():.1f} +/- {foot2.std(ddof=0):.1f}% (CV {cv(foot2):.1f}%)",
       f"- **Water + wetland + flood-prone**: {foot3.mean():.1f} +/- {foot3.std(ddof=0):.1f}% (CV {cv(foot3):.1f}%)",
       f"- i.e. the combined footprint is near-constant while the open-water fraction swings {wat.max()/wat.min():.1f}-fold.\n",
       "## Spatial coherence of 2017->2024 change (raster-derived; see diagnose_lulc_consistency.py)",
       "- changed pixels: 28.4% of area; of those only 5.2% are isolated (no changed neighbour),",
       "  i.e. coherent zone-flips along the migrating flood line, not salt-and-pepper classifier noise."]
txt = "\n".join(out)
open(f"{RESULTS}/lulc_area_stats.md", "w").write(txt)
print(txt)
print(f"\nSaved {RESULTS}/lulc_area_stats.md")
