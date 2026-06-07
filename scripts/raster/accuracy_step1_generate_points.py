import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
LULC accuracy assessment -- STEP 1: generate stratified-random reference points.
Reviewer comment 9. There is no archived ground-truth, so we build a defensible post-hoc
accuracy assessment: sample N points per class from the classified map, which a human then
labels with the TRUE class by inspecting high-resolution imagery (Google Earth/Esri/Planet)
or field knowledge. STEP 2 computes the confusion matrix, overall accuracy and kappa.

Output: REVISION/accuracy_points_2024.csv  (lon, lat, predicted_class, true_class[BLANK])
        REVISION/accuracy_points_2024.geojson  (load in QGIS/Google Earth to label)
Edit YEAR / N_PER_CLASS as needed. Assess 2024 (best reference imagery); repeat for 2017 if desired.
"""
import numpy as np, pandas as pd, geopandas as gpd, rasterio
from rasterio.transform import xy
from shapely.geometry import Point
import json

YEAR = 2024
N_PER_CLASS = 40           # >=30 recommended for stable per-class accuracy
SEED = 42
# [path set in paths.py] ROOT = "/Volumes/SSD Rx/Research/SOC"
TIF = f"{GIS}/LULC{YEAR}c.tif"
CLASS_NAMES = {1:"Water",2:"Vegetation",4:"Flood-prone",5:"Wetland",
               7:"Urban",8:"Bare/Fallow",10:"Other",11:"Flooded vegetation"}

rng = np.random.default_rng(SEED)
with rasterio.open(TIF) as s:
    arr = s.read(1)
    transform, crs = s.transform, s.crs

rows = []
for code, name in CLASS_NAMES.items():
    ys, xs = np.where(arr == code)
    if len(ys) == 0:
        continue
    n = min(N_PER_CLASS, len(ys))
    pick = rng.choice(len(ys), size=n, replace=False)
    for r, c in zip(ys[pick], xs[pick]):
        x, y = xy(transform, int(r), int(c))   # map coords (EPSG:32646)
        rows.append({"row":int(r),"col":int(c),"x":x,"y":y,
                     "predicted_code":int(code),"predicted_class":name,"true_class":""})

df = pd.DataFrame(rows)
gdf = gpd.GeoDataFrame(df, geometry=[Point(x,y) for x,y in zip(df.x,df.y)], crs=crs).to_crs(4326)
df["lon"], df["lat"] = gdf.geometry.x, gdf.geometry.y
df = df[["lon","lat","x","y","row","col","predicted_code","predicted_class","true_class"]]
df.to_csv(f"{DERIVED}/accuracy_points_{YEAR}.csv", index=False)
gdf.to_file(f"{DERIVED}/accuracy_points_{YEAR}.geojson", driver="GeoJSON")

print(f"Generated {len(df)} stratified-random reference points for {YEAR}:")
print(df.groupby("predicted_class").size().to_string())
print(f"\nFiles: REVISION/accuracy_points_{YEAR}.csv  +  .geojson")
print("NEXT: open the points over high-resolution imagery (QGIS + Google/Esri basemap, or")
print("Google Earth), fill the 'true_class' column with the actual class at each point,")
print("then run accuracy_step2_compute.py.")
