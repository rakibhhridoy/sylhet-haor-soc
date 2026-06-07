import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Sample Copernicus CGLS-LC100 (2019) land cover at WoSIS Sylhet-class profile coordinates,
via GEE (the corrupt local tif is bypassed). Builds a TRUE land-cover flag so we can isolate
herbaceous-wetland (class 90) and cultivated (40) profiles within the Sylhet soil class.
Output: REVISION/wosis_class_landcover.csv  (profile_id, lon, lat, lc)
"""
import ee, pandas as pd, numpy as np
ee.Initialize(project="ee-arsenicbd")
# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
agg=pd.read_parquet(f"{DERIVED}/wosis_topsoil_0_30.parquet")
cls=agg[(agg.ph<6)&(agg.clay.between(30,75))].dropna(subset=["soc","clay"]).reset_index(drop=True)
print("Sylhet-class profiles to sample:",len(cls))

lc=(ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V-C3/Global")
    .select("discrete_classification").filterDate("2019-01-01","2019-12-31").first())

rows=[]
B=1000
for i in range(0,len(cls),B):
    sub=cls.iloc[i:i+B]
    fc=ee.FeatureCollection([ee.Feature(ee.Geometry.Point([float(r.lon),float(r.lat)]),
                                         {"pid":int(r.profile_id)}) for r in sub.itertuples()])
    samp=lc.reduceRegions(collection=fc, reducer=ee.Reducer.first(), scale=100).getInfo()
    for f in samp["features"]:
        p=f["properties"]; rows.append({"profile_id":p["pid"],"lc":p.get("first")})
    print(f"  sampled {min(i+B,len(cls))}/{len(cls)}")

out=pd.DataFrame(rows)
out=out.merge(cls[["profile_id","lon","lat"]],on="profile_id",how="left")
out.to_csv(f"{DERIVED}/wosis_class_landcover.csv",index=False)
print("Saved. LC class counts:",out.lc.value_counts().head(10).to_dict())
print("herbaceous wetland (90):",(out.lc==90).sum(),"| cultivated (40):",(out.lc==40).sum())
