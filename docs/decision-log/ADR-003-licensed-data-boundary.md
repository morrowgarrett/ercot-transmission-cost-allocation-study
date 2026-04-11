# ADR-003 Licensed Data Boundary

- Status: Accepted
- Date: 2026-04-11

## Context
The project depends on Yes Energy and Enverus data, both of which are licensed. The public repo must be community-vettable without leaking vendor content or reverse-engineerable derived raw tables.

## Decision
Keep all licensed raw and sensitive derived data local only. The public repo may contain code, schemas, methodology docs, synthetic fixtures, public-safe notebooks, and public-safe examples.

## Alternatives considered
- Commit small raw vendor samples for convenience
- Publish processed vendor-derived tables if raw inputs are omitted
- Keep the project entirely private

## Consequences
The public package remains legally safer and more shareable, but reproducibility requires synthetic fixtures and clear interface contracts rather than bundled commercial datasets.
