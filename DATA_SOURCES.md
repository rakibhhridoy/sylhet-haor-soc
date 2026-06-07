# Data sources & provenance

The `data/` directory is archived on Zenodo: **https://doi.org/10.5281/zenodo.20579004**.

Every file in `data/` is documented below: what it is, where it came from, and (for derived
products) which script regenerates it. Large external datasets (multi-GB rasters, the full WoSIS
snapshot) are **not** redistributed here; their cached tabular derivatives are, so all reported
numbers reproduce offline.

## `data/field/` — primary field & laboratory data
| File | What | Origin |
|---|---|---|
| `TopSoil.csv` | 2025 topsoil measurements (9 sites) + cleaned 1985 baseline: SOC %, SOCiT, TN, clay, pH, CEC, SBD | Field sampling + lab analysis, Dept. of Soil, Water & Environment, University of Dhaka, 2025 |
| `PreviousTopSoil.csv` | 1985 reconnaissance topsoil values (pre-screening) | SRDI *Upazila Nirdeshika* (see below) |
| `MainData.xlsx` | Original laboratory workbook (audit trail; used for data-quality screening) | University of Dhaka |

CEC values in the original workbook had a decimal data-entry error (×10); corrected to
cmol_c kg⁻¹ in `TopSoil.csv`. SOC was determined by Walkley–Black with a 1.30 recovery factor.

## `data/geodata/` — derived spectral / LULC summary tables
| File | What | How produced |
|---|---|---|
| `indices_1985_2025.csv` | Annual Landsat NDVI/NDWI (the `mean_lst` column is corrupt — superseded by the dry-season LST below) | GEE export (Landsat C2 L2) |
| `ndvi_changes.csv` | Annual NDVI series (1988–2023) | GEE export |
| `biomass_ndvi.csv` | NDVI-derived biomass (Eq. 2) | derived |
| `biomass_agb.csv` | ESA CCI standing AGB, 2010–2021 | ESA CCI |
| `LULCAreaCover.csv` | Per-class LULC area (m²) by year, 2017–2024 | pixel counts from the Sentinel-2 classification |

## `data/gis/` — vector boundary
| File | What | Origin |
|---|---|---|
| `StudyArea.shp` (+ .shx/.dbf/.prj/.cpg) | ~12,300 km² study-area boundary polygon | Project GIS (LULC valid extent) |

## `data/derived/` — cached GEE / raster outputs (so numbers reproduce offline)
| File | What | Regenerate with |
|---|---|---|
| `dryseason_indices_combined.csv` (+ `_1988_2025`, `partial_1988_2020`) | Dry-season (Feb–Apr) NDVI/NDWI/water-fraction per year | `gee/extract_dryseason_gee.py`, `gee/_extract_2021_2025.py` + `local/03_analyze_dryseason.py` |
| `lst_real_1985_2025.csv` | Dry-season Landsat thermal LST per year | `gee/extract_lst_gee.py` |
| `hydrology_era5_1985_2025.csv` | ERA5-Land basin-mean annual soil moisture / precip / T / PET | `gee/extract_hydrology_gee.py` |
| `converging_hydrology.csv` | GLDAS-2.1 soil moisture & ET (2000–2025); GRACE/GRACE-FO TWS (2003–2016) | `gee/converging_hydrology_gee.py` |
| `wosis_topsoil_0_30.parquet` | WoSIS profiles depth-weighted to 0–30 cm topsoil | `wosis/wosis_validation.py` (needs WoSIS snapshot) |
| `wosis_class_climate.csv` | WorldClim MAT/MAP joined to each profile | `gee/extract_climate_gee.py` |
| `wosis_class_landcover.csv` | Copernicus CGLS-LC100 (2019) class at each profile | `gee/sample_landcover_gee.py` |
| `lulc_composition_2017_2024.csv` | Per-year 8-class composition (% of always-valid area) | `raster/diagnose_lulc_consistency.py` (needs rasters) |
| `buffer_lulc_per_site.csv` | Per-site 500 m buffer LULC change | `raster/make_buffer_table.py` (needs rasters) |
| `accuracy_points_2024.csv` / `.geojson` | 285 labelled accuracy reference points | `raster/accuracy_step1_generate_points.py` (needs LULC2024 raster) |

## External datasets (NOT redistributed — obtain from source)
| Dataset | Use | Source / DOI |
|---|---|---|
| Landsat Collection-2 L2 (5/7/8/9) | dry-season NDVI/NDWI/LST 1988–2025 | USGS via GEE `LANDSAT/*/C02/T1_L2` |
| Sentinel-2 MSI | LULC classification 2017–2024 | ESA via GEE `COPERNICUS/S2` |
| ERA5-Land monthly | hydrology 1985–2025 | Muñoz-Sabater 2021, *ESSD* 13:4349, doi:10.5194/essd-13-4349-2021; GEE `ECMWF/ERA5_LAND/MONTHLY_AGGR` |
| GLDAS-2.1 NOAH | hydrology 2000–2025 | Rodell et al. 2004, *BAMS* 85:381, doi:10.1175/BAMS-85-3-381; GEE `NASA/GLDAS/V021/NOAH/G025/T3H` |
| GRACE / GRACE-FO mascons | terrestrial water storage 2003–2016 | Tapley et al. 2004, *Science* 305:503, doi:10.1126/science.1099192; GEE `NASA/GRACE/MASS_GRIDS/MASCON` |
| WorldClim v1 BIO | MAT/MAP for space-for-time | Hijmans et al. 2005, *Int. J. Climatol.* 25:1965, doi:10.1002/joc.1276; GEE `WORLDCLIM/V1/BIO` |
| Copernicus CGLS-LC100 (2019) | land-cover subsets of WoSIS class | Buchhorn et al. 2020, *Remote Sensing* 12:1044, doi:10.3390/rs12061044 |
| WoSIS soil profiles | external SOC benchmark | Batjes et al. 2020, *ESSD* 12:299, doi:10.5194/essd-12-299-2020 (ISRIC) |
| ESA CCI Above-Ground Biomass | biomass cross-check 2010–2021 | ESA CCI Biomass |
| SRDI *Upazila Nirdeshika* | 1985 historical soil baseline | Soil Resource Development Institute, Bangladesh |
| Classified LULC rasters `LULC{2017..2024}c.tif` (~6.5 GB) | per-site buffers, spatial-coherence, Figs 1/6 | Project Sentinel-2 Random Forest classification (available from the corresponding author) |

## Notes
- `indices_1985_2025.csv` annual means are water-fraction-confounded (NDVI~NDWI r=−0.89); the
  analysis therefore uses **dry-season** composites (`data/derived/dryseason_*`).
- The biomass equation (Eq. 2) is Meshesha et al. 2020 (*Heliyon*), valid on dry-season NDVI
  (0.47–0.63), not on annual-mean NDVI.
