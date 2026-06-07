# Value map — every manuscript number to its script and data

Each row links a quantity reported in the manuscript (not distributed here) to the script that
computes it and the data file it reads. Unless noted, scripts run **offline** from `data/` (no Google
Earth Engine, no rasters) via `run_all.sh`, and write to `results/`. Verified to match the
manuscript on Python 3.11 with the pinned `requirements.txt`.

Legend: **L** = local/offline (in `run_all.sh`); **R** = needs the 6.5 GB rasters (provenance,
cached output shipped); **G** = needs Google Earth Engine (provenance, cached output shipped).

## Present-day soil geochemistry (2025) — Section 3.1, Fig 2, Fig 9, Table 2 (PCA)
| Value (manuscript) | Script | Reads | Type |
|---|---|---|---|
| SOC 0.64–2.63 %, SOCiT 30.7–122.7 Mg/ha | `local/01_recompute_numbers.py`, `figures/make_fig2.py`, `figures/make_fig3.py` | `data/field/TopSoil.csv` | L |
| Clay–SOC r=0.04, p=0.93 (and all stock metrics \|r\|≤0.21) | `local/01_recompute_numbers.py` | `data/field/TopSoil.csv` | L |
| TN–SOC r=0.82, p=0.006; pH–SOC r=−0.52, p=0.16 | `local/01_recompute_numbers.py` | `data/field/TopSoil.csv` | L |
| CEC–clay r=0.93; SBD–clay r=−0.72, p=0.028; CEC 16.7–32.5 | `local/01_recompute_numbers.py` | `data/field/TopSoil.csv` | L |
| PCA PC1 52.9 %, PC2 34.5 %, eigenvalues, loadings (Table 2) | `local/01_recompute_numbers.py`, `figures/make_fig9.py` | `data/field/TopSoil.csv` | L |

## Historical (1985) baseline & long-term change — Section 2.3 / 3.2
| Value | Script | Reads | Type |
|---|---|---|---|
| Paired t p=0.15; Wilcoxon p=0.20; 6 down / 3 up | `local/01_recompute_numbers.py` | `data/field/TopSoil.csv` | L |
| Mean change −48 %; −16 % excluding Hakaluki & Sarail | `local/01_recompute_numbers.py` | `data/field/TopSoil.csv` | L |
| Impossible/flagged 1985 values (pH 0; SBD>2.65; peat SOC 7.01/4.30 %) | `local/02_flag_data_quality.py` | `data/field/MainData.xlsx`, `PreviousTopSoil.csv` | L |

## LULC 2017–2024 — Section 3.3, Figs 5–6, Table 3 (buffers), Table 1 (accuracy)
| Value | Script | Reads | Type |
|---|---|---|---|
| Water −43.5 %, Veg −21.8 %, Urban +76.5 % (m², OLS/Spearman p) | `local/01_recompute_numbers.py` | `data/geodata/LULCAreaCover.csv` | L |
| Built-up 7.2→12.7 % (+76 %); +41 % excl. 2017; Veg 9.1→7.1 % | `local/05_lulc_area_stats.py` | `data/derived/lulc_composition_2017_2024.csv` | L |
| Open water 12.4–33.6 % (2.7-fold); footprint 78.7±1.0 % CV 1.3 %; +flood 80.6±1.1 % CV 1.4 % | `local/05_lulc_area_stats.py` | `data/derived/lulc_composition_2017_2024.csv` | L |
| Changed pixels 28.4 %; 5.2 % isolated | `raster/diagnose_lulc_consistency.py` → cached in `lulc_composition_2017_2024.csv` header note | `gis/LULC2017–2024c.tif` | R |
| Per-site 500 m buffer change, Table 3 | `raster/make_buffer_table.py` → `data/derived/buffer_lulc_per_site.csv` | `gis/LULC*c.tif` | R |
| Confusion matrix (Table 1); OA 56.8 %, κ 0.50; Urban UA 95 %, Veg UA 98 % | `local/08_lulc_accuracy.py` | `data/derived/accuracy_points_2024.csv` | L |
| Aggregated (hydromorphic merged) OA 83.2 %, κ 0.74 | `local/08_lulc_accuracy.py` | `data/derived/accuracy_points_2024.csv` | L |
| 285 reference points generated | `raster/accuracy_step1_generate_points.py` → `accuracy_points_2024.csv/.geojson` | `gis/LULC2024c.tif` | R |

## Multi-decadal warming / greening (dry-season, 1988–2025) — Section 3.5, Figs 7–8, 11
| Value | Script | Reads | Type |
|---|---|---|---|
| Dry-season NDVI 0.47→0.57, MK p<0.001, Sen +0.031/dec (+22 %) | `local/03_analyze_dryseason.py`, `figures/make_fig7.py` | `data/derived/dryseason_indices_combined.csv` | L |
| Dry-season LST 26.3→27.6 °C, MK p=0.015, +0.55/dec (annual +0.66/dec) | `local/03_analyze_dryseason.py`, `figures/make_fig7.py` | `data/derived/dryseason_indices_combined.csv`, `lst_real_1985_2025.csv` | L |
| Dry-season NDWI mirrors NDVI r=−0.97; annual NDVI~NDWI r=−0.89 | `local/03_analyze_dryseason.py`, `local/01_recompute_numbers.py` | `dryseason_indices_combined.csv`, `geodata/indices_1985_2025.csv` | L |
| Biomass ≈1.0→1.7 t/ha/yr, OLS p<0.001 (Eq. 2) | `figures/make_fig8.py` | `data/derived/dryseason_indices_combined.csv` | L |
| ESA CCI AGB 20.8–30.4 Mg/ha (2010–2021) | `local/01_recompute_numbers.py` | `data/geodata/biomass_agb.csv` | L |
| Dry-season composite extraction (NDVI/NDWI/LST) | `gee/extract_dryseason_gee.py`, `_extract_2021_2025.py`, `extract_lst_gee.py` | GEE Landsat C2 L2 | G |
| Fig 11 decadal NDVI/NDWI maps | (decadal raster composites) | GEE / `gis` rasters | R/G |

## Independent hydrology (drying) — Section 3.5, Fig 14
| Value | Script | Reads | Type |
|---|---|---|---|
| ERA5 root-zone soil moisture MK p=0.021 (Sen −0.0033/dec)¹; precip −161 mm/dec p=0.017; air T +0.18 °C/dec p<0.001 | `local/04_analyze_hydrology.py`, `figures/make_fig14_converging.py` | `data/derived/hydrology_era5_1985_2025.csv` | L |
| GLDAS-2.1 soil moisture MK p=0.014; ET p<0.001; GRACE TWS p=0.66 | `figures/make_fig14_converging.py` | `data/derived/converging_hydrology.csv` | L |
| ERA5 / GLDAS / GRACE extraction | `gee/extract_hydrology_gee.py`, `converging_hydrology_gee.py` | GEE | G |

¹ The manuscript abstract/Section 3.5 print the soil-moisture Sen slope as “−0.033 m³ m⁻³ decade⁻¹”; the script computes **−0.0033** (a likely 10× typo in the text — see README “Known discrepancies”).

## SOC controls — external benchmarking (WoSIS) — Section 3.7, Figs 12–13
| Value | Script | Reads | Type |
|---|---|---|---|
| Sylhet-class n=9,676; clay–SOC ρ=0.12, partial\|N ρ=0.01; SOC–N ρ=0.81 | `local/06_sylhet_class_analysis.py`, `figures/make_fig_wosis.py` | `data/derived/wosis_topsoil_0_30.parquet` | L |
| Cultivated/paddy n=2,425 (ρ=0.07, partial 0.02); herbaceous wetland n=96 (ρ=0.29→0.06) | `local/06_sylhet_class_analysis.py`, `figures/make_fig_wosis.py` | `wosis_topsoil_0_30.parquet`, `wosis_class_landcover.csv` | L |
| All-soils clay–SOC ρ=0.25; Sylhet ~31st percentile of paddy | `local/06_sylhet_class_analysis.py` | `wosis_topsoil_0_30.parquet` | L |
| Space-for-time βMAT −0.38 (global) → −0.11 (warm&wet n=2,947); βN +0.47 | `local/07_regional_space_for_time.py`, `figures/make_fig13_v2.py` | `wosis_topsoil_0_30.parquet`, `wosis_class_climate.csv` | L |
| WoSIS 0–30 cm aggregation (build of the parquet) | `wosis/wosis_validation.py` | external WoSIS/PEDOFLUX snapshot | (ext) |
| WorldClim MAT/MAP join; Copernicus land-cover sampling | `gee/extract_climate_gee.py`, `sample_landcover_gee.py` | GEE | G |

## Figures index
| Figure | Script | Type |
|---|---|---|
| Fig 1 study area | `raster/make_fig1.py` (DEM + extra shapefiles) | R |
| Fig 2 soil properties | `figures/make_fig2.py` | L |
| Fig 3 SOCiT IDW map | `figures/make_fig3.py` | L |
| Fig 5 LULC composition | `figures/make_fig5.py` | L |
| Fig 6 annual LULC maps | `raster/make_fig6.py` | R |
| Fig 7 dry-season indices | `figures/make_fig7.py` | L |
| Fig 8 biomass | `figures/make_fig8.py` | L |
| Fig 9 PCA & correlations | `figures/make_fig9.py` | L |
| Fig 11 decadal indices | raster composites | R/G |
| Fig 12 WoSIS benchmark | `figures/make_fig_wosis.py` | L |
| Fig 13 climate–SOC | `figures/make_fig13_v2.py` | L |
| Fig 14 converging hydrology | `figures/make_fig14_converging.py` | L |
