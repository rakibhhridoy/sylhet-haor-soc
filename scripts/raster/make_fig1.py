import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Figure 1 (REVISED) — Study-area map of the nine Sylhet haor sites.
Addresses reviewer comment 7: the confusing SOC legend is REMOVED (sites shown as uniform
labelled markers, since SOC is a result not a locational attribute); a single elevation
colorbar, a non-overlapping scale bar and north arrow, and a regional-context inset are used.
Data: gis/DEM.tif, gis/StudyArea.shp, gis/Area.shp, gis/Location.shp, gis/ne_110m_countries.
Output: REVISION/Fig1_StudyAreaMap.png
"""
import numpy as np, geopandas as gpd, rasterio
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap, Normalize
from rasterio.enums import Resampling
from scipy.ndimage import gaussian_filter
import warnings; warnings.filterwarnings("ignore")

# [path set in paths.py] ROOT = "/Volumes/SSD Rx/Research/SOC"; GIS = f"{ROOT}/gis"
NAMES = {"Ajmiraganj":"Ajmiriganj","Balagagonj":"Balaganj","Goainghat":"Goainghat",
         "Hakaluki Haor":"Hakaluki","Kanairghat":"Kanairghat","Phagu":"Phagu",
         "Sarail":"Sarail","Sulla":"Sulla","Terchibari":"Terchibari"}

with rasterio.open(f"{GIS}/DEM.tif") as src:
    sc = 4
    dem = src.read(1, out_shape=(1, src.height//sc, src.width//sc),
                   resampling=Resampling.average).squeeze().astype(float)
    dem[dem == src.nodata] = np.nan
    b = src.bounds; ext = [b.left, b.right, b.bottom, b.top]

def hillshade(a, az=315, alt=45, ve=4):
    s = gaussian_filter(a, sigma=1.5); f = np.where(np.isnan(s), 0, s)
    dy, dx = np.gradient(f*ve); slope = np.arctan(np.sqrt(dx**2+dy**2)); aspect = np.arctan2(-dy, dx)
    hs = (np.sin(np.deg2rad(alt))*np.cos(slope) +
          np.cos(np.deg2rad(alt))*np.sin(slope)*np.cos(np.deg2rad(az)-aspect))
    hs = np.clip(hs, 0, 1); hs[np.isnan(s)] = np.nan; return hs
hs = hillshade(dem)

stops = [(-10,'#2166AC'),(0,'#74ADD1'),(4,'#ABD9E9'),(8,'#E0F3F8'),(12,'#C7E9B4'),
         (18,'#91CF60'),(28,'#BEAD7C'),(55,'#9E7A3E'),(110,'#6B4226'),(175,'#F5F5F5')]
vv = [v for v,_ in stops]; cc = [c for _,c in stops]
cmap = LinearSegmentedColormap.from_list("ter", list(zip(np.interp(vv,[min(vv),max(vv)],[0,1]), cc)), N=512)
norm = Normalize(vmin=np.nanmin(dem), vmax=np.nanmax(dem))

study = gpd.read_file(f"{GIS}/StudyArea.shp").to_crs(4326)
area  = gpd.read_file(f"{GIS}/Area.shp").to_crs(4326)
loc   = gpd.read_file(f"{GIS}/Location.shp").to_crs(4326)
world = gpd.read_file(f"{GIS}/ne_110m_countries/ne_110m_admin_0_countries.shp").to_crs(4326)

fig = plt.figure(figsize=(11, 10), dpi=300); fig.patch.set_facecolor("white")
ax = fig.add_axes([0.07, 0.07, 0.78, 0.86])
ax.imshow(hs, extent=ext, origin="upper", cmap="gray", alpha=0.55, zorder=1)
ax.imshow(np.ma.masked_invalid(dem), extent=ext, origin="upper", cmap=cmap, norm=norm,
          alpha=0.62, zorder=2)
area.plot(ax=ax, facecolor="none", edgecolor="#0072B2", lw=0.6, ls="--", zorder=3)
study.plot(ax=ax, facecolor="none", edgecolor="#D55E00", lw=2.0, zorder=4)

# uniform sampling-site markers (NO SOC coloring)
ax.scatter(loc.geometry.x, loc.geometry.y, s=95, marker="^", c="#B2182B",
           edgecolors="white", linewidths=1.1, zorder=6)
STROKE = [pe.withStroke(linewidth=2.2, foreground="white")]
off = {"Ajmiriganj":(0.05,-0.05),"Balaganj":(-0.22,-0.05),"Goainghat":(0.05,0.03),
       "Hakaluki":(0.05,0.0),"Kanairghat":(-0.26,-0.03),"Phagu":(-0.16,0.04),
       "Sarail":(-0.14,-0.06),"Sulla":(-0.15,0.05),"Terchibari":(0.05,0.03)}
for _, r in loc.iterrows():
    nm = NAMES[r["Site Name"]]; dx, dy = off[nm]; x, y = r.geometry.x, r.geometry.y
    ax.annotate("", xy=(x+dx*0.8, y+dy*0.8), xytext=(x, y),
                arrowprops=dict(arrowstyle="-", color="#333", lw=0.5), zorder=5)
    ax.text(x+dx, y+dy, nm, fontsize=9.5, fontweight="bold", color="#111",
            va="center", ha="left", zorder=7, path_effects=STROKE)

PAD = 0.04
ax.set_xlim(b.left-PAD, b.right+PAD); ax.set_ylim(b.bottom-PAD, b.top+PAD)
ax.set_xlabel("Longitude (°E)", fontsize=12, fontweight="bold")
ax.set_ylabel("Latitude (°N)", fontsize=12, fontweight="bold")
ax.tick_params(labelsize=10)

# north arrow (lower-left, above the scale bar, clear of the inset)
ax.annotate("N", xy=(0.06, 0.24), xytext=(0.06, 0.15), xycoords="axes fraction",
            ha="center", fontsize=13, fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color="#222", lw=2))
# scale bar (bottom-left), ~20 km. 1 deg lon ~ 101 km at 24.5N
deg = 20/101.0; x0 = b.left-PAD+0.05; y0 = b.bottom-PAD+0.04
ax.plot([x0, x0+deg], [y0, y0], color="#111", lw=3, solid_capstyle="butt", zorder=8)
ax.text(x0+deg/2, y0+0.015, "20 km", ha="center", fontsize=9, fontweight="bold", zorder=8)

# single elevation colorbar
cax = fig.add_axes([0.87, 0.30, 0.022, 0.40])
cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
cb.set_label("Elevation (m a.s.l.)", fontsize=11, fontweight="bold")
cb.ax.tick_params(labelsize=9)

# legend for boundaries/sites (top-right, no SOC)
handles = [Line2D([0],[0], color="#D55E00", lw=2.0, label="Study boundary"),
           Line2D([0],[0], color="#0072B2", lw=0.8, ls="--", label="District boundary"),
           Line2D([0],[0], marker="^", color="w", markerfacecolor="#B2182B",
                  markeredgecolor="white", markersize=10, label="Sampling site")]
ax.legend(handles=handles, loc="upper right", fontsize=9.5, frameon=True,
          framealpha=0.92, edgecolor="#ccc")

# regional context inset (Bangladesh + study box)
axin = fig.add_axes([0.085, 0.70, 0.20, 0.22])
world.plot(ax=axin, facecolor="#eee", edgecolor="#999", lw=0.4)
world[world.NAME == "Bangladesh"].plot(ax=axin, facecolor="#56B4E9", edgecolor="#333", lw=0.5)
axin.add_patch(plt.Rectangle((b.left, b.bottom), b.right-b.left, b.top-b.bottom,
               fill=False, edgecolor="#D55E00", lw=1.5))
axin.set_xlim(87.8, 92.9); axin.set_ylim(20.5, 26.8)
axin.set_xticks([]); axin.set_yticks([])
axin.set_title("Bangladesh", fontsize=8.5, fontweight="bold", pad=2)

ax.set_title("Study area: nine haor wetland sites, Sylhet Basin",
             fontsize=13.5, fontweight="bold", pad=10)
out = f"{RESULTS}/Fig1_StudyAreaMap.png"
plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
print("Saved", out)
