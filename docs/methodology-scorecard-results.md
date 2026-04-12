# Methodology Scorecard Results

## Status
This file summarizes the v1 comparison layer using synthetic example inputs. It is a framework validation artifact, not a substantive ERCOT policy conclusion.

## What the scorecard currently does
The comparison layer now produces:
- zonal allocation-share tables across all six implemented core models
- burden shift versus incumbent 4CP
- revenue sufficiency checks
- concentration metrics
- gaming exposure heuristics
- optional CBTCA sensitivity scenarios

## What the synthetic run is good for
- validating that every model emits a comparable `MethodologyResult`
- checking that shares sum to 1.0 and allocations sum to the TCOS target
- confirming that the scorecard can compare baseline models and CBTCA on the same interface
- demonstrating that CBTCA fallback modes are surfaced rather than hidden

## What it is not good for
- claiming a preferred ERCOT policy outcome
- estimating real customer bill impacts
- proving congestion-cost causation fidelity
- adjudicating TDSP-level fairness with licensed vendor data absent

## Early pattern from the framework
The framework shows that different methodologies can be compared on the same scaffolding without pretending they rely on equally direct data.

That matters. The real fight is not only over who pays, but over how much approximation burden we are willing to tolerate before calling a model policy-grade.

## Next review targets
External reviewers should especially stress-test:
- the CBTCA gaming-exposure heuristic values
- planning target-set selection logic
- confidence labeling for proxy-driven methods
- whether synthetic examples unintentionally flatter one methodology
