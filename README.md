# Soil Organic Carbon under Warming, Drying and Agricultural Intensification in the Sylhet Haors — reproducibility package

Code and data to reproduce **every value, table and figure** in the manuscript
*"Soil Organic Carbon under Warming, Drying and Agricultural Intensification: Integrating Field
Sampling, Multi-decadal Remote Sensing and Reanalysis in the Sylhet Haors, Bangladesh"*
(submitted to the *Journal of Environmental Management*).

The study combines 2025 field soil sampling at nine haor wetlands with a cleaned 1985 SRDI
reconnaissance baseline, multi-decadal dry-season Landsat indices, Sentinel-2 LULC, ERA5-Land /
GLDAS / GRACE hydrological reanalysis, and an external WoSIS soil-profile benchmark.

## How this package is hosted

| Part | Where | Contents |
|---|---|---|
| **Code** | GitHub repository | `scripts/`, `manuscript/`, `paths.py`, `*.md`, `requirements.txt`, `environment.yml`, `run_all.sh` |
| **Data** | Zenodo archive (DOI: `TODO`) | the `data/` directory |

To reproduce: clone the GitHub repo, download the Zenodo archive, and unzip it so that the
`data/` folder sits in the repo root next to `paths.py`. All scripts resolve their paths through
`paths.py`, so nothing else needs editing.

```
Reproducible_JEM/
├── paths.py              # single source of truth for all paths
├── requirements.txt / environment.yml
├── run_all.sh            # reproduces every offline number + figure
├── README.md  VALUE_MAP.md  DATA_SOURCES.md
├── scripts/              # ── GitHub ──
│   ├── local/            # offline analyses (reproduce the numbers; run by run_all.sh)
│   ├── figures/          # figure scripts (run by run_all.sh)
│   ├── raster/           # need the 6.5 GB classified rasters (provenance; outputs cached)
│   ├── gee/              # Google Earth Engine extraction (provenance; outputs cached)
│   └── wosis/            # WoSIS 0–30 cm aggregation (needs external WoSIS snapshot)
├── manuscript/           # ── GitHub ── Manuscript.tex, references.bib, Fig*.png, cover letter
├── data/                 # ── Zenodo ──
│   ├── field/            # 2025 field soil, 1985 baseline, lab workbook
│   ├── geodata/          # spectral-index & LULC-area CSVs
│   ├── gis/              # study-area boundary shapefile
│   └── derived/          # cached GEE / raster outputs so all numbers reproduce offline
└── results/              # created on run: regenerated tables (*.md) + figures (*.png)
```

## Quick start

```bash
# 1. environment (conda or pip)
conda env create -f environment.yml && conda activate sylhet-soc
#   or:  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 2. make sure data/ (from Zenodo) sits next to paths.py, then:
bash run_all.sh
```

This runs entirely offline (no Earth Engine, no large rasters) and writes the regenerated
statistics (`results/*.md`) and figures (`results/*.png`). Each statistics file is paste-ready
and matches the corresponding manuscript values.

## Where each manuscript number comes from

See **`VALUE_MAP.md`** — a table mapping every reported quantity (correlations, p-values, trends,
percentages, accuracy, regression coefficients, figure panels) to the exact script and data file
that produces it.

## Reproducibility tiers

- **Offline (default, `run_all.sh`)** — reproduces all reported statistics, tables and most
  figures from `data/` alone. This is the complete claim-bearing set.
- **Raster tier (`scripts/raster/`)** — the per-site buffer table, the LULC spatial-coherence
  diagnostic, and Figs 1/6 need the 6.5 GB classified Sentinel-2 / index rasters, which are too
  large to redistribute. Their **tabular outputs are cached** in `data/derived/`, so the numbers
  still reproduce offline; the scripts are included for provenance. See `DATA_SOURCES.md` for how
  to obtain/regenerate the rasters.
- **Earth Engine tier (`scripts/gee/`)** — the dry-season composites, LST, ERA5/GLDAS/GRACE
  hydrology, WorldClim and Copernicus land-cover samples were extracted in Google Earth Engine.
  Their outputs are cached in `data/derived/`. To regenerate, install `earthengine-api`, run
  `earthengine authenticate`, and edit the `ee.Initialize(project=...)` line to your own GEE
  project.

## Known discrepancies (full disclosure)

- **Soil-moisture Sen slope units.** The manuscript prints the ERA5-Land root-zone soil-moisture
  trend as `−0.033 m³ m⁻³ decade⁻¹`; `scripts/local/04_analyze_hydrology.py` computes
  `−0.0033 m³ m⁻³ decade⁻¹` (the significance, p≈0.02, and the ≈−6 % total change over the record
  are unaffected). This looks like a 10× typo in the manuscript text and should be corrected to
  `−0.0033` at proof stage.
- **Water endpoint decline.** The text's `−43.5 %` open-water change is the area (m²) computation
  in `01_recompute_numbers.py` (`data/geodata/LULCAreaCover.csv`); `05_lulc_area_stats.py` reports
  `−43.8 %` from the percent-of-valid-pixels composition. The small difference is the denominator
  (total area vs. always-valid pixels); both are documented.

## Packaging for upload

This folder is already split so the two halves go to the two hosts. Build clean artifacts
(no macOS `._*` sidecars) like so:

```bash
# --- GitHub (code) ---  from inside Reproducible_JEM/
git init && git add . && git commit -m "Reproducibility package"   # data/ and results/ are .gitignored
# git remote add origin <your repo> && git push -u origin main

# --- Zenodo (data) ---  build a clean zip of just data/
export COPYFILE_DISABLE=1          # stop macOS adding ._ files into the zip
zip -r -X sylhet_haor_soc_data.zip data        # ~6 MB
```

After minting the Zenodo DOI, paste it into `README.md` ("DOI: TODO") and the `## Citation`
section before pushing to GitHub.

## Citation

If you use this code or data, please cite the article (once assigned) and the Zenodo data
archive (DOI above). External datasets retain their own citations — see `DATA_SOURCES.md`.

## License

- Code (`scripts/`): MIT (see `LICENSE`, to be added).
- Data (`data/`) and manuscript text/figures: CC-BY-4.0 unless a source dataset specifies
  otherwise (see `DATA_SOURCES.md`).
