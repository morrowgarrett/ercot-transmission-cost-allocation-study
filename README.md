# ERCOT Transmission Cost Allocation Study

An open-source research framework for comparing incumbent and alternative ERCOT transmission cost allocation methodologies under a shared interface, a shared comparison layer, and an explicit public-data boundary.

## Research question
**Which ERCOT transmission cost allocation methodology best balances cost causation, fairness, revenue sufficiency, administrative practicality, and resistance to strategic gaming, once the assumptions and proxy layers are made explicit?**

## What this repository is
This repository is a methodology lab.

It is built to let reviewers inspect, challenge, and compare multiple ERCOT transmission cost allocation approaches without pretending that all methods rely on the same quality of evidence.

It is not:
- a tariff filing
- a settlement engine
- a final policy recommendation
- a customer-billing reconstruction model
- a licensed data dump

That distinction matters. The point of the repo is not to smuggle in a preferred answer. The point is to make the arguments visible enough that they can be attacked honestly.

## Why this exists
ERCOT transmission cost allocation debates often collapse several different arguments into one noisy fight:
- who causes transmission costs
- who benefits from transmission investment
- which signals can be measured directly
- which signals require proxies
- how much strategic behavior a methodology invites
- how much administrative burden a methodology imposes

Those arguments should not be blended into a single slogan.

This repository separates them.

## Public-data boundary
This public repository does **not** include licensed Yes Energy or Enverus raw data.

Public artifacts are limited to:
- methodology specifications
- assumptions and decision logs
- shared-engine code
- comparison tooling
- synthetic example data
- tests
- public-safe notebooks
- documentation for external review

If you are looking for full empirical replication against private vendor datasets, this repo is not claiming to provide that.

## Current scope
The current public framework compares six implemented core methodologies plus one CBTCA sensitivity-family summary row in the scorecard.

### Core methodologies
1. **4CP**
2. **4CP Net Load**
3. **12CP**
4. **12CP Net Load**
5. **Hybrid Volumetric + 12CP Net Load**
6. **CBTCA**

### Scorecard family row
7. **CBTCA Sensitivities**, an aggregated robustness summary across predefined perturbation cases

## Methodology summary table
| Methodology | Short description | Main signal | Main strength | Main risk |
|---|---|---|---|---|
| 4CP | Incumbent summer coincident-peak allocation on gross load | Four summer system peak intervals | Simple, familiar, revenue-clear | Extremely narrow-window and highly gameable |
| 4CP Net Load | 4CP timing with net-load treatment | Four summer net-load peak intervals | Recognizes DER / BTM offsets | Very sensitive to export treatment and interval gaming |
| 12CP | Twelve monthly coincident peaks on gross load | Annual gross-load peak responsibility | Less spiky than 4CP | Still peak-centric, still indirect on congestion causation |
| 12CP Net Load | Twelve monthly coincident peaks on net load | Annual net-load peak responsibility | Annualizes net-load behavior | Can over-credit export-heavy zones depending on preprocessing |
| Hybrid Vol + 12CP NL | Blend of annual volumetric usage and 12CP net load | Usage + annual peak responsibility | More stable than pure peak methods | Still inherits some net-load preprocessing fragility |
| CBTCA | Congestion-Based Transmission Cost Allocation | Operational congestion burden + planning-ledger burden | Closest design intent to cost-causation analysis | Can rely on proxy hierarchy when direct congestion data is incomplete |
| CBTCA Sensitivities | Aggregated scenario family row | Stability across parameter perturbations | Shows robustness range instead of one point claim | Not an independent methodology, can be misread if framed poorly |

## What is implemented now
### Shared model interface
All core models emit the same shape:
- `MethodologyInputs`
- `MethodologyResult`

That common interface is what makes side-by-side comparison possible.

### Core model implementations
- `src/models/four_cp.py`
- `src/models/four_cp_net_load.py`
- `src/models/twelve_cp.py`
- `src/models/twelve_cp_net_load.py`
- `src/models/hybrid_vol_12cp_nl.py`
- `src/models/cbtca.py`

### Comparison layer
- `src/comparison/metrics.py`
- `src/comparison/scorecard.py`
- `src/comparison/synthetic_data.py`

The comparison layer currently reports:
- allocation shares by zone
- burden shift versus incumbent 4CP
- revenue sufficiency checks
- concentration metrics
- gaming-exposure heuristics
- CBTCA sensitivity-family summary metrics

## Repository structure
```text
assumptions/                 explicit modeling assumptions and approximation registry
data_manifest/               public/private boundary and data-source documentation
docs/                        limitations, validation, review guides, results, scope
methodologies/               plain-language methodology specifications
notebooks/                   public-safe exploratory notebooks
src/models/                  shared-engine methodology implementations
src/comparison/              scorecard, metrics, synthetic comparison fixtures
tests/                       regression and framework tests
README.md                    public entrypoint
CONTRIBUTING.md              contribution guide
LICENSE                      MIT license
```

## Installation
### Option A, editable install from a clean clone
```bash
git clone <repo-url>
cd ercot-transmission-cost-allocation-study
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

### Option B, requirements-based install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Python version
- Python `>=3.11`

### Core public dependencies
Defined in `pyproject.toml`:
- `pydantic`
- `pyyaml`
- `pandas`
- `pytest`

## Reproducing the public test suite
After installation:
```bash
python3 -m pytest -v
```

Or use the one-command reproduction target:
```bash
make reproduce
```

The current public suite covers:
- baseline methodology correctness
- CBTCA methodology fidelity and sensitivity behavior
- comparison-layer scorecard behavior
- preprocessing and export-rule handling

## Running the comparison layer
The easiest public-safe run uses the synthetic fixture rather than hand-building `MethodologyInputs`.

```python
from src.comparison.scorecard import build_comparison_bundle
from src.comparison.synthetic_data import build_four_zone_synthetic_inputs

inputs = build_four_zone_synthetic_inputs()
bundle = build_comparison_bundle(inputs)

print(bundle["scorecard"])
print(bundle["allocation_shares"])
print(bundle["burden_shift"])
```

### What the bundle returns
- `results`: raw methodology outputs
- `cbtca_sensitivity_results`: scenario-level CBTCA sensitivity outputs
- `allocation_shares`: zone-level shares and allocations
- `burden_shift`: differences versus incumbent 4CP
- `scorecard`: one-row-per-method summary table

## Synthetic data, clearly stated
The public comparison run uses a synthetic fixture called `four_zone_v1`.

It includes:
- four ERCOT load zones: `NORTH`, `SOUTH`, `WEST`, `HOUSTON`
- a high-BTM / export-heavy `WEST`
- an import-heavy high-load `HOUSTON`
- asymmetric congestion and planning stress patterns

It does **not** claim historical truth.

Read `docs/synthetic-data.md` before treating any scorecard result as more than a framework result.

## How to read the current results
Start here:
- `docs/methodology-scorecard-results.md`

That document summarizes the current synthetic comparison run and explains:
- what each methodology rewards
- what each methodology punishes
- how burden shifts differ from 4CP
- which method appears most gaming-resistant in the current heuristic framework
- why none of that should be mistaken for a live ERCOT policy verdict

## Supporting documentation
### Methodology specs
- `methodologies/4cp.md`
- `methodologies/4cp_net_load.md`
- `methodologies/12cp.md`
- `methodologies/12cp_net_load.md`
- `methodologies/hybrid_vol_12cp_nl.md`
- `methodologies/cbtca.md`
- `methodologies/cbtca_sensitivities.md`

### Scope, validation, and limits
- `docs/SCOPE.md`
- `docs/validation.md`
- `docs/limitations.md`
- `docs/methodology-scorecard-framework.md`
- `docs/methodology-scorecard-results.md`
- `docs/synthetic-data.md`

### Review and governance
- `docs/community-review-guide.md`
- `docs/decision-log/`
- `docs/relay-governance.md`
- `CONTRIBUTING.md`

### Assumptions and data-boundary docs
- `assumptions/approximation_registry.md`
- `assumptions/export_treatment_rules.md`
- `assumptions/net_load_definition.md`
- `assumptions/proxy_class_mapping.md`
- `data_manifest/licensing_policy.md`
- `data_manifest/overview.md`

## What this study can currently support
This public framework can currently support:
- methodology-to-spec comparisons
- code-level validation of implemented formulas
- synthetic stress tests across multiple methodologies
- burden-shift and concentration comparisons on common inputs
- explicit debate about proxy quality, fallback behavior, and review standards

## What this study cannot currently support
This repository cannot currently support credible claims about:
- real customer bill impacts
- tariff-grade settlement reconstruction
- final TDSP- or customer-class-level fairness conclusions
- real historical congestion-cost responsibility without licensed or richer public data
- empirical validation of the gaming-exposure heuristic values

That last point deserves emphasis. The gaming scores in the scorecard are useful directional heuristics, not field-calibrated truth.

## Explicit limitations
Short version:
- this is not customer-level settlement reconstruction
- TDSP and proxy-class views are analytical overlays, not tariff truth
- CBTCA may rely on proxy hierarchy when direct congestion components are unavailable
- `LMP - system lambda` is a congestion-plus-loss proxy, not pure congestion
- planning-ledger inputs may depend on simplified public-safe structures in the public framework
- net-load variants depend heavily on export treatment and BTM observability
- synthetic runs validate framework behavior, not real-world policy outcomes
- gaming metrics are heuristic and should be challenged, not worshiped

For the full list, read `docs/limitations.md`.

## How to contribute or challenge the results
Read:
- `CONTRIBUTING.md`
- `docs/community-review-guide.md`

Good contributions usually do one of four things:
1. catch a mismatch between code and methodology spec
2. make a proxy or fallback more honestly labeled
3. improve reproducibility or test depth
4. challenge an interpretation that pretends a synthetic result is stronger than it is

### If you disagree with a methodology implementation
Open an issue or PR with:
- the file and line range
- the disputed interpretation
- the methodology doc or protocol citation you think controls
- the practical effect on outputs

### If you want to submit data corrections
Do that only with public-safe material.

Do **not** submit:
- Yes Energy raw extracts
- Enverus raw extracts
- licensed customer data
- anything else that would violate the repo’s public boundary

## Review standard
The best critique is not “I don’t like the outcome.”

The best critique is one of these:
- the method does not match its own written spec
- the proxy hierarchy is overstated
- the comparison layer embeds a hidden policy preference
- the confidence language is too aggressive for the evidence quality
- the public/private data boundary is leaking

## License
This project is released under the **MIT License**.

See `LICENSE`.

## Attribution
Author of record in `pyproject.toml`:
- **Garrett Morrow**

This public repo also reflects iterative design, testing, and documentation refinement across the project workflow.

## Current status
Current package version in `pyproject.toml`:
- `0.1.0`

Current public posture:
- six core methodologies implemented
- seven scorecard rows including the CBTCA sensitivity family summary
- synthetic comparison fixture in place
- public test suite passing
- documentation oriented toward external scrutiny rather than narrative comfort

## If you only read three files
Read these first:
1. `README.md`
2. `docs/methodology-scorecard-results.md`
3. `docs/limitations.md`

That will tell you what the repo is doing, what it currently shows, and where it is still weak.
