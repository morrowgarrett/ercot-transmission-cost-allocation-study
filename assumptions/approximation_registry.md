# Approximation Registry

This file exists to make approximation debt explicit.

Every material approximation in the public framework should be recorded with enough detail that a reviewer can answer four questions:
1. what is being approximated
2. why it had to be approximated
3. which methodologies are affected
4. what kind of bias or interpretive risk it may introduce

## Minimum fields for each approximation entry
For each material approximation, record:
- approximation name
- affected methodologies
- affected outputs
- rationale
- underlying data gap
- approximation rule or fallback logic
- sensitivity coverage
- expected directional bias, if known
- confidence level
- public replacement path, if one exists
- licensed-data replacement path, if one exists

## Priority approximation classes in this repo
At minimum, the public registry should cover approximations in these categories:
- net-load construction where direct observability is incomplete
- export treatment under Rules A, B, and C
- proxy segmentation between large-load and retail overlays
- TDSP mapping derived from zonal results
- CBTCA congestion proxy fallback hierarchy
- CBTCA planning-ledger target-set construction
- synthetic comparison fixtures and any weather / scarcity simplifications
- annual TCOS target estimation when exact public allocator context is incomplete

## Review standard
Do not use the registry to hide weak evidence behind tidy prose.

Use it to state, plainly:
- where the model is standing on direct measurement
- where it is standing on proxy logic
- where results are likely stable
- where results are highly assumption-sensitive

## Bias language
When possible, directional bias should be stated in concrete terms, for example:
- may over-credit export-heavy zones
- may understate congestion burden in mixed loss/congestion fallbacks
- may flatten within-zone customer diversity
- may overstate confidence in TDSP-level burden patterns

If directional bias is unknown, say that too. False confidence is worse than admitted uncertainty.
