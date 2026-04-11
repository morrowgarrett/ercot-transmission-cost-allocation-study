# ADR-007 Export Rule Preprocessing Responsibility

- Status: Accepted
- Date: 2026-04-11

## Context
Rules A, B, and C govern how raw net load is transformed before it is used by net-load methodologies. The shared model layer currently consumes timestamped gross and net zonal load series rather than raw gross-generation-storage components.

## Decision
Export-rule application is a preprocessing responsibility, not an in-model responsibility, for v1 baseline models. Callers must provide `net_zonal_load` that already reflects the intended export rule and must declare that rule in `metadata.export_rule`.

## Alternatives considered
- Apply Rules A/B/C inside every net-load model
- Require raw generation and storage telemetry in `MethodologyInputs`
- Support only one export rule in v1

## Consequences
This keeps the model interfaces simple and avoids duplicating transformation logic across models, but it requires clear documentation and validation so callers do not mistakenly pass unprocessed raw net-load data.
