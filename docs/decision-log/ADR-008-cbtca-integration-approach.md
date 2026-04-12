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
   - `congestion_series`: zonal LMP decomposition (energy, congestion, loss components)
   - `system_lambda_series`: system-wide energy price baseline
   - `shadow_price_series`: binding constraint shadow prices
   - `planning_facilities`: transmission facility metadata for planning ledger
   - `planning_constraint_summary`: constraint identification and reference-period parameters
   All fields are `Optional` and default to `None`. Existing models ignore them.
4. Build adapter functions that translate shared inputs into the legacy CBTCA submodel expectations before refactoring internals
5. Preserve CBTCA-specific rich intermediate result objects behind adapter boundaries, but normalize public outputs to shared `MethodologyResult`

## Alternatives considered
- Create a wholly separate CBTCA-only input class
- Rewrite the legacy CBTCA models from scratch before integration
- Collapse all congestion/planning inputs into generic metadata dicts without structure

## Consequences
This approach minimizes destructive rewrite risk, keeps the baseline engine comparable, and allows phased migration of the existing CBTCA code. It does require extending the shared input schema beyond simple load series and will likely introduce adapter complexity in the short term.

## Backward compatibility
The existing five baseline models continue to operate unchanged so long as any new congestion/planning fields are optional. They can ignore those fields entirely and continue consuming the current load-centric interface.

## Approval boundary
No CBTCA integration code should be merged under this ADR until the optional-field shape is accepted by review. The next relay may implement adapters and shared-schema extensions after ADR-008 is approved.
