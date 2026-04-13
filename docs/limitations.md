# Limitations

This repository is a public methodology lab, not a tariff adjudication engine.

That means the right question is not, "does this repo produce numbers?" It does. The right question is, "what kind of claim do those numbers justify?"

## What this study is doing
This v1 framework compares multiple ERCOT transmission cost allocation methodologies on a common interface and scorecard.

It is designed to support:
- methodology-to-spec validation
- burden-shift comparison on shared inputs
- explicit treatment of proxy layers and fallback logic
- public review of assumptions, approximations, and incentives

## What this study is not doing
This v1 framework is **not**:
- customer-level settlement reconstruction
- a full ERCOT tariff simulator
- an empirical proof of legal or regulatory superiority
- a substitute for licensed raw market datasets
- a final answer on who "should" pay transmission costs

## Core limits on inference
### 1. Not customer-bill truth
The public framework does not reconstruct customer invoices, settled allocator mechanics, rider interactions, or customer-specific billing determinants.

Any TDSP or proxy-class allocation shown here is an analytical overlay, not tariff-bill truth.

### 2. Zonal first, overlays second
The core public engine works at the zonal level. TDSP and proxy-class views are derived overlays layered on top of zonal logic.

That means:
- zonal outputs are the primary modeled object
- TDSP views inherit mapping assumptions
- proxy-class views inherit segmentation assumptions
- downstream overlays can look more precise than the evidence actually warrants if not read carefully

### 3. Proxy segmentation is not observed truth
The large-load vs retail split is not directly observed as a canonical public ERCOT field in this framework.

Proxy-class segmentation therefore depends on scenario overlays and judgment calls about:
- industrial concentration
- corridor characteristics
- load-factor behavior
- public geography context
- whatever public-safe classification inputs are available

That means proxy-class outputs are useful for directional stress testing, not for pretending we know the exact large-load share by reporting unit.

### 4. Net-load methods depend on preprocessing choices
All net-aware methods depend heavily on how net load is defined and how exports are treated.

Those choices are not cosmetic. They can materially change the ranking and burden shift of:
- 4CP Net Load
- 12CP Net Load
- Hybrid Volumetric + 12CP Net Load
- any CBTCA sensitivity variant that uses export-rule perturbations

If a reviewer disagrees with Rule A, B, or C preprocessing, that disagreement can legitimately change the result.

### 5. CBTCA can rely on proxies rather than direct congestion truth
CBTCA is designed to be more causation-aware than pure peak methods, but that does not mean every input is direct truth.

Its operational ledger may rely on a tiered proxy hierarchy:
- direct congestion component when available
- decomposed congestion estimate when available
- `LMP - system lambda` style congestion-plus-loss fallback when better decomposition is absent

That hierarchy is meaningful, but it is still a hierarchy of evidence quality, not a magic escape from missing data.

### 6. Planning-ledger approximation risk
The CBTCA planning ledger depends on constraint-scoring and target-set construction that may be assembled from simplified public-safe structures in the public repo.

That introduces several risks:
- target-set selection may not match the richness of a full market-system reconstruction
- shadow-price persistence may be simplified
- planning pressure may be over- or under-attributed depending on input assembly choices

So planning-ledger outputs should be read as structured approximations, not settled planning-cost attribution fact.

### 7. Synthetic comparison data is useful, but not empirical proof
The public comparison run uses synthetic data by design.

That is good for:
- testing the shared framework
- exposing directional behavior under stress cases
- showing how methods differ under export-heavy and high-BTM conditions

It is not good for:
- claiming real customer impacts
- proving historical cost causation
- validating a methodology for policy adoption on its own

Synthetic results can show how the machinery behaves. They cannot prove that the world behaves that way.

### 8. Gaming metrics are heuristic, not field-calibrated
The scorecard’s gaming-resistance metrics are currently heuristic and expert-assigned.

They are useful as ordinal challenge targets, not as empirically calibrated field measurements.

That means the scorecard can say things like:
- this method appears more exposed to narrow-window behavior than that one

It cannot honestly say:
- this model has been empirically validated to reduce gaming by X percent

### 9. Distributional equity is partly normative
Distributional equity is not a purely mechanical metric.

Reasonable people can disagree about whether equity means:
- closer match to measured load responsibility
- closer match to congestion causation
- greater bill stability
- less burden on retail load
- less burden on large industrial users
- more gradual transition from incumbent methodology

The framework can expose tradeoffs. It cannot abolish the underlying normative disagreement.

### 10. Political and administrative scoring is partly judgment-based
Administrative implementability and political resistance are not purely quantitative fields.

Narrative scoring in those areas reflects a structured analytical judgment about:
- data availability
- auditability
- explainability
- expected stakeholder resistance
- implementation burden

Those judgments should be challenged openly, not mistaken for objective law.

## Data-boundary limitations
### Licensed data is intentionally excluded from the public repo
This repository must not contain raw licensed Yes Energy or Enverus datasets.

That means the public package cannot by itself reproduce every empirical study Garrett may run locally with private data access.

### Public replication is partial by design
The public repo is reproducible at the level of:
- code
- tests
- methodology definitions
- synthetic examples
- assumptions
- scorecard structure

It is not a promise of full empirical replication against private vendor data.

## Approximation-specific cautions
The following approximation areas deserve extra skepticism:
- TDSP mapping from zonal results
- proxy-class segmentation into large-load vs retail overlays
- BTM observability in net-load methods
- fallback from direct congestion to proxy congestion
- planning-ledger target-set construction
- export-rule treatment under signed net-load variants
- synthetic weather / scarcity / outlier representation in public examples

## What this repo cannot conclude
This study cannot currently conclude, in any final or policy-grade sense:
- the exact fair allocator for ERCOT
- the exact bill impact on any real customer or customer class
- the precise historical cost responsibility of any zone, TDSP, or segment
- that CBTCA is definitively superior in the real system
- that any net-load methodology should or should not be adopted as policy
- that the gaming scores are empirically validated
- that proxy overlays are precise enough for legal or regulatory finality

## What this repo can conclude
This study can credibly conclude narrower things, such as:
- whether an implementation matches its stated methodology spec
- whether two methodologies behave differently under the same inputs
- whether a method is more or less dependent on proxy quality
- whether a method appears more or less exposed to narrow-window gaming incentives
- whether a burden shift is large, small, concentrated, or broadly distributed under the tested assumptions

## Reviewer guidance
If you want to criticize this repo well, separate these questions:
1. Is the method implemented correctly?
2. Are the assumptions honest?
3. Are the proxies too weak for the claim being made?
4. Is the narrative overstating what the evidence supports?

Those are different failure modes. Mixing them together creates noise and hides the real defects.
