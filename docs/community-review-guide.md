# Community Review Guide

If you want to review this repo well, scrutinize the weak joints, not the marketing copy.

## 1. Methodology fidelity
Check whether each implemented model matches its methodology spec closely enough to be publicly defensible.

Focus on:
- peak interval handling in 4CP and 12CP variants
- export-rule handling in net-load methodologies
- whether the hybrid model really mixes volumetric and 12CP net-load logic the way the spec says
- whether CBTCA clearly labels proxy hierarchy, planning target-set construction, and fallback behavior

## 2. Proxy honesty
CBTCA is the place where false precision can creep in.

Review:
- whether direct congestion, decomposed congestion, and LMP-minus-system-lambda are kept distinct
- whether fallback modes are clearly flagged in warnings and assumptions
- whether confidence labels are conservative enough

## 3. Comparison neutrality
The scorecard should not assume a winner.

Challenge:
- embedded gaming-resistance heuristics
- interpretation of burden shifts vs 4CP
- concentration metrics and whether they overstate or understate distributional issues
- any composite framing that hides component tradeoffs

## 4. Public/private boundary
This public repo must not include licensed raw data.

Verify that:
- no Yes Energy or Enverus extracts are committed
- notebooks use synthetic or public-safe example inputs
- docs do not imply reproducibility from data that is not actually public

## 5. Reproducibility
A reviewer should be able to install dependencies and run tests without private infrastructure.

Minimum expectation:
```bash
pip install -r requirements.txt
python3 -m pytest -v
```

## 6. Best kinds of issues to file
Open an issue when you find:
- a methodology mismatch
- a silent fallback
- a misleading confidence label
- a comparison metric that bakes in a policy preference
- a public/private data-boundary leak

The goal is not consensus. The goal is pressure-tested clarity.
