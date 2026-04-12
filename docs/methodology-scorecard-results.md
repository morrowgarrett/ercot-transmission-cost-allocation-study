# Methodology Scorecard Results

## Status
This document summarizes the current comparison run using the public-safe synthetic fixture `four_zone_v1`.

It is a **framework result**, not a real ERCOT policy recommendation. Every number below comes from synthetic inputs documented in `docs/synthetic-data.md`.

## Synthetic run setup
- Dataset: `four_zone_v1`
- Zones: `NORTH`, `SOUTH`, `WEST`, `HOUSTON`
- Edge cases included:
  - export-heavy / high-BTM `WEST`
  - import-heavy high-load `HOUSTON`
  - asymmetric congestion patterns across all four zones
- TCOS target: `$1,000`

## Scorecard summary table
| Methodology | NORTH | SOUTH | WEST | HOUSTON | Max Zone Share | HHI | Mean Abs Shift vs 4CP | Gaming Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 4CP | 32.40% | 24.01% | 13.52% | 30.07% | 32.40% | 0.271 | n/a | 0.90 |
| 4CP Net Load | 38.66% | 28.92% | -5.02% | 37.44% | 38.66% | 0.376 | 9.27 pts | 0.75 |
| 12CP | 31.61% | 23.29% | 15.77% | 29.33% | 31.61% | 0.265 | 1.13 pts | 0.55 |
| 12CP Net Load | 37.35% | 27.66% | -0.84% | 35.83% | 37.35% | 0.344 | 7.18 pts | 0.45 |
| Hybrid Vol + 12CP NL | 35.05% | 25.91% | 5.81% | 33.23% | 35.05% | 0.304 | 3.86 pts | 0.35 |
| CBTCA | 43.82% | 15.52% | 14.23% | 26.43% | 43.82% | 0.306 | 6.06 pts | 0.25 |
| CBTCA Sensitivities (family row) | n/a | n/a | n/a | n/a | 43.82% | 0.306 | n/a | 0.30 |

## Read before interpreting
Three things matter here:
1. all methodologies recover the full `$1,000` synthetic TCOS target within tolerance
2. these methods are not answering the same moral question, even when they share a scorecard
3. synthetic stress cases can expose directional behavior, but not settle an ERCOT policy fight

## Methodology-by-methodology narrative

### 4CP
4CP rewards gross-load contribution during the four summer coincident peak intervals. In this synthetic run it places the largest burden on `NORTH` at **32.40%** and `HOUSTON` at **30.07%**, while leaving `WEST` at **13.52%**. That is exactly what 4CP tends to do: it punishes load that shows up during a tiny set of summer system peaks and mostly ignores behavior outside that window. The upside is simplicity. The downside is obvious too, it is the most gameable method in the comparison set, with a gaming score of **0.90** and a peak-dependence score of **1.00**.

### 4CP Net Load
4CP Net Load rewards the same narrow summer timing, but it punishes zones based on net rather than gross load. In this synthetic case that moves major burden toward `NORTH` (**38.66%**) and `HOUSTON` (**37.44%**) while pushing `WEST` to **-5.02%** because `WEST` is intentionally export-heavy during summer. That tells you the model is highly sensitive to export treatment and behind-the-meter behavior. It solves one blindness in plain 4CP, but it can swing hard enough to create negative obligations in synthetic edge cases, which is why its mean absolute shift versus 4CP is a large **9.27 percentage points**.

### 12CP
12CP rewards persistent contribution across all twelve monthly peaks rather than a four-interval summer ambush. That lowers the drama. In this run the shares are close to 4CP, but slightly flatter: `NORTH` **31.61%**, `HOUSTON` **29.33%**, `SOUTH` **23.29%**, `WEST` **15.77%**. It punishes zones that are consistently heavy through the year, not just opportunistically present in the summer peak. That is why it posts the smallest burden shift versus 4CP among the non-incumbent methods, only **1.13 percentage points**, while also improving gaming resistance relative to 4CP.

### 12CP Net Load
12CP Net Load rewards annual persistence on a net-load basis. In the synthetic fixture that again benefits the export-heavy `WEST`, driving it slightly negative at **-0.84%**, while increasing `NORTH` to **37.35%** and `HOUSTON` to **35.83%**. Compared with 4CP Net Load it is less extreme, because the burden is annualized over twelve peaks instead of four, but the same structural fact remains: if a zone is meaningfully export-heavy under the chosen preprocessing rule, net-load methods can treat it as a credit source rather than a cost causer. That makes it more gaming-resistant than 4CP variants, but still sensitive to preprocessing choices.

### Hybrid Volumetric + 12CP Net Load
The hybrid rewards two things at once: annual usage and net-load peak responsibility. In this run it lands in the middle almost everywhere: `NORTH` **35.05%**, `HOUSTON` **33.23%**, `SOUTH` **25.91%**, `WEST` **5.81%**. The volumetric leg keeps `WEST` from going negative, while the net-load leg still recognizes its export-heavy behavior. That makes the hybrid look like a stabilization mechanism. It punishes persistent consumption without letting one narrow proxy dominate. Its gaming score of **0.35** is materially better than the pure peak methods, though it still inherits some export-rule sensitivity from the net-load component.

### CBTCA
CBTCA rewards zones that look like persistent cost causers across both the operational ledger and the planning ledger. In this synthetic run it pushes the most burden onto `NORTH` at **43.82%**, keeps `HOUSTON` at **26.43%**, and cuts `SOUTH` to **15.52%**. `WEST` stays positive at **14.23%** despite its export-heavy net profile because CBTCA is not driven only by net-load peaks, it also sees congestion and planning stress. That is the key distinction. CBTCA punishes zones associated with transmission stress, not merely zones present at coincident load peaks. It also posts the lowest gaming score in the core comparison, **0.25**, because its signal is diversified across operational and planning evidence rather than concentrated in a few intervals.

### CBTCA Sensitivities
The sensitivity family row is not a seventh independent methodology so much as a summary of the CBTCA perturbation set. In the current run there are **19 scenarios**, with a **max zone delta of 0.1408** and a **mean zone delta of 0.0131** relative to the baseline CBTCA case. The framework labels that confidence as **High**. That does not mean CBTCA is proven true. It means the synthetic result is reasonably stable across the specified weight, proxy-tier, export-rule, planning-window, target-set-size, and outlier-cap variants. Reviewers should read this row as a robustness signal, not as an additional allocation rule.

## Key findings

### Which methodology best aligns with cost causation in this synthetic run?
**CBTCA** is the strongest cost-causation candidate in the current synthetic comparison.

Why:
- it is the only method here that explicitly blends operational congestion evidence with planning-ledger pressure
- it keeps `WEST` positive even though `WEST` is export-heavy, which better matches the idea that a zone can still drive transmission planning needs while exporting in some intervals
- it avoids the narrow-window distortions of 4CP and the over-crediting tendency visible in pure net-load methods

That said, this is still a synthetic judgment. The statement is: **CBTCA best aligns with the design intent of cost causation in this fixture**, not that it has won the real ERCOT argument.

### Which methodology is most resistant to gaming?
On the scorecard’s current heuristic, **CBTCA** is the most gaming-resistant core methodology with a gaming exposure score of **0.25**.

The ranking logic is straightforward:
- 4CP is most exposed because four intervals can be managed aggressively
- 12CP softens that by annualizing across twelve peaks
- net-load variants remain sensitive to export-rule engineering and DER timing
- the hybrid diversifies incentives but still inherits some net-load fragility
- CBTCA spreads the obligation signal across multiple congestion and planning indicators, which makes single-window gaming materially harder

## Burden-shift highlights versus 4CP
Relative to incumbent 4CP:
- **4CP Net Load** moves the most burden away from `WEST` and onto `NORTH` and `HOUSTON`
- **12CP** is the gentlest transition, with only **1.13 percentage points** of mean absolute share shift
- **Hybrid Vol + 12CP NL** is a middle path, softening the negative-`WEST` outcome seen in pure net-load methods
- **CBTCA** produces a more structural reallocation: `NORTH` rises by **11.42 points**, `SOUTH` falls by **8.49 points**, `HOUSTON` falls by **3.64 points**, and `WEST` rises modestly by **0.71 points**

## What this run does and does not prove
### It does show
- the seven-row scorecard can compare all implemented approaches on one input scaffold
- the methods produce materially different burden patterns under export-heavy and high-BTM conditions
- CBTCA behaves differently from both peak-only and net-load-only formulations in a way that is visible, not hand-waved

### It does not show
- real ERCOT bill impacts
- real TDSP or customer-class fairness
- empirical proof that any methodology here should be adopted
- empirical proof that the heuristic gaming scores are calibrated to field behavior

## Bottom line
The synthetic comparison is now strong enough to support external review of framework behavior.

It is not strong enough to justify policy triumphalism. That is fine. Better an honest synthetic result than a fake empirical one.
