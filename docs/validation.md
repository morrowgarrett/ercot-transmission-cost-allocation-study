# Validation

## Universal checks
- Allocation shares sum to 1.0 within tolerance
- Dollar allocations sum to annual TCOS target within tolerance
- Missing critical inputs fail loudly
- Sensitivity and approximation flags appear in outputs

## Baseline methods
- Peak intervals are traceable to source series
- Hourly fallback is flagged when used

## Net-load methods
- Net load treatment rule is explicit
- Export rule is explicit
- Net load negativity behavior is validated per rule

## CBTCA
- Operational proxy tier is explicit
- Planning reference window is explicit
- Planning target-set size is explicit
- If no operational signal is available, model falls back to planning-only sensitivity mode and labels the run accordingly
