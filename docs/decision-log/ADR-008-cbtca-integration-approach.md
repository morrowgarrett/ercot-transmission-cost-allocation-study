# ADR-008 CBTCA Integration Approach

- Status: Proposed
- Date: 2026-04-11

## Context
The legacy CBTCA project under `projects/cbtca/src/models/` already implements operational, planning, combined, 4CP, and TDSP allocation logic with pandas-heavy result objects and project-specific configuration. Phase 4 requires integrating CBTCA into the shared methodology engine without silently losing methodological detail.

## Decision
Proposed integration path:
1. Keep the shared `MethodologyInputs` / `MethodologyResult` interface for top-level comparability
2. Extend `MethodologyInputs` with optional congestion-oriented fields rather than introducing a separate incompatible input class
3. Add structured optional fields to `MethodologyInputs` in a future revision:
   - `zonal_lmp_series`: zonal DA LMP time series used by the planning ledger and by the operational ledger fallback path
   - `system_lambda_series`: system-wide energy price baseline
   - `congestion_series`: optional direct congestion component series for validation or fallback support
   - `shadow_price_series`: DAM or SCED binding constraint shadow prices for the preferred operational path
   - `zone_shift_factors`: optional zone-by-constraint mapping used when shadow prices are available
   - `planning_facilities`: transmission facility metadata for planning ledger
   - `planning_constraint_summary`: constraint identification and reference-period parameters
   All fields are `Optional` and default to `None`. Existing models ignore them.
4. Build adapter functions that translate shared inputs into the legacy CBTCA submodel expectations before refactoring internals
5. Preserve CBTCA-specific rich intermediate result objects behind adapter boundaries, but normalize public outputs to shared `MethodologyResult`
6. Treat CBTCA as three shared-engine layers:
   - operational ledger adapter
   - planning ledger adapter
   - combined allocator wrapper
   The TDSP allocator stays outside the core methodology engine as a downstream reporting layer.

## Alternatives considered
- Create a wholly separate CBTCA-only input class
- Rewrite the legacy CBTCA models from scratch before integration
- Collapse all congestion/planning inputs into generic metadata dicts without structure
- Reuse a single generic `CongestionData` blob instead of discrete optional fields

## Consequences
This approach minimizes destructive rewrite risk, keeps the baseline engine comparable, and allows phased migration of the existing CBTCA code. It does require extending the shared input schema beyond simple load series and will introduce adapter complexity in the short term.

Using discrete optional fields instead of a single opaque `CongestionData` object keeps the schema auditable. The tradeoff is a wider input contract, but that is preferable here because the legacy code already distinguishes between zonal LMP, system lambda, direct congestion, shadow prices, shift factors, and planning metadata.

## Backward compatibility
The existing five baseline models continue to operate unchanged so long as any new congestion/planning fields are optional. They can ignore those fields entirely and continue consuming the current load-centric interface.

Adapter code for Phase 4 implementation should also tolerate partial CBTCA datasets. Specifically:
- if `shadow_price_series` is present, the operational adapter should prefer it
- if not, but `zonal_lmp_series` plus `system_lambda_series` are present, the operational adapter may fall back to LMP decomposition
- the planning adapter requires `zonal_lmp_series` plus `system_lambda_series`
- `planning_facilities` and `planning_constraint_summary` should remain optional enrichments, not hard blockers

## Approval boundary
No CBTCA integration code should be merged under this ADR until the optional-field shape is accepted by review. The next relay may implement adapters and shared-schema extensions after ADR-008 is approved.
