"""Reads results.csv (written by evaluate.py). No API calls, so it costs nothing.
Usage: python analyze_results.py
"""
import pandas as pd

r = pd.read_csv("results.csv")
r["ok"] = r.jev_category == r.true_category

if "source" in r:
    print("Accuracy by source (real vs synthetic):")
    print(r.groupby("source").ok.agg(["mean", "count"]).round(3).to_string(), "\n")

print("Threshold sweep (rows with confidence >= threshold are auto-categorized):")
print(f"{'threshold':>9} {'coverage':>9} {'accuracy':>9} {'wrong kept':>11}")
for t in [0.0, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
    kept = r[r.jev_confidence >= t]
    acc = kept.ok.mean() if len(kept) else float("nan")
    print(f"{t:>9.2f} {len(kept) / len(r):>9.0%} {acc:>9.1%} {(~kept.ok).sum():>11}")

print("\nPer-category accuracy (true category):")
print(r.groupby("true_category").ok.agg(["mean", "count"]).round(2).sort_values("mean").to_string())

print("\nConfident mistakes (confidence >= 0.9), the dangerous ones:")
print(r[(~r.ok) & (r.jev_confidence >= 0.9)][["description", "true_category", "jev_category", "jev_confidence"]].to_string(index=False))
