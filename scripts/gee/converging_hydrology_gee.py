import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
(B) Converging hydrology: corroborate the ERA5-Land drying with INDEPENDENT products.
- GLDAS-2.1 NOAH (2000-2025): root-zone soil moisture (RootMoist) + evapotranspiration (Evap).
- GRACE/GRACE-FO mascon (2002-2025): terrestrial water-storage anomaly (lwe_thickness).
Basin-mean annual, then Mann-Kendall. Output: converging_hydrology.csv
"""
import ee, geopandas as gpd, pandas as pd
ee.Initialize(project="ee-arsenicbd")
# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
geom=ee.Geometry(gpd.read_file(f"{GIS}/StudyArea.shp").to_crs(4326).geometry.iloc[0].__geo_interface__)

# ---- GLDAS 2.1 NOAH, 3-hourly 2000-present ----
gldas=ee.ImageCollection("NASA/GLDAS/V021/NOAH/G025/T3H")
def gldas_year(y):
    y=ee.Number(y); yc=gldas.filter(ee.Filter.calendarRange(y,y,"year"))
    sm=yc.select("RootMoist_inst").mean().rename("gldas_rootmoist")     # kg/m2
    et=yc.select("Evap_tavg").mean().multiply(86400).rename("gldas_et") # kg/m2/s -> mm/day
    img=sm.addBands(et)
    d=img.reduceRegion(ee.Reducer.mean(), geom, 27830, bestEffort=True, maxPixels=int(1e9), tileScale=4)
    return ee.Feature(None, ee.Dictionary(d).set("year", y))

rows=[]; yrs=list(range(2000,2026))
print("GLDAS soil moisture + ET, 3-year batches...")
for i in range(0,len(yrs),3):
    feats=ee.FeatureCollection(ee.List(yrs[i:i+3]).map(gldas_year)).getInfo()["features"]
    for f in feats:
        p=f["properties"]; rows.append(p)
        print(f"  {int(p['year'])}: rootmoist={p.get('gldas_rootmoist') and round(p['gldas_rootmoist'],1)} et={p.get('gldas_et') and round(p['gldas_et'],2)}")
g=pd.DataFrame(rows)

# ---- GRACE / GRACE-FO terrestrial water storage anomaly ----
try:
    grace=ee.ImageCollection("NASA/GRACE/MASS_GRIDS/MASCON").select("lwe_thickness")
    def grace_year(y):
        y=ee.Number(y); yc=grace.filter(ee.Filter.calendarRange(y,y,"year"))
        v=yc.mean().reduceRegion(ee.Reducer.mean(), geom, 50000, bestEffort=True, maxPixels=int(1e9)).get("lwe_thickness")
        return ee.Feature(None, {"year":y, "grace_tws_cm": v})
    gy=list(range(2003,2017))  # GRACE mascon coverage
    gr=[f["properties"] for f in ee.FeatureCollection(ee.List(gy).map(grace_year)).getInfo()["features"]]
    grdf=pd.DataFrame(gr)
    g=g.merge(grdf, on="year", how="outer")
    print("GRACE TWS merged (2003-2016).")
except Exception as e:
    print("GRACE skipped:", str(e)[:90])

g=g.sort_values("year")
g.to_csv(f"{DERIVED}/converging_hydrology.csv", index=False)
print("Saved converging_hydrology.csv"); print(g.to_string(index=False))
