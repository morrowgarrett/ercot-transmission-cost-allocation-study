# Relay Governance

## Public repo requirement
Clutch must create the public repo named exactly `ercot-transmission-cost-allocation-study` when its environment supports GitHub access.

## Reviewer outage rule
If Clutch cannot authenticate or inspect Gear's filesystem, Gear continues producing local artifacts and the relay must not claim independent review completion.

## Round structure
Each round should produce:
- a production artifact
- a reviewer handoff packet or reviewer response
- any consequential methodology ADR
- public repo status
