import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Recompute per-site 500 m buffer LULC areas (2017 & 2024) from the recovered LULC rasters,
replacing the unreproducible per-site numbers in the old section 3.4 (reviewer comment 30).
Windowed reads (each buffer ~100x100 px) -> fast & low-memory.
Output: REVISION/buffer_lulc_per_site.csv  +  printed LaTeX-ready table.
"""
import numpy as np, geopandas as gpd, rasterio, pandas as pd
from rasterio.windows import from_bounds
import warnings; warnings.filterwarnings("ignore")

# [path set in paths.py] ROOT = "/Volumes/SSD Rx/Research/SOC"
# [path set in paths.py] BK   = "/Volumes/SSD Rx/rakibhhridoyws/BackUp/M1/Research1/SOC/gis"
NAMES = {"Ajmiraganj":"Ajmiriganj","Balagagonj":"Balaganj","Goainghat":"Goainghat",
         "Hakaluki Haor":"Hakaluki","Kanairghat":"Kanairghat","Phagu":"Phagu",
         "Sarail":"Sarail","Sulla":"Sulla","Terchibari":"Terchibari"}
CLASSES = {1:"Water", 2:"Vegetation", 4:"Flood", 7:"Urban", 11:"FloodedVeg"}
R = 500.0  # buffer radius (m)

with rasterio.open(f"{GIS}/LULC2017c.tif") as s:
    crs = s.crs; px = abs(s.transform[0])
loc = gpd.read_file(f"{GIS}/Location.shp").to_crs(crs)

def buffer_areas(year):
    rows = {}
    with rasterio.open(f"{GIS}/LULC{year}c.tif") as s:
        for _, r in loc.iterrows():
            cx, cy = r.geometry.x, r.geometry.y
            win = from_bounds(cx-R, cy-R, cx+R, cy+R, s.transform)
            arr = s.read(1, window=win)
            wt = s.window_transform(win)
            ny, nx = arr.shape
            xs = wt.c + (np.arange(nx)+0.5)*wt.a
            ys = wt.f + (np.arange(ny)+0.5)*wt.e
            gx, gy = np.meshgrid(xs, ys)
            mask = (gx-cx)**2 + (gy-cy)**2 <= R*R
            nm = NAMES[r["Site Name"]]
            rows[nm] = {lbl: int(((arr==code)&mask).sum())*px*px for code,lbl in CLASSES.items()}
    return pd.DataFrame(rows).T

a17, a24 = buffer_areas(2017), buffer_areas(2024)
chg = (a24 - a17)
chg.columns = [f"{c}_change_m2" for c in chg.columns]
out = pd.concat([a17.add_suffix("_2017_m2"), a24.add_suffix("_2024_m2"), chg], axis=1)
out.to_csv(f"{DERIVED}/buffer_lulc_per_site.csv")

print("Per-site 500 m buffer area CHANGE 2017->2024 (m2):")
print(chg.round(0).to_string())
print("\nRange per class (m2):")
for c in chg.columns:
    print(f"  {c}: {chg[c].min():+.0f} to {chg[c].max():+.0f}")
print("\nSaved REVISION/buffer_lulc_per_site.csv")
