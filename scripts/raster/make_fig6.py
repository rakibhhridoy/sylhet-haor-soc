import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Figure 6 (REVISED) — LULC classification maps 2017-2024 (2x4 grid).
Addresses reviewer comment 29: sampling points enlarged and labelled with site names.
Source rasters recovered from backup (originals missing from gis/); verified to reproduce
geodata/LULCAreaCover.csv areas exactly. Output: REVISION/Fig6_LULCMaps.png
"""
import numpy as np, geopandas as gpd, rasterio
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.lines import Line2D
import warnings; warnings.filterwarnings("ignore")

# [path set in paths.py] ROOT = "/Volumes/SSD Rx/Research/SOC"
# [path set in paths.py] BK   = "/Volumes/SSD Rx/rakibhhridoyws/BackUp/M1/Research1/SOC/gis"
YEARS = list(range(2017, 2025))
STEP = 16  # downsample 10 m -> 160 m for display

CLASS_INFO = {1:("Water","#0072B2"), 2:("Vegetation","#009E73"), 4:("Flood-prone","#56B4E9"),
              5:("Wetland (haor)","#F0E442"), 7:("Urban / built-up","#D55E00"),
              8:("Bare / fallow","#999999"), 10:("Other","#CC79A7"), 11:("Flooded vegetation","#117733")}
CODES = [0,1,2,4,5,7,8,10,11]
COLORS = ["#FFFFFF"] + [CLASS_INFO[c][1] for c in CODES[1:]]
idx = {c:i for i,c in enumerate(CODES)}
cmap = ListedColormap(COLORS); norm = BoundaryNorm(np.arange(-0.5, len(CODES)), len(CODES))

with rasterio.open(f"{GIS}/LULC{YEARS[0]}c.tif") as s:
    transform, crs, (nr, nc) = s.transform, s.crs, s.shape
inv = ~transform
loc = gpd.read_file(f"{GIS}/Location.shp").to_crs(crs)
NAMES = {"Ajmiraganj":"Ajmiriganj","Balagagonj":"Balaganj","Goainghat":"Goainghat",
         "Hakaluki Haor":"Hakaluki","Kanairghat":"Kanairghat","Phagu":"Phagu",
         "Sarail":"Sarail","Sulla":"Sulla","Terchibari":"Terchibari"}
scol, srow = [], []
for x, y in zip(loc.geometry.x, loc.geometry.y):
    c, r = inv * (x, y); scol.append(c/STEP); srow.append(r/STEP)
scol, srow = np.array(scol), np.array(srow)

def read(y):
    with rasterio.open(f"{GIS}/LULC{y}c.tif") as s:
        d = s.read(1)[::STEP, ::STEP].astype(float)
    out = np.zeros_like(d)
    for c, i in idx.items(): out[d == c] = i
    return out

off = {"Ajmiriganj":(0.04,-0.02),"Balaganj":(-0.30,-0.02),"Goainghat":(0.04,0.0),
       "Hakaluki":(0.04,0.0),"Kanairghat":(-0.34,0.0),"Phagu":(-0.20,0.0),
       "Sarail":(-0.18,0.0),"Sulla":(0.04,-0.02),"Terchibari":(0.04,0.0)}
dnr, dnc = nr//STEP, nc//STEP
STROKE = [pe.withStroke(linewidth=1.8, foreground="white")]

fig, axes = plt.subplots(2, 4, figsize=(18, 10.5), dpi=300,
                         gridspec_kw={"hspace":0.10, "wspace":0.04})
fig.patch.set_facecolor("white")
for i, (ax, yr) in enumerate(zip(axes.flat, YEARS)):
    ax.imshow(read(yr), origin="upper", cmap=cmap, norm=norm, interpolation="nearest", zorder=1)
    ax.scatter(scol, srow, s=70, marker="^", c="#111", edgecolors="white",
               linewidths=1.0, zorder=4)
    # site labels only on first panel to avoid clutter; markers on all
    if i == 0:
        for (_, r), c, rw in zip(loc.iterrows(), scol, srow):
            nm = NAMES[r["Site Name"]]; dx, dy = off[nm]
            ax.text(c + dx*dnc, rw + dy*dnr, nm, fontsize=8.5, fontweight="bold",
                    color="#111", va="center", ha="left" if dx>0 else "right",
                    zorder=5, path_effects=STROKE)
    ax.text(0.5, 1.03, f"({chr(97+i)}) {yr}", transform=ax.transAxes,
            fontsize=12, fontweight="bold", ha="center", va="bottom")
    ax.set_xlim(0, dnc); ax.set_ylim(dnr, 0)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)

handles = [mpatches.Patch(facecolor=CLASS_INFO[c][1], edgecolor="#555", label=CLASS_INFO[c][0])
           for c in CODES[1:]]
handles.append(Line2D([0],[0], marker="^", color="none", markerfacecolor="#111",
               markeredgecolor="white", markersize=10, label="Sampling site"))
fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=12, frameon=True,
           framealpha=0.95, edgecolor="#ccc", bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Land use / land cover classification, Sylhet haors (2017–2024)",
             fontsize=15, fontweight="bold", y=1.0)
out = f"{RESULTS}/Fig6_LULCMaps.png"
plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
print("Saved", out)
