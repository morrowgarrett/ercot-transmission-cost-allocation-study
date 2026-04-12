# Synthetic Data Boundary

## Purpose
The comparison layer currently uses a public-safe synthetic fixture to validate methodology behavior and scorecard wiring without exposing licensed data.

The fixture is **not** an empirical ERCOT reconstruction.

## Current fixture
- Name: `four_zone_v1`
- Source module: `src/comparison/synthetic_data.py`
- Coverage: `NORTH`, `SOUTH`, `WEST`, `HOUSTON`

## What is synthetic
The following fields are synthetic and hand-constructed for testability:
- `zonal_load`
- `net_zonal_load`
- `zonal_lmp_series`
- `system_lambda_series`
- `congestion_series`
- `shadow_price_series`

These values are shaped to create useful comparison stress, not to claim historical truth.

## What the fixture is trying to represent
- **NORTH**: large diversified load center
- **SOUTH**: moderate-load region with lower congestion intensity
- **WEST**: high-BTM / renewable-heavy zone with export-heavy summer net-load behavior, including negative net-load intervals
- **HOUSTON**: large coastal import-heavy zone with elevated gross load and summer constraint pressure

## Why this is better than the earlier toy fixture
The earlier comparison inputs were effectively a two-zone toy. That was enough to smoke-test interfaces, but too weak to support meaningful method comparison.

The new fixture improves on that by:
- covering all four ERCOT load zones
- introducing asymmetric gross vs net load behavior
- including a high-BTM / export-heavy case
- creating distinct congestion and planning-pressure patterns by zone

## What would come from real data in a deeper study
A non-synthetic run would replace these fields with:
- zonal gross load from ERCOT or licensed vendors
- net-zonal load after explicit Rule A/B/C preprocessing
- DA zonal LMP and, where available, decomposition components
- system lambda or equivalent energy baseline
- direct congestion components where available
- binding shadow prices / constraint records for planning-ledger target-set construction

## What this synthetic fixture can and cannot do
### Useful for
- verifying that all methodologies accept the shared input interface
- checking that allocation shares sum correctly
- exercising burden-shift, concentration, and sensitivity reporting
- surfacing whether one methodology behaves strangely under export-heavy or high-BTM conditions

### Not useful for
- estimating real customer bill impact
- proving cost-causation fidelity
- ranking methodologies for policy adoption
- validating TDSP-level or customer-class fairness in the real ERCOT system

## Review guidance
If you challenge a scorecard result that comes from this fixture, challenge two things separately:
1. whether the code computes the methodology correctly
2. whether the synthetic input assumptions are flattering or unfair to a methodology

Those are different arguments. Keep them separate.
