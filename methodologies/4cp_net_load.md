# 4CP Net Load

## Formula
CP4_NL(u,y) = (1/4) * sum_{m=6..9} NL(u, CP_m)

Share_4CPNL(u,y) = CP4_NL(u,y) / sum_j CP4_NL(j,y)

## Settlement interval
15-minute preferred.

## Annualization logic
Same four summer coincident peak intervals as incumbent 4CP, but on a net-load basis.

## DER / BTM / storage treatment
Local generation offsets load. Storage charging increases net load; storage discharge reduces it. Net effect depends on the export-treatment rule in use.


## Export rule application note
Rules A, B, and C are applied during preprocessing. These models expect `net_zonal_load` to already reflect the chosen export rule, and they record `metadata.export_rule` for auditability.
## Export treatment
Must be run under Rules A, B, and C.

## Cost recovery target
Full annual TCOS.

## Incentive effects
Preserves 4CP structure while recognizing load-offset behavior, but remains narrow-window gameable and sensitive to export treatment.
