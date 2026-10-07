"""Compare repeated evaluation runs. No API calls.
Usage:  python compare_runs.py results_before
        python compare_runs.py results_after
Reads results_before_1.csv, results_before_2.csv, ... (saved by the 3-run loop).
"""
import glob
import sys

import pandas as pd

prefix = sys.argv[1] if len(sys.argv) > 1 else "results_before"
files = sorted(glob.glob(f"{prefix}_*.csv"))
if not files:
    sys.exit(f"No files matching {prefix}_*.csv")

runs = []
for f in files:
    r = pd.read_csv(f)
    r["ok"] = r.jev_category == r.true_category
    runs.append(r)

n = len(runs)
print(f"{n} runs from {prefix}_*.csv\n")

accs = [r.ok.mean() for r in runs]
print("Accuracy per run:", ", ".join(f"{a:.1%}" for a in accs))
print(f"Mean {sum(accs) / n:.1%}   range {min(accs):.1%} to {max(accs):.1%}\n")

if "source" in runs[0]:
    print("Accuracy by source, mean over runs:")
    by_src = pd.concat([r.groupby("source").ok.mean() for r in runs], axis=1).mean(axis=1)
    counts = runs[0].groupby("source").size()
    for s in by_src.index:
        print(f"  {s:<10} {by_src[s]:.1%}  ({counts[s]} rows)")
    print()

# Per-row stability. Rows are matched by position because all runs use the same file.
correct = pd.concat([r.ok.astype(int) for r in runs], axis=1).sum(axis=1)
base = runs[0][["description", "true_category"]].copy()
base["correct_runs"] = correct
base["jev_picks"] = [
    "/".join(sorted({str(r.loc[i, "jev_category"]) for r in runs})) for i in base.index
]
base["mean_conf"] = pd.concat([r.jev_confidence for r in runs], axis=1).mean(axis=1).round(2)

always_wrong = base[base.correct_runs == 0]
flipping = base[(base.correct_runs > 0) & (base.correct_runs < n)]
print(f"ALWAYS wrong in all {n} runs ({len(always_wrong)} rows): real weaknesses or label problems")
print(always_wrong.drop(columns="correct_runs").to_string(index=False), "\n")
print(f"FLIPPING between runs ({len(flipping)} rows): borderline cases, this is the noise")
print(flipping.to_string(index=False))
