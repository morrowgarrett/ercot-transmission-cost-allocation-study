# ADR-002 Net Load Definition

- Status: Accepted
- Date: 2026-04-11

## Context
Net-load variants require a consistent definition across 4CP Net Load, 12CP Net Load, hybrids, and any net-aware CBTCA sensitivities. Export treatment is especially contentious and can materially change allocation outcomes in high-renewable zones.

## Decision
Use raw net load = gross load - local generation - storage discharge + storage charging, with three required export-treatment sensitivities: Rule A floor-at-zero, Rule B signed net load, Rule C export-neutral with explicit export indicator.

## Alternatives considered
- Single floor-at-zero rule only
- Signed net load only
- Treat exports as direct credits in all base cases

## Consequences
The base framework stays coherent while preserving explicit sensitivity around the hardest normative choice. This increases implementation complexity slightly but makes the comparison far more honest.
