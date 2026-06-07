"""
Central path configuration for the Sylhet Haor SOC reproducibility package.

Every analysis script imports from here, so the bundle works wherever it is unzipped:
clone the GitHub repo (scripts/, paths.py) and drop the Zenodo `data/`
archive in next to this file.

Layout
------
<repo root>/
  paths.py            <- this file (defines ROOT as its own directory)
  scripts/            <- code (GitHub)
  data/               <- inputs + derived products (Zenodo)
    field/            <- 2025 field soil + 1985 baseline + lab workbook
    geodata/          <- spectral-index & LULC-area CSVs
    gis/              <- study-area boundary shapefile
    derived/          <- cached GEE / raster outputs (so numbers reproduce offline)
  results/            <- regenerated tables, stats (*.md) and figures (created on run)
"""
import os

ROOT    = os.path.dirname(os.path.abspath(__file__))
DATA    = os.path.join(ROOT, "data")
FIELD   = os.path.join(DATA, "field")
GEODATA = os.path.join(DATA, "geodata")
GIS     = os.path.join(DATA, "gis")
DERIVED = os.path.join(DATA, "derived")
RESULTS = os.path.join(ROOT, "results")

os.makedirs(RESULTS, exist_ok=True)
