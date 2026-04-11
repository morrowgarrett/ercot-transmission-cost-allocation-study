# 12CP Net Load

## Formula
CP12_NL(u,y) = (1/12) * sum_{m=1..12} NL(u, CP_m)

Share_12CPNL(u,y) = CP12_NL(u,y) / sum_j CP12_NL(j,y)

## Settlement interval
15-minute preferred.

## Annualization logic
Twelve monthly coincident peaks averaged on a net-load basis.

## DER / BTM / storage treatment
Local generation and storage behavior are directly reflected through the chosen net-load rule.


## Export rule application note
Rules A, B, and C are applied during preprocessing. These models expect `net_zonal_load` to already reflect the chosen export rule, and they record `metadata.export_rule` for auditability.
## Export treatment
Must be run under Rules A, B, and C.

## Cost recovery target
Full annual TCOS.

## Incentive effects
A strong moderate-reform candidate: broader than 4CP, still legible, and more aware of on-site offsets.
