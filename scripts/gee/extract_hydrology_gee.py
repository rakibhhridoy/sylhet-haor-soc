import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Independent hydrology check (settles the "drying" question without optical NDWI).
ERA5-Land monthly reanalysis over the study basin, 1985-2025:
  - surface soil moisture (vol. layer 1) and root-zone 0-100 cm (depth-weighted L1-3)
  - annual total precipitation, annual mean 2 m air temperature, annual potential evaporation
Basin-mean per year via GEE. Output: REVISION/hydrology_era5_1985_2025.csv
"""
import ee, geopandas as gpd, pandas as pd
ee.Initialize(project="ee-arsenicbd")
# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
geom=ee.Geometry(gpd.read_file(f"{GIS}/StudyArea.shp").to_crs(4326).geometry.iloc[0].__geo_interface__)
col=ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
# root-zone 0-100cm depth-weighted soil water from layers 1-3 (7,21,72 cm)
def rootzone(img):
    return (img.select("volumetric_soil_water_layer_1").multiply(7)
            .add(img.select("volumetric_soil_water_layer_2").multiply(21))
            .add(img.select("volumetric_soil_water_layer_3").multiply(72)).divide(100).rename("sm_root"))

def per_year(y):
    y=ee.Number(y); yc=col.filter(ee.Filter.calendarRange(y,y,"year"))
    sm1=yc.select("volumetric_soil_water_layer_1").mean().rename("sm1")
    smr=yc.map(rootzone).mean()
    precip=yc.select("total_precipitation_sum").sum().multiply(1000).rename("precip_mm")  # m->mm annual
    t2m=yc.select("temperature_2m").mean().subtract(273.15).rename("t2m_C")
    pet=yc.select("potential_evaporation_sum").sum().multiply(1000).abs().rename("pet_mm")
    img=sm1.addBands(smr).addBands(precip).addBands(t2m).addBands(pet)
    d=img.reduceRegion(ee.Reducer.mean(), geom, 11132, bestEffort=True, maxPixels=int(1e9))
    return ee.Feature(None, ee.Dictionary(d).set("year", y))

rows=[]; yrs=list(range(1985,2026))
print("Extracting ERA5-Land basin hydrology in 6-year batches...")
for i in range(0,len(yrs),6):
    batch=yrs[i:i+6]
    feats=ee.FeatureCollection(ee.List(batch).map(per_year)).getInfo()["features"]
    for f in feats:
        p=f["properties"]; rows.append(p)
        fmt=lambda k: round(p[k],3) if p.get(k) is not None else None
        print(f"  {int(p['year'])}: sm1={fmt('sm1')} sm_root={fmt('sm_root')} precip={fmt('precip_mm')} t2m={fmt('t2m_C')} pet={fmt('pet_mm')}")
df=pd.DataFrame(rows).sort_values("year")
df=df[["year","sm1","sm_root","precip_mm","t2m_C","pet_mm"]]
df.to_csv(f"{DERIVED}/hydrology_era5_1985_2025.csv",index=False)
print("Saved REVISION/hydrology_era5_1985_2025.csv")
