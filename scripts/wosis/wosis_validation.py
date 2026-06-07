import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import ROOT, FIELD, GEODATA, GIS, DERIVED, RESULTS  # noqa: E402,F401

"""
Strengthen the Sylhet SOC paper with WoSIS global soil profiles + Copernicus land cover.
1. Aggregate WoSIS to depth-weighted 0-30 cm topsoil per profile (match Sylhet sampling).
2. Sample Copernicus CGLS-LC100 (2019) class at each profile -> TRUE land-cover flags
   (90=herbaceous wetland, 40=cultivated) instead of only a soil-class proxy.
3. Layered clay-SOC & pH-SOC effect sizes: GLOBAL -> S/SE Asia -> Bengal, crossed with
   all-soils / herbaceous-wetland / cultivated / acidic-clay-rich analog.
4. Place the 9 Sylhet sites in the regional & wetland SOC distributions.
Outputs: REVISION/wosis_topsoil_0_30.parquet, REVISION/wosis_validation_results.md
"""
import pandas as pd, numpy as np, rasterio
from scipy import stats
PED="/Volumes/SSD Ex/PEDOFLUX_data"
LC=f"{PED}/raw/copernicus_lulc/2019/PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif"
OUTP=f"{DERIVED}/wosis_topsoil_0_30.parquet"
OUTMD=f"{RESULTS}/wosis_validation_results.md"

df=pd.read_parquet(f"{PED}/processed/pedoflux_profiles.parquet")
# clip each horizon to 0-30 cm and depth-weight
h=df[df.depth_top_cm<30].copy()
h["bot"]=h.depth_bot_cm.clip(upper=30); h["top"]=h.depth_top_cm.clip(lower=0)
h["w"]=(h.bot-h.top).clip(lower=0)
h=h[h.w>0]
def wavg(g,c):
    m=g[c].notna()
    return np.average(g.loc[m,c],weights=g.loc[m,"w"]) if m.any() and g.loc[m,"w"].sum()>0 else np.nan
agg=h.groupby("profile_id").apply(lambda g: pd.Series({
    "soc":wavg(g,"soc"),"clay":wavg(g,"clay"),"sand":wavg(g,"sand"),"ph":wavg(g,"ph"),
    "bd":wavg(g,"bd"),"cec":wavg(g,"cec"),"n_total":wavg(g,"n_total"),
    "lon":g.lon.iloc[0],"lat":g.lat.iloc[0]})).reset_index()
agg=agg.dropna(subset=["soc","clay","lon","lat"])
agg.to_parquet(OUTP)   # save first, regardless of land-cover step
print("aggregated 0-30cm profiles:",len(agg))

# sample land cover at each profile (graceful if raster unreadable)
agg["lc"]=np.nan
try:
    with rasterio.open(LC) as src:
        vals=list(src.sample([(x,y) for x,y in zip(agg.lon,agg.lat)]))
    agg["lc"]=[int(v[0]) for v in vals]
    agg.to_parquet(OUTP)
    print("LC sampled. class counts (top):",agg.lc.value_counts().head(8).to_dict())
except Exception as e:
    print("LC sampling SKIPPED (raster unreadable):",str(e)[:80])

def partial_clay_soc_given_ph(d):
    # Spearman partial corr of clay~soc controlling for ph (rank-based)
    d=d.dropna(subset=["clay","soc","ph"])
    if len(d)<30: return np.nan
    import numpy as _np
    R=d[["clay","soc","ph"]].rank()
    c=_np.corrcoef(R.values,rowvar=False)
    rcs,rcp,rsp=c[0,1],c[0,2],c[1,2]
    denom=_np.sqrt((1-rcp**2)*(1-rsp**2))
    return (rcs-rcp*rsp)/denom if denom>0 else _np.nan

def es(d):
    d=d.dropna(subset=["clay","soc"])
    if len(d)<30: return f"n={len(d)} (too few)"
    rc,pc=stats.spearmanr(d.clay,d.soc)
    dp=d.dropna(subset=["ph"]); rp,_=stats.spearmanr(dp.ph,dp.soc) if len(dp)>=30 else (np.nan,1)
    pr=partial_clay_soc_given_ph(d)
    return f"n={len(d):6d} | clay-SOC rho={rc:+.2f} (p={pc:.0e}) | clay-SOC|pH={pr:+.2f} | pH-SOC rho={rp:+.2f}"

regions={"GLOBAL":agg,
 "S/SE Asia":agg[(agg.lon.between(60,110))&(agg.lat.between(5,35))],
 "Bengal":agg[(agg.lon.between(87,93))&(agg.lat.between(21,27))]}
subsets={"all soils":lambda d:d,
 "herbaceous wetland (LC=90)":lambda d:d[d.lc==90],
 "cultivated (LC=40)":lambda d:d[d.lc==40],
 "acidic clay-rich (pH<6,clay>30)":lambda d:d[(d.ph<6)&(d.clay>30)]}
out=["# WoSIS external validation (depth-weighted 0-30 cm topsoil) — layered\n",
     "Spearman effect sizes; at large n the message is effect SIZE (weak), not significance.\n"]
for rn,rd in regions.items():
    out.append(f"\n## {rn}")
    for sn,fn in subsets.items():
        out.append(f"- {sn:34s}: {es(fn(rd))}")

# Sylhet context
syl=np.array([2.63,0.96,1.10,1.32,1.22,0.64,1.03,1.42,1.14])*10  # g/kg
wet=agg[(agg.lc==90)&(agg.lon.between(60,110))&(agg.lat.between(5,35))].soc
beng=regions["Bengal"].soc
out.append("\n## Sylhet placement (topsoil SOC, g/kg)")
out.append(f"- Sylhet mean={syl.mean():.1f}, median={np.median(syl):.1f}")
out.append(f"- Bengal WoSIS median={beng.median():.1f} (n={len(beng)}); Sylhet-mean percentile={100*(beng<syl.mean()).mean():.0f}")
if len(wet)>=10:
    out.append(f"- Asian herbaceous-wetland WoSIS median={wet.median():.1f} (n={len(wet)}); Sylhet-mean percentile={100*(wet<syl.mean()).mean():.0f}")
txt="\n".join(out); open(OUTMD,"w").write(txt); print("\n"+txt)
