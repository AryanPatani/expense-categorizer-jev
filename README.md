# Expense Categorizer with Jev

Classifies short UPI payment notes (`chai`, `auto to station`, `AC service`) into spending
categories using **Jev**, TypeSafe AI's "System One" model, which returns typed, probabilistic
decisions instead of free text. Low-confidence predictions can be routed to manual review.

This is a learning project. The focus is on **measuring** the model honestly, not only calling it.
It is not affiliated with TypeSafe AI.

## How it works

Each transaction is sent to Jev as *state* (description and amount) with two typed questions:

- `Choice`: which of 9 categories does this belong to?
- `Noul`: how likely is this a recurring payment?

Jev returns a probability per category plus a confidence value. If confidence is below a
threshold, the transaction becomes `needs_review` instead of a guess.

| File | Purpose |
|---|---|
| `categorizer.py` | Core logic and category definitions |
| `baseline.py` | Keyword-matching baseline (built for merchant names, so a weak comparison) |
| `evaluate.py` | Accuracy, coverage and latency on a labeled CSV |
| `analyze_results.py` | Threshold sweep, per-category accuracy, confident mistakes |
| `compare_runs.py` | Compares repeated runs: which rows are stable errors vs. noise |
| `app.py` | Streamlit demo |
| `data/expenses_labeled.csv` | Synthetic sample data only |

## Results

Categories: food, groceries, transport, bills, shopping, entertainment, health, travel, other.

**Dev set:** 105 rows (58 real UPI notes, 47 synthetic). Category definitions were tuned on this set.
**Holdout:** 32 real notes, partly hand-picked as ambiguous. Not used for tuning until after the v1 result.

| Set | Result | Notes |
|---|---|---|
| Dev set, first definitions | 84.4% | mean of 3 runs |
| Dev set, tuned (v1) | 92.7% | mean of 3 runs; optimistic, tuned on this set |
| Dev set, v2 definitions | 93.0% | mean of 3 runs; no regressions |
| Dev set, real rows only | 78.2% → 87.4% | v0 → v2 |
| **Holdout, v1 definitions** | **75.0%** | **clean estimate** (n=32) |
| Holdout, v2 definitions | 86.5% (84 to 88%) | tuned on: the v2 change was made after seeing these mistakes |

Confidence threshold (v1 definitions): at 0.8, coverage was 78% with 91.5% accuracy on the dev set
and 81% with 88.5% on the holdout. Median latency was roughly 0.3 to 0.7 s per call, measured from my machine.

With 105 and 32 rows, one row is 1 to 3 points, so treat these as estimates, not precise figures.
Raw outputs vary by about 1 to 3 points between identical runs, so I report means over 3 runs.

### What I found

- **A definition conflict caused most holdout errors.** My `food` definition listed snacks and drinks,
  while my labeling rule said packaged items are groceries. Jev followed the written definition.
  Six of the eight v1 holdout errors were this single conflict. Aligning the two lifted the holdout
  with no regressions on the dev set.
- **Confidence flags uncertainty but not every error.** Some mistakes had confidence of 0.94 to 1.0.
- **The amount is not used reliably.** A 5 rupee railway ticket was labeled travel, and a 100 rupee
  `ps5` as shopping. A rule in code, run before the model, would be the fix.

### Limitations

- Small evaluation sets; tuning and dev data overlap; the v2 holdout score is not clean.
- Some dev-set food/groceries labels were assigned before the labeling rule was finalized.
- Bare words (`cable`, `diet coke`) are ambiguous and can produce confident wrong answers.
- Jev is days old and in early access; check TypeSafe's docs for current API behavior and pricing.
- The keyword baseline scored about 33%, but it was written for merchant names, so it is not a fair
  comparison for informal notes.
- Real transactions are not published for privacy. Only synthetic sample data is included.

## Category definitions

Version 1 vs. version 2 (only these two changed):

```
v1 food:      Ready-to-eat meals, snacks, street food, drinks, cafes, canteen or mess, food delivery
v1 groceries: Ingredients and packaged items for home: vegetables, milk, bread, eggs, quick-commerce grocery orders

v2 food:      Meals and items eaten or drunk on the spot: restaurant, cafe, street food, canteen or mess,
              food delivery, single-serve snacks, ice cream, juice, chaas, a single can or glass of a soft drink
v2 groceries: Items bought to take home: vegetables, milk, bread, eggs, sauces, pickles, and packaged snacks,
              biscuits, chips, chocolates and multipack or large bottled drinks; quick-commerce grocery orders
```

## Labeling rules I used

- Label by what was actually bought, not by the merchant name.
- Services and fees with no category (haircut, repair, photocopy, exam fee), cash withdrawals and
  money sent to people go in `other`.
- Physical non-food, non-medicine products (stationery, toiletries, merchandise) go in `shopping`.
- Packaged items bought to take home go in `groceries`; things eaten or drunk on the spot go in `food`.
- Local train and daily commute go in `transport`; intercity trips and bookings go in `travel`.
- Phone recharge and rent go in `bills`.
- Write the rules before labeling. I wrote some after, which created ambiguous labels.

## Run it

```
pip install -r requirements.txt
$env:TYPESAFE_API_KEY = "your-key"        # PowerShell; use export on Mac/Linux
python categorizer.py                      # smoke test
python evaluate.py data/expenses_labeled.csv
python analyze_results.py
streamlit run app.py
```

Use your own labeled CSV with the columns `description,amount,true_category`.
