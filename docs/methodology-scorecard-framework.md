# Methodology Scorecard Framework

## Quantitative categories
- Allocation shares by zone, TDSP, proxy class
- Burden shift versus incumbent 4CP
- Year-to-year volatility
- Gaming exposure metrics
- Concentration metrics
- Congestion-causation alignment
- Revenue sufficiency checks

## Narrative categories
For every methodology, provide:
- Who benefits
- Who loses
- Behavior encouraged
- Behavior discouraged poorly or not at all
- Implementation burden
- Political resistance profile
- Confidence level and why

## Confidence overlay
Each methodology output must include High, Moderate, or Low confidence based on data directness, approximation burden, and sensitivity robustness.

## Composite scoring rule
A composite score may be reported only after implementation. Until then, component metrics are primary.
If a composite is used, normalize each quantitative metric using min-max scaling across methodologies within the same study year:

normalized(x) = (x - min(x_set)) / (max(x_set) - min(x_set))

If higher raw values are worse, invert after scaling.
Narrative dimensions are not folded into the numeric composite; they remain separate commentary.
