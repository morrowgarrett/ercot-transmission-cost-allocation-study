# ERCOT Transmission Cost Allocation Study

An open-source research framework for comparing incumbent and alternative ERCOT transmission cost allocation methodologies.

## Research question
Which ERCOT transmission cost allocation methodology best balances cost causation, fairness, revenue stability, administrative implementability, and resistance to strategic gaming?

## Important boundary
This repository is a methodology lab, not a policy recommendation.

It does **not** publish licensed Yes Energy or Enverus raw data. Public artifacts are limited to code, methodology docs, assumptions, synthetic examples, tests, and public-safe notebooks.

## Methodologies in scope
1. ERCOT 4CP
2. 4CP Net Load
3. 12CP
4. 12CP Net Load
5. Hybrid volumetric + 12CP Net Load
6. CBTCA
7. CBTCA sensitivity variants

## What is implemented now
### Core models
- `src/models/four_cp.py`
- `src/models/four_cp_net_load.py`
- `src/models/twelve_cp.py`
- `src/models/twelve_cp_net_load.py`
- `src/models/hybrid_vol_12cp_nl.py`
- `src/models/cbtca.py`

All models emit the same shared interface:
- `MethodologyInputs`
- `MethodologyResult`

### Comparison layer
- `src/comparison/metrics.py`
- `src/comparison/scorecard.py`

The scorecard currently supports:
- zonal allocation shares
- burden shift vs incumbent 4CP
- revenue sufficiency checks
- concentration metrics
- gaming exposure heuristics
- CBTCA sensitivity scenarios

## Repo structure
- `methodologies/` — plain-language specs for each methodology
- `docs/decision-log/` — ADRs and scope decisions
- `assumptions/` — explicit modeling assumptions
- `src/models/` — shared-engine implementations
- `src/comparison/` — scorecard and metrics layer
- `tests/` — synthetic test coverage
- `notebooks/` — public-safe exploratory notebooks

## Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest -v
```

## Running the comparison layer
The current test suite uses synthetic fixtures to exercise the shared engine. For a local exploratory run, instantiate `MethodologyInputs` with:
- gross zonal load
- net zonal load where applicable
- monthly or seasonal peak intervals
- CBTCA congestion inputs (`zonal_lmp_series`, `system_lambda_series`, `shadow_price_series`, optional `congestion_series`)

Then call:
```python
from src.comparison.scorecard import build_comparison_bundle
bundle = build_comparison_bundle(inputs)
print(bundle["scorecard"])
```

## Reproducibility note
The public repo is reproducible at the code-and-tests level. Full empirical replication of licensed-data studies requires access to private vendor datasets that are intentionally not published here.

## Limitations
See `docs/limitations.md`.

Short version:
- this is not customer-level settlement reconstruction
- CBTCA may rely on proxy hierarchy when direct congestion data is absent
- synthetic comparison runs validate framework behavior, not real-world policy outcomes

## Contributing
Read `CONTRIBUTING.md` and `docs/community-review-guide.md`.

The best contributions make assumptions more visible, not less.
