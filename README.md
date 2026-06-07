# Soil Organic Carbon Dynamics in the Tropical Sylhet Haor Wetlands of Bangladesh — reproducibility package

Code and data to reproduce **every value, table and figure** in the manuscript
*"Soil Organic Carbon Dynamics in the Tropical Sylhet Haor Wetlands of Bangladesh"*
(submitted to the *Journal of Environmental Management*).

The study combines 2025 field soil sampling at nine haor wetlands with a cleaned 1985 SRDI
reconnaissance baseline, multi-decadal dry-season Landsat indices, Sentinel-2 LULC, ERA5-Land /
GLDAS / GRACE hydrological reanalysis, and an external WoSIS soil-profile benchmark.

## How this package is hosted

| Part | Where | Contents |
|---|---|---|
| **Code** | GitHub repository | `scripts/`, `paths.py`, `*.md`, `requirements.txt`, `environment.yml`, `run_all.sh` |
| **Data** | Zenodo archive ([10.5281/zenodo.20579004](https://doi.org/10.5281/zenodo.20579004)) | the `data/` directory |

To reproduce: clone the GitHub repo, download the Zenodo archive, and unzip it so that the
`data/` folder sits in the repo root next to `paths.py`. All scripts resolve their paths through
`paths.py`, so nothing else needs editing.

> **Note.** The manuscript text, figures and cover letter are **not** included in this public
> package; they are available through the journal or from the corresponding author on request.
> This repository provides only the code (and, via Zenodo, the data) needed to reproduce the
> reported results.

```
Reproducible_JEM/
├── paths.py              # single source of truth for all paths
├── requirements.txt / environment.yml
├── run_all.sh            # reproduces every offline number + figure
├── README.md  DATA_SOURCES.md
├── scripts/              # ── GitHub ──
│   ├── local/            # offline analyses (reproduce the numbers; run by run_all.sh)
│   ├── figures/          # figure scripts (run by run_all.sh)
│   ├── raster/           # need the 6.5 GB classified rasters (provenance; outputs cached)
│   ├── gee/              # Google Earth Engine extraction (provenance; outputs cached)
│   └── wosis/            # WoSIS 0–30 cm aggregation (needs external WoSIS snapshot)
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

## Citation

If you use this code or data, please cite the article (once assigned) and the Zenodo data
archive (https://doi.org/10.5281/zenodo.20579004). External datasets retain their own citations
— see `DATA_SOURCES.md`.

## License

- Code (`scripts/`): MIT (see `LICENSE`, to be added).
- Data (`data/`) and manuscript text/figures: CC-BY-4.0 unless a source dataset specifies
  otherwise (see `DATA_SOURCES.md`).
