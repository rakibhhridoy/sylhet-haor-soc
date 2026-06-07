import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Diagnose LULC temporal consistency (is the 2017-2024 change analysis trustworthy?).
Tests: (1) per-year class composition; (2) class-set presence/absence across years
(a single consistent model -> same classes every year); (3) year-to-year GROSS churn vs
NET change (high gross/low net => seasonal or classifier instability, not land-use change);
(4) spatial coherence of change (salt-and-pepper => classifier noise).
Uses stride subsampling for speed (proportions are unbiased).
"""
import numpy as np, rasterio, pandas as pd
# [path set in paths.py] ROOT = "/Volumes/SSD Rx/Research/SOC"; GIS = f"{ROOT}/gis"
YEARS = list(range(2017, 2025))
STEP = 8
NAMES = {0:"nodata",1:"Water",2:"Veg",4:"Flood",5:"Wetland",7:"Urban",8:"Bare",10:"Cls10",11:"FloodVeg"}

arrs = {}
for y in YEARS:
    with rasterio.open(f"{GIS}/LULC{y}c.tif") as s:
        arrs[y] = s.read(1)[::STEP, ::STEP]
shape = arrs[YEARS[0]].shape
valid = np.ones(shape, bool)
for y in YEARS: valid &= (arrs[y] != 0)   # pixels valid in all years
nv = valid.sum()
print(f"grid {shape}, pixels valid in ALL years: {nv}\n")

# (1)(2) per-year class % and class-set
codes = sorted(NAMES)
rows = {}
for y in YEARS:
    a = arrs[y][valid]
    rows[y] = {NAMES[c]: 100*np.mean(a==c) for c in codes if c!=0}
comp = pd.DataFrame(rows).T
print("=== Per-year class composition (% of always-valid area) ===")
print(comp.round(1).to_string())
print("\n=== Class PRESENCE per year (any pixels?) -> inconsistency = per-year independent models ===")
pres = pd.DataFrame({y:{NAMES[c]:int((arrs[y]==c).any()) for c in codes if c!=0} for y in YEARS}).T
print(pres.to_string())

# (3) gross churn vs net change between consecutive years
print("\n=== Consecutive-year change: GROSS churn vs |NET| compositional change ===")
print("year_pair | gross_%_pixels_changing_class | net_%_(sum of |Δclass share|)/2")
for y0,y1 in zip(YEARS[:-1], YEARS[1:]):
    a0,a1 = arrs[y0][valid], arrs[y1][valid]
    gross = 100*np.mean(a0!=a1)
    net = (comp.loc[y1]-comp.loc[y0]).abs().sum()/2
    print(f"  {y0}->{y1} | gross={gross:5.1f}% | net={net:5.1f}%  (gross/net={gross/net:.1f}x)" if net>0 else f"  {y0}->{y1} | gross={gross:.1f}% | net~0")

# (4) spatial coherence of change 2017->2024 (salt-and-pepper test)
a0 = arrs[2017]; a1 = arrs[2024]; chg = (a0!=a1) & valid
# fraction of changed pixels whose 4-neighbours are ALSO changed (coherent) vs isolated
ch = chg.astype(np.uint8)
neigh = np.zeros_like(ch);
neigh[1:,:]+=ch[:-1,:]; neigh[:-1,:]+=ch[1:,:]; neigh[:,1:]+=ch[:,:-1]; neigh[:,:-1]+=ch[:,1:]
isolated = ((ch==1)&(neigh==0)).sum(); total_ch = ch.sum()
print(f"\n=== Spatial coherence of 2017->2024 change ===")
print(f"changed pixels: {100*total_ch/nv:.1f}% of area; of those, {100*isolated/total_ch:.1f}% are ISOLATED (no changed neighbour)")
print("(high isolated fraction => salt-and-pepper classifier noise rather than coherent land-use change)")
