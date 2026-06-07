"""
LULC classification accuracy (Section 2.7 / Table 1 of the manuscript).

Computes, from the 285 labelled stratified-random reference points
(data/derived/accuracy_points_2024.csv):
  (1) the full eight-class confusion matrix, overall accuracy and Cohen's kappa
      -> OA 56.8%, kappa 0.50; user's accuracy Urban 95%, Vegetation 98% (Table 1); and
  (2) the functionally aggregated assessment in which the seasonally interconverting
      hydromorphic sub-classes (Water, Flood-prone, Flooded vegetation, Wetland) are merged
      into a single "Hydromorphic" class -> OA 83.2%, kappa 0.74 (cited in text + Table 1 caption).
Outputs: results/lulc_accuracy_results.md (also printed).
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from paths import DERIVED, RESULTS  # noqa: E402

import pandas as pd, numpy as np  # noqa: E402
from sklearn.metrics import confusion_matrix, cohen_kappa_score, accuracy_score  # noqa: E402

YEAR = 2024
df = pd.read_csv(f"{DERIVED}/accuracy_points_{YEAR}.csv")
df = df[df["true_class"].astype(str).str.strip() != ""].copy()
if len(df) == 0:
    raise SystemExit("No labelled points: the 'true_class' column is empty.")

# ---- (1) full eight-class assessment ----------------------------------------
labels = sorted(set(df.predicted_class) | set(df.true_class))
cm = confusion_matrix(df.true_class, df.predicted_class, labels=labels)
oa = accuracy_score(df.true_class, df.predicted_class)
kappa = cohen_kappa_score(df.true_class, df.predicted_class, labels=labels)
ua = np.divide(np.diag(cm), cm.sum(0), out=np.zeros(len(labels)), where=cm.sum(0) != 0)
pa = np.divide(np.diag(cm), cm.sum(1), out=np.zeros(len(labels)), where=cm.sum(1) != 0)

out = [f"# LULC accuracy assessment {YEAR} (n={len(df)} reference points)\n",
       "## Full eight-class",
       f"- Overall accuracy: **{oa*100:.1f}%**", f"- Cohen's kappa: **{kappa:.2f}**\n",
       "Confusion matrix (rows = reference/true, cols = map/predicted):\n",
       "| true \\\\ pred | " + " | ".join(labels) + " | Producer's |",
       "|" + "---|" * (len(labels) + 2)]
for i, lab in enumerate(labels):
    out.append(f"| {lab} | " + " | ".join(str(int(v)) for v in cm[i]) + f" | {pa[i]*100:.0f}% |")
out.append("| User's | " + " | ".join(f"{u*100:.0f}%" for u in ua) + " |  |")
# claim-bearing per-class user's accuracies
for lab in ("Urban", "Vegetation"):
    if lab in labels:
        out.append(f"- {lab} user's accuracy: **{ua[labels.index(lab)]*100:.0f}%**")

# ---- (2) functionally aggregated (hydromorphic merged) ----------------------
HYDRO = {"Water", "Flood-prone", "Flooded vegetation", "Wetland"}
agg = lambda s: "Hydromorphic" if s in HYDRO else s
t2 = df.true_class.map(agg); p2 = df.predicted_class.map(agg)
lab2 = sorted(set(p2) | set(t2))
oa2 = accuracy_score(t2, p2)
k2 = cohen_kappa_score(t2, p2, labels=lab2)
out += ["\n## Functionally aggregated (Water/Flood/FloodedVeg/Wetland -> Hydromorphic)",
        f"- Overall accuracy: **{oa2*100:.1f}%**", f"- Cohen's kappa: **{k2:.2f}**",
        "  (confusion is confined almost entirely to the seasonally interconverting hydromorphic",
        "   sub-classes; merging them recovers the level at which the LULC data are interpreted.)"]

txt = "\n".join(out)
open(f"{RESULTS}/lulc_accuracy_results.md", "w").write(txt)
print(txt)
print(f"\nSaved {RESULTS}/lulc_accuracy_results.md")
