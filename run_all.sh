#!/usr/bin/env bash
# Reproduce every offline number, table and figure in the manuscript.
# Requires only the contents of data/ (no Google Earth Engine, no large rasters).
# Outputs land in results/ (stats *.md + figures *.png).
set -euo pipefail
cd "$(dirname "$0")"
PY=${PYTHON:-python3}

echo "==> Statistics & tables (results/*.md)"
$PY scripts/local/01_recompute_numbers.py        # soil 2025, PCA, SOC change, LULC m^2 trends
$PY scripts/local/02_flag_data_quality.py        # 1985 baseline screening (impossible values)
$PY scripts/local/03_analyze_dryseason.py        # dry-season NDVI / LST / NDWI trends
$PY scripts/local/04_analyze_hydrology.py        # ERA5-Land drying (soil moisture, precip, T)
$PY scripts/local/05_lulc_area_stats.py          # LULC %-of-area, fold-range, footprint CV
$PY scripts/local/06_sylhet_class_analysis.py    # WoSIS Sylhet-class correlations + placement
$PY scripts/local/07_regional_space_for_time.py  # climate-restricted SOC~temperature betas
$PY scripts/local/08_lulc_accuracy.py            # confusion matrix; 8-class & aggregated OA/kappa

echo "==> Figures (results/*.png)"
for f in make_fig2 make_fig3 make_fig5 make_fig7 make_fig8 make_fig9 \
         make_fig_wosis make_fig13_v2 make_fig14_converging; do
  $PY scripts/figures/$f.py
done

echo
echo "Done. See results/ for regenerated tables (*.md) and figures (*.png)."
echo "Fig1 (study area), Fig6 (annual LULC maps) and Fig11 (decadal indices) require the"
echo "6.5 GB classified/index rasters (not redistributed) -- see scripts/raster/ and DATA_SOURCES.md."
