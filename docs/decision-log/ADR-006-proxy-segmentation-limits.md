# ADR-006 Proxy Segmentation Limits

- Status: Accepted
- Date: 2026-04-11

## Context
The brief requires proxy class outputs for large-load versus retail, but v1 does not have customer-level settlement data. There is real risk that readers over-interpret proxy overlays as billing truth.

## Decision
Treat TDSP and proxy-class results as analytical overlays only. Large-load versus retail views must be scenario-based, confidence-tagged, and never described as customer-level settlement reconstruction.

## Alternatives considered
- Avoid proxy segmentation entirely
- Publish a single-point proxy class split as if it were measured
- Claim customer-level equity conclusions from zone-level data

## Consequences
The equity layer becomes more cautious but more truthful. Some readers may want sharper claims than the data can support; those claims are intentionally deferred.
