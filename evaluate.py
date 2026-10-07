"""Measure Jev vs. the keyword baseline on hand-labeled data.

Usage: python evaluate.py data/expenses_labeled.csv
This is the part that makes the project resume-worthy: real numbers.
"""
import sys
import time

import pandas as pd

from baseline import baseline_categorize
from categorizer import categorize

path = sys.argv[1] if len(sys.argv) > 1 else "data/expenses_labeled.csv"
df = pd.read_csv(path)

rows = []
for _, r in df.iterrows():
    start = time.perf_counter()
    out = categorize(r["description"], r.get("amount"))
    latency_ms = (time.perf_counter() - start) * 1000
    rows.append({
        **r.to_dict(),
        "jev_category": out["category"],
        "jev_confidence": out["confidence"],
        "jev_final": out["final_category"],
        "baseline": baseline_categorize(r["description"]),
        "latency_ms": latency_ms,
    })

res = pd.DataFrame(rows)
res.to_csv("results.csv", index=False)

n = len(res)
jev_acc = (res.jev_category == res.true_category).mean()
base_acc = (res.baseline == res.true_category).mean()

# Of the transactions Jev was confident about, how many did it get right?
confident = res[res.jev_final != "needs_review"]
conf_acc = (confident.jev_category == confident.true_category).mean() if len(confident) else float("nan")

print(f"Transactions evaluated:      {n}")
print(f"Jev accuracy (all):          {jev_acc:.1%}")
print(f"Keyword baseline accuracy:   {base_acc:.1%}")
print(f"Jev coverage @ threshold:    {len(confident) / n:.1%} (rest sent to review)")
print(f"Jev accuracy on confident:   {conf_acc:.1%}")
print(f"Median latency per call:     {res.latency_ms.median():.0f} ms")

print("\nMistakes to study (these teach you the most):")
print(res[res.jev_category != res.true_category][
    ["description", "true_category", "jev_category", "jev_confidence"]
].to_string(index=False))
