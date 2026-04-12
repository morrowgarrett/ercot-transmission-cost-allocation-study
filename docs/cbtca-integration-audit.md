# CBTCA Integration Audit

## Source audited
Legacy code reviewed in `projects/cbtca/src/models/`:
- `operational_ledger.py`
- `planning_ledger.py`
- `combined_allocator.py`
- `four_cp.py`
- `tdsp_allocator.py`

## What the legacy CBTCA code computes

### Operational ledger
- Primary result object: `OperationalLedgerResult`
- Supports two effective paths:
  - shadow-price direct approximation (`prepare_shadow_price_data`)
  - LMP decomposition fallback (`prepare_lmp_data`)
- Core outputs:
  - hourly charges
  - monthly summary
  - annual summary
  - zone allocations and ratios
  - capped-hours count
  - methodology notes
- Inputs required today:
  - DA LMP and system lambda for fallback path
  - optional direct congestion data
  - optional DAM/SCED shadow prices
  - optional system load and zone shift-factor approximations

### Planning ledger
- Primary result object: `PlanningLedgerResult`
- Identifies target constraints using keyword filters and/or planning/facility metadata
- Computes zone sensitivities from LMP minus system lambda during a reference window
- Allocates annual planning TCOS using sensitivity × load-share weighting
- Inputs required today:
  - DA LMP
  - system lambda
  - optional facilities and constraint summary data

### Combined allocator
- Primary result object: `CombinedAllocationResult`
- Blends operational and planning zone ratios using configurable weights
- Supports weight sweeps and comparison dataframe generation

### Legacy 4CP model
- Richer than the shared baseline scaffold
- Supports ERCOT-native, official, and API-derived paths
- Produces CP interval detail objects and zone allocations

### TDSP allocator
- Project-specific overlay that maps TDSPs to zones and applies hard-coded CBTCA zone ratios
- Useful as a downstream reporting layer, not as core shared-engine logic

## Mapping to shared engine

### Current shared inputs that already align
- `year`
- `tcos_target_usd`
- `system_load`
- `zonal_load`
- `net_zonal_load`
- `peak_intervals`
- `metadata`

### Inputs missing for CBTCA integration
The shared interface does not yet have explicit fields for:
- system lambda series
- zonal/node LMP series with decomposition
- shadow price / binding constraint records
- facilities metadata
- planning constraint summaries

### Recommended extension path
Add optional structured congestion/planning inputs rather than overloading `metadata`:
- `congestion_series`
- `system_lambda_series`
- `shadow_price_series`
- `planning_facilities`
- `planning_constraint_summary`

Short-term alternative: adapter reads these from `metadata`, but that should be transitional only.

## Integration recommendation
1. Do not rewrite legacy CBTCA internals yet
2. Add a structured congestion-data extension to shared inputs after ADR-008 approval
3. Wrap legacy operational/planning/combined results with adapter functions that emit `MethodologyResult`
4. Preserve richer pandas result objects for notebook/reporting use behind the adapter layer

## Risks
- Legacy CBTCA code is tightly coupled to project-specific config and file locations
- Result objects are richer than the current shared engine outputs
- Shadow-price and planning data availability may not match the simplified baseline schema
- TDSP allocator embeds project-specific zone ratios and should not be treated as core methodology logic
