import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Figure 3 (REVISED) — 2025 immobilized topsoil SOC stock (SOCiT) across the nine Sylhet haors.
Single-panel IDW map of SOCiT (the quantity discussed in the text; range 30.7-122.7 Mg/ha),
replacing the submitted map of total Stock (max ~351) and the unreliable 1985 panel (cf. comment 39).
Data: data/TopSoil.csv (2025 SOCi + site coords), gis/StudyArea.shp.
Output: REVISION/Fig3_SOCStockMap.png
"""
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from rasterio.features import geometry_mask
from rasterio.transform import from_bounds
from shapely.geometry import mapping
import warnings; warnings.filterwarnings('ignore')

# [path set in paths.py] ROOT = "/Volumes/SSD Rx/Research/SOC"
ts = pd.read_csv(f"{FIELD}/TopSoil.csv")
ts["Location"] = ts["Location"].replace({"Goaninghat": "Goainghat"})
d = ts[ts.Year == 2025].copy()
lon, lat, soc = d.Longitude.values, d.Latitude.values, d.SOCi.values
names = d.Location.values

study = gpd.read_file(f"{GIS}/StudyArea.shp").to_crs(4326)
b = study.total_bounds  # minx,miny,maxx,maxy
PAD = 0.04
nx = ny = 400
xs = np.linspace(b[0], b[2], nx); ys = np.linspace(b[3], b[1], ny)
gx, gy = np.meshgrid(xs, ys)

def idw(gx, gy, px, py, v, power=2):
    dx = gx[:, :, None] - px[None, None, :]
    dy = gy[:, :, None] - py[None, None, :]
    dist = np.sqrt(dx**2 + dy**2); dist[dist < 1e-10] = 1e-10
    w = 1.0 / dist**power
    return (w * v[None, None, :]).sum(2) / w.sum(2)

grid = idw(gx, gy, lon, lat, soc)
transform = from_bounds(b[0], b[1], b[2], b[3], nx, ny)
mask = geometry_mask([mapping(g) for g in study.geometry], transform=transform,
                     invert=True, out_shape=(ny, nx))
grid[~mask] = np.nan

SOC_CMAP = LinearSegmentedColormap.from_list(
    "soc", ["#FFFDE7", "#FFF176", "#FFD54F", "#FF8F00", "#E65100", "#4E342E"], N=256)

fig, ax = plt.subplots(figsize=(9.0, 9.5), dpi=300); fig.patch.set_facecolor("white")
im = ax.imshow(grid, extent=[b[0], b[2], b[1], b[3]], origin="upper",
               cmap=SOC_CMAP, vmin=30, vmax=125, aspect="auto", interpolation="bilinear", zorder=1)
study.plot(ax=ax, facecolor="none", edgecolor="#D55E00", linewidth=1.8, zorder=3)

cb = fig.colorbar(im, ax=ax, fraction=0.040, pad=0.02)
cb.set_label("SOCiT (Mg ha$^{-1}$)", fontsize=12, fontweight="bold")
cb.ax.tick_params(labelsize=10)

ax.scatter(lon, lat, c=soc, cmap=SOC_CMAP, vmin=30, vmax=125, s=170,
           edgecolors="white", linewidths=1.3, zorder=5)
STROKE = [pe.withStroke(linewidth=2.2, foreground="white")]
off = {"Ajmiriganj":(0.06,-0.02),"Balaganj":(-0.20,-0.05),"Goainghat":(-0.22,0.03),
       "Hakaluki":(0.05,0.02),"Kanairghat":(-0.24,-0.05),"Phagu":(-0.16,0.04),
       "Sarail":(-0.14,-0.06),"Sulla":(-0.14,0.06),"Terchibari":(0.05,0.03)}
for n, x, y, s in zip(names, lon, lat, soc):
    dx, dy = off.get(n, (0.03, 0.03))
    ax.annotate("", xy=(x+dx*0.85, y+dy*0.85), xytext=(x, y),
                arrowprops=dict(arrowstyle="-", color="#333", lw=0.5), zorder=4)
    ax.text(x+dx, y+dy, f"{n}\n{s:.0f}", fontsize=8.5, fontweight="bold",
            color="#1a1a1a", va="center", ha="left", zorder=6, path_effects=STROKE)

ax.set_xlim(b[0]-PAD, b[2]+PAD); ax.set_ylim(b[1]-PAD, b[3]+PAD)
ax.set_xlabel("Longitude (°E)", fontsize=12, fontweight="bold")
ax.set_ylabel("Latitude (°N)", fontsize=12, fontweight="bold")
ax.tick_params(labelsize=10)
for sp in ax.spines.values(): sp.set_visible(False)
# north arrow
axn = ax.inset_axes([0.04, 0.86, 0.05, 0.10]); axn.set_xlim(0,1); axn.set_ylim(0,1)
axn.fill_between([0.35,0.5,0.65],[0.15,0.88,0.15],[0.5,0.5,0.5],color="#333")
axn.text(0.5,0.0,"N",ha="center",va="bottom",fontsize=10,fontweight="bold")
axn.axis("off")
ax.set_title("2025 immobilized topsoil SOC stock (SOCiT), Sylhet haors",
             fontsize=13, fontweight="bold", pad=10)
out = f"{RESULTS}/Fig3_SOCStockMap.png"
plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
print("Saved", out, "| SOCiT range", f"{soc.min():.1f}-{soc.max():.1f}")
