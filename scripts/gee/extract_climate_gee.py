import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Sample WorldClim bioclim (MAT, MAP) at WoSIS Sylhet-class profile coords via GEE, for the
space-for-time test of the warming->SOC mechanism. bio01 = annual mean temperature (degC*10),
bio12 = annual precipitation (mm). Output: REVISION/wosis_class_climate.csv
"""
import ee, pandas as pd
ee.Initialize(project="ee-arsenicbd")
# [path set in paths.py] ROOT="/Volumes/SSD Rx/Research/SOC"
agg=pd.read_parquet(f"{DERIVED}/wosis_topsoil_0_30.parquet")
cls=agg[(agg.ph<6)&(agg.clay.between(30,75))].dropna(subset=["soc","clay"]).reset_index(drop=True)
print("profiles:",len(cls))
bio=ee.Image("WORLDCLIM/V1/BIO").select(["bio01","bio12"])
rows=[]; B=1000
for i in range(0,len(cls),B):
    sub=cls.iloc[i:i+B]
    fc=ee.FeatureCollection([ee.Feature(ee.Geometry.Point([float(r.lon),float(r.lat)]),{"pid":int(r.profile_id)}) for r in sub.itertuples()])
    s=bio.reduceRegions(collection=fc,reducer=ee.Reducer.first(),scale=1000).getInfo()
    for f in s["features"]:
        p=f["properties"]; rows.append({"profile_id":p["pid"],"mat":(p.get("bio01") or None),"map":p.get("bio12")})
    print(f"  {min(i+B,len(cls))}/{len(cls)}")
out=pd.DataFrame(rows)
out["mat"]=pd.to_numeric(out["mat"],errors="coerce")/10.0   # degC*10 -> degC
out["map"]=pd.to_numeric(out["map"],errors="coerce")
out.to_csv(f"{DERIVED}/wosis_class_climate.csv",index=False)
print("Saved. MAT range %.1f-%.1f C; MAP range %.0f-%.0f mm"%(out.mat.min(),out.mat.max(),out["map"].min(),out["map"].max()))
