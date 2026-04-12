# CBTCA Integration Audit

## Source audited
Legacy code reviewed in `projects/cbtca/src/models/`:
- `operational_ledger.py`
- `planning_ledger.py`
- `combined_allocator.py`
- `four_cp.py`
- `tdsp_allocator.py`

## What the legacy CBTCA code computes

### Operational ledger (`src/models/operational_ledger.py`)
- Primary result object: `OperationalLedgerResult`
- Two execution paths inside `run(...)`:
  - **Primary path:** `prepare_shadow_price_data(...)` when `dam_shadow_prices` is supplied
  - **Fallback path:** `prepare_lmp_data(...)` when only zonal DA LMP plus system lambda are available
- Shared downstream steps after data preparation:
  - `calculate_hourly_charges(...)`
  - `apply_outlier_cap(...)`
  - `aggregate(...)`
- Core outputs:
  - hourly zone charges
  - monthly and annual summaries
  - `zone_allocations_usd` and `zone_ratios`
  - `total_congestion_usd`
  - `capped_hours`
  - narrative `methodology_notes`
- Inputs accepted today by the legacy `run(...)` function:
  - `da_lmp`, `system_lambda`, `zone_loads`, `da_congestion`, `system_load`
  - `dam_shadow_prices`, `sced_shadow_prices`, `zone_shift_factors`
  - `annual_tcos`, `year`
- Important integration note: the code does not require all congestion artifacts at once. It supports a progressive fidelity ladder, with shadow prices preferred and LMP decomposition retained as a fallback.

### Planning ledger (`src/models/planning_ledger.py`)
- Primary result object: `PlanningLedgerResult`
- `run(...)` performs three steps:
  1. `identify_target_constraints(...)`
  2. `calculate_zone_sensitivities(...)`
  3. `allocate_planning_tcos(...)`
- Computes zone sensitivities from `DA LMP - system lambda` over a configured reference window, then weights those sensitivities by zone load share
- Inputs accepted today:
  - required: `da_lmp`, `system_lambda`
  - optional: `facilities`, `constraint_summary`
  - scalar controls: `year`, `annual_tcos`
- Important integration note: facilities and constraint summary data influence constraint identification and narrative context, but allocation can still run without them.

### Combined allocator (`src/models/combined_allocator.py`)
- Primary result object: `CombinedAllocationResult`
- Combines `OperationalLedgerResult` and `PlanningLedgerResult` by applying configurable operational/planning weights
- Also exposes:
  - `sweep_weights(...)` for sensitivity runs
  - `to_comparison_dataframe(...)` for 4CP vs CBTCA comparisons
- Important integration note: this layer only needs normalized zonal ratios from the two ledger submodels, which makes it a good adapter boundary for the shared engine.

### Legacy 4CP model (`src/models/four_cp.py`)
- Richer than the shared baseline scaffold
- Supports ERCOT-official, derived native-load, and API-sourced workflows
- Produces interval-level objects (`CPInterval`, `FourCPResult`) and can attach TDSP detail
- Important integration note: useful as a validation reference, but Phase 4 does not need to import this richer implementation into the shared baseline engine.

### TDSP allocator (`src/models/tdsp_allocator.py`)
- Reporting overlay that maps TDSPs to zones and applies static CBTCA zone ratios from `comparison_shift.parquet`
- Useful for downstream presentation and distributional analysis
- Not appropriate as core methodology logic in the shared engine because it depends on post-allocation zone ratios rather than producing them

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
- DA zonal LMP series
- system lambda series
- direct congestion component series (optional operational fallback validation path)
- DAM/SCED shadow price records
- zone shift-factor mappings
- facilities metadata
- planning constraint summaries

### Recommended extension path
Add optional structured congestion/planning inputs rather than overloading `metadata`:
- `zonal_lmp_series`
- `system_lambda_series`
- `congestion_series`
- `shadow_price_series`
- `zone_shift_factors`
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
