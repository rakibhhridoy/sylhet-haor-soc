# Journal of Environmental Management — submission package

Target: **Journal of Environmental Management** (Elsevier; subscription/hybrid, free-to-publish
via the subscription route). Format: `elsarticle` (no reformatting needed).

## Contents
| File | Purpose |
|---|---|
| `Manuscript.tex` | Main manuscript (elsarticle, author-year). Compiles to `Manuscript.pdf` (24 pp incl. Supplementary Table S1). |
| `references.bib` | Bibliography (all DOIs CrossRef-verified). |
| `Fig1..Fig14*.png` | The 12 figures referenced in the text. |
| `Highlights.txt` | 5 highlights (<=85 chars each) for the JEM Highlights field. |
| `cover_letter.txt` | Cover letter (fill in [Date]). |

## Build
```
pdflatex Manuscript && bibtex Manuscript && pdflatex Manuscript && pdflatex Manuscript
```

## JEM-specific framing (vs the generic REVISION draft)
- Journal set to Journal of Environmental Management.
- Abstract opening + closing foreground the **integrated multi-source assessment** and
  **management/monitoring** contribution (what JEM rewards), including the confound-aware
  "inundated-area imagery can misrepresent hydrological change" lesson.

## Before submitting (author actions)
- Fill the cover-letter date; confirm author list/affiliations/ORCIDs.
- Confirm JEM is the chosen venue and that you publish via the (free) subscription route, not OA.
- Optional: add author ORCIDs and a graphical abstract if desired.
- Data availability: point to the repository (private GitHub `rakibhhridoy/sylhet-haor-soc`);
  decide if/when to make it public for the data-availability statement.

## Honest positioning (for your awareness)
The field soil core is n=9, single time point, with a secondary 1985 baseline; the long-term SOC
change is reported as suggestive (not significant). The manuscript's strength is the integrated,
statistically-supported environmental characterization (warming + drying + intensification), the
WoSIS/space-for-time external validation of the SOC-nitrogen (not clay) finding, and the
management framework. JEM was chosen to match this integrated-assessment + management scope.
Fallback venue if needed: Environmental Monitoring and Assessment (Springer).
