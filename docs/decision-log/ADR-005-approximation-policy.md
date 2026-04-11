# ADR-005 Approximation Policy

- Status: Accepted
- Date: 2026-04-11

## Context
PTDFs, zonal load series, system lambda, proxy class segmentation, and BTM observability may all be incomplete. Hidden approximations would make the public conclusions misleading.

## Decision
Every material approximation must be documented, surfaced in outputs, and sensitivity-tested where relevant. Runs that depend on degraded proxies must carry confidence penalties and warnings.

## Alternatives considered
- Silent approximation inside code
- Stop work whenever data is incomplete
- Publish a single approximation path without sensitivity coverage

## Consequences
The project becomes more verbose but far more defensible. Approximation-aware outputs will be slower to produce and interpret, but they will survive scrutiny better.
