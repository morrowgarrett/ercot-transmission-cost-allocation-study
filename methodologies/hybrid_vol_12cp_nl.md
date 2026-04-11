# Volumetric + 12CP Net Load Hybrid

## Formula
Share_VOL(u,y) = sum_t E(u,t) / sum_j sum_t E(j,t)

Share_12CPNL(u,y) = CP12_NL(u,y) / sum_j CP12_NL(j,y)

Share_HYB(u,y) = alpha * Share_VOL(u,y) + (1-alpha) * Share_12CPNL(u,y)

## Default presentation case
alpha = 0.40

## Annualization logic
Annual volumetric usage blended with twelve monthly net-load coincident peak shares.

## DER / BTM / storage treatment
Volumetric component reflects measured consumption basis. Peak component reflects net-load treatment, including storage charging/discharging and the chosen export rule.


## Export rule application note
Rules A, B, and C are applied during preprocessing. These models expect `net_zonal_load` to already reflect the chosen export rule, and they record `metadata.export_rule` for auditability.
## Export treatment
Peak component must be tested under Rules A, B, and C. Volumetric component does not grant negative export credit in the base case.

## Required sensitivities
20/80, 40/60, 50/50, 60/40, 80/20.

## Why 40/60 is only a presentation anchor
It weights peak responsibility slightly more than volumetric usage and provides contrast with both pure peak and balanced formulations. It is not a normative recommendation.
