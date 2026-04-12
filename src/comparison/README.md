# Comparison Layer

This package compares methodology outputs on a shared interface.

## Modules
- `metrics.py` — tabular quantitative metrics
- `scorecard.py` — orchestration across models and scorecard assembly

## Current metrics
- allocation shares by zone
- burden shift vs 4CP
- revenue sufficiency checks
- concentration metrics
- gaming exposure heuristics

## Current limits
This layer is intentionally conservative. It compares what the models emit; it does not pretend synthetic inputs settle ERCOT policy arguments.
