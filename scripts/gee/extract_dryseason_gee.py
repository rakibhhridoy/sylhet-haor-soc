import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
DRY-SEASON re-extraction to break the annual-mean water-fraction confound (audit N3/N4).
For each year 1988-2025, build a Feb-Apr (pre-monsoon, peak-Boro / min-flood) median composite
over the VERIFIED StudyArea polygon, and compute basin-mean:
  - NDVI            (NIR-Red)/(NIR+Red)
  - NDWI  McFeeters (Green-NIR)/(Green+NIR)
  - LST   (C)       Landsat C2 L2 thermal
  - NDVI_land       NDVI averaged over LAND only (NDWI<0), i.e. water-masked vegetation signal
  - water_frac      fraction of valid pixels with NDWI>=0 (to show we've controlled it)
Harmonised across Landsat 5/7/8/9. Proven 3-year-batch server-side pattern (avoids memory limit).
Output: REVISION/dryseason_indices_1988_2025.csv
"""
import ee, geopandas as gpd, pandas as pd
PROJECT="ee-arsenicbd"
SHP=f"{GIS}/StudyArea.shp"
OUT=f"{DERIVED}/dryseason_indices_1988_2025.csv"
DRY_START,DRY_END="-02-01","-04-30"      # pre-monsoon dry / peak Boro
ee.Initialize(project=PROJECT)
geom=ee.Geometry(gpd.read_file(SHP).to_crs(4326).geometry.iloc[0].__geo_interface__)

def harmonise(img, b):  # b = dict of band roles -> band names
    sr=lambda n: img.select(n).multiply(0.0000275).add(-0.2)
    red,green,nir = sr(b['red']),sr(b['green']),sr(b['nir'])
    ndvi=nir.subtract(red).divide(nir.add(red)).rename('NDVI')
    ndwi=green.subtract(nir).divide(green.add(nir)).rename('NDWI')
    lst=img.select(b['th']).multiply(0.00341802).add(149.0-273.15).rename('LST')
    qa=img.select('QA_PIXEL'); mask=qa.bitwiseAnd(1<<3).eq(0).And(qa.bitwiseAnd(1<<4).eq(0))
    return (ndvi.addBands(ndwi).addBands(lst).updateMask(mask)
            .set('yr',ee.Image(img).date().get('year')))

L57={'red':'SR_B3','green':'SR_B2','nir':'SR_B4','th':'ST_B6'}
L89={'red':'SR_B4','green':'SR_B3','nir':'SR_B5','th':'ST_B10'}
def coll(cid,b):
    # filter date window (Feb-Apr) on RAW collection (still has timestamps) BEFORE harmonising
    return (ee.ImageCollection(cid).filterBounds(geom).filter(ee.Filter.lt('CLOUD_COVER',60))
            .filter(ee.Filter.calendarRange(2,4,'month'))
            .map(lambda im: harmonise(im,b)))
merged=(coll("LANDSAT/LT05/C02/T1_L2",L57).merge(coll("LANDSAT/LE07/C02/T1_L2",L57))
        .merge(coll("LANDSAT/LC08/C02/T1_L2",L89)).merge(coll("LANDSAT/LC09/C02/T1_L2",L89)))

def per_year(y):
    y=ee.Number(y)
    yc=merged.filter(ee.Filter.eq('yr',y))   # filter by the 'yr' property (post-harmonise; no timestamp)
    comp=yc.median()
    ndvi=comp.select('NDVI'); ndwi=comp.select('NDWI'); lst=comp.select('LST')
    land=ndwi.lt(0)                      # land = non-water
    ndvi_land=ndvi.updateMask(land)
    d=ee.Dictionary(comp.reduceRegion(ee.Reducer.mean(),geom,100,bestEffort=True,maxPixels=int(1e9),tileScale=4))
    wfrac=ee.Dictionary(ndwi.gte(0).reduceRegion(ee.Reducer.mean(),geom,100,bestEffort=True,maxPixels=int(1e9),tileScale=4))
    dl=ee.Dictionary(ndvi_land.reduceRegion(ee.Reducer.mean(),geom,100,bestEffort=True,maxPixels=int(1e9),tileScale=4))
    return ee.Feature(None,{'year':y,'ndvi':d.get('NDVI',-9999),'ndwi':d.get('NDWI',-9999),
        'lst_C':d.get('LST',-9999),'ndvi_land':dl.get('NDVI',-9999),'water_frac':wfrac.get('NDWI',-9999),
        'n_images':yc.size()})

rows=[]
yrs=list(range(1988,2026))
print("Extracting dry-season (Feb-Apr) composites in 3-year batches...")
for i in range(0,len(yrs),3):
    batch=yrs[i:i+3]
    feats=ee.FeatureCollection(ee.List(batch).map(per_year)).getInfo()['features']
    for f in feats:
        p=f['properties']; rows.append(p)
        fmt=lambda k: 'NA' if p.get(k) in (None,-9999) else round(p[k],3)
        print(f"  {int(p['year'])}: NDVI={fmt('ndvi')} NDVI_land={fmt('ndvi_land')} NDWI={fmt('ndwi')} "
              f"LST={fmt('lst_C')} waterfrac={fmt('water_frac')} n={p['n_images']}")

df=pd.DataFrame(rows).sort_values('year')
for c in ['ndvi','ndwi','lst_C','ndvi_land','water_frac']:
    df[c]=pd.to_numeric(df[c],errors='coerce').replace(-9999,pd.NA)
df=df[['year','ndvi','ndvi_land','ndwi','lst_C','water_frac','n_images']]
df.to_csv(OUT,index=False)
print(f"\nSaved {OUT}")
print(df.to_string(index=False))
