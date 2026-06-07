import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

#!/usr/bin/env python3
"""
Extract REAL annual Land Surface Temperature (LST) for the Sylhet study area
from Landsat Collection-2 Level-2 thermal bands, 1985-2025 (server-side, one fetch).

Replaces the corrupt `mean_lst` column in geodata/indices_1985_2025.csv
(a byte-for-byte duplicate of mean_bui).

RUN:
    earthengine authenticate          # one-time (browser); credentials already present here
    python3 REVISION/extract_lst_gee.py
Output: REVISION/lst_real_1985_2025.csv  (year, mean_lst_C, n_images)

Science notes (for Methods):
- C2 L2 surface-temperature band: ST_B6 (L5/L7), ST_B10 (L8/L9).
- LST(C) = ST * 0.00341802 + 149.0 - 273.15  [USGS C2 L2 scaling, Kelvin->C].
- Cloud/shadow masked via QA_PIXEL bits 3 (cloud) & 4 (cloud shadow).
- Annual mean image, then basin spatial mean at 100 m (LST is smooth; fast & robust).
- Pre-2010 thermal coverage is sparse; years with n_images < 3 are flagged.
"""
import ee, geopandas as gpd, pandas as pd

PROJECT = "ee-arsenicbd"
SHP = f"{GIS}/StudyArea.shp"
OUT = f"{DERIVED}/lst_real_1985_2025.csv"

ee.Initialize(project=PROJECT)
gdf = gpd.read_file(SHP).to_crs(4326)
geom = ee.Geometry(gdf.geometry.iloc[0].__geo_interface__)

def lst_band(img, band):
    qa = img.select("QA_PIXEL")
    mask = qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 4).eq(0))
    lst = img.select(band).multiply(0.00341802).add(149.0 - 273.15).rename("LST_C")
    return lst.updateMask(mask).set("year", ee.Image(img).date().get("year"))

def tagged(cid, band):
    return (ee.ImageCollection(cid).filterBounds(geom)
            .filter(ee.Filter.lt("CLOUD_COVER", 60))
            .map(lambda im: lst_band(im, band)))

merged = (tagged("LANDSAT/LT05/C02/T1_L2", "ST_B6")
          .merge(tagged("LANDSAT/LE07/C02/T1_L2", "ST_B6"))
          .merge(tagged("LANDSAT/LC08/C02/T1_L2", "ST_B10"))
          .merge(tagged("LANDSAT/LC09/C02/T1_L2", "ST_B10")))

def per_year(y):
    y = ee.Number(y)
    yc = merged.filter(ee.Filter.eq("year", y))
    stats = yc.mean().reduceRegion(ee.Reducer.mean(), geom, scale=100,
                                   bestEffort=True, maxPixels=int(1e9), tileScale=4)
    val = ee.Dictionary(stats).get("LST_C", -9999)  # default for empty/all-masked years
    return ee.Feature(None, {"year": y, "mean_lst_C": val, "n_images": yc.size()})

print("Computing server-side in 5-year batches...")
rows = []
all_years = list(range(1985, 2026))
for i in range(0, len(all_years), 5):
    batch = all_years[i:i + 5]
    fc = ee.FeatureCollection(ee.List(batch).map(per_year))
    feats = fc.getInfo()["features"]
    for f in feats:
        rows.append(f["properties"])
        p = f["properties"]
        v = p.get("mean_lst_C")
        print(f"  {int(p['year'])}: LST={'NA' if v is None else round(v,2)} C (n={p['n_images']})")
df = pd.DataFrame(rows).sort_values("year")[["year", "mean_lst_C", "n_images"]]
df["year"] = df["year"].astype(int)
df["mean_lst_C"] = df["mean_lst_C"].replace(-9999, pd.NA)
df.to_csv(OUT, index=False)
print(f"Saved {OUT}\n")
print(df.to_string(index=False))

ok = df.dropna(subset=["mean_lst_C"])
ok = ok[ok.n_images >= 3]
if len(ok) > 3:
    from scipy import stats
    sl, ic, r, p, se = stats.linregress(ok.year, ok.mean_lst_C)
    print(f"\nLST trend (years with n>=3, n={len(ok)}): {sl*10:+.2f} C/decade, p={p:.3f}; "
          f"{ok.year.min()}={ok.mean_lst_C.iloc[0]:.1f}C -> {ok.year.max()}={ok.mean_lst_C.iloc[-1]:.1f}C")
