# ERCOT 4CP

## Formula
For June through September, let CP_m be the system coincident peak interval.

CP4(u,y) = (1/4) * sum_{m=6..9} L_gross(u, CP_m)

Share_4CP(u,y) = CP4(u,y) / sum_j CP4(j,y)

Alloc_4CP(u,y) = Share_4CP(u,y) * TCOS(y)

## Settlement interval
15-minute preferred, hourly fallback allowed.

## Annualization logic
One monthly summer system peak per month, averaged into annual obligation.

## DER / BTM / storage treatment
Gross-load basis. To the extent BTM generation reduces metered gross load, it lowers observed obligation indirectly. No explicit separate DER or storage adjustment is performed in the base formulation.

## Export treatment
No explicit export credit. Gross-load formulation generally makes exports invisible unless they reduce measured load.

## Cost recovery target
Full annual TCOS.

## Allocation unit
Zone, TDSP overlay, proxy-class overlay.

## Incentive effects
Concentrates value into a few summer intervals, making short-window gaming highly effective.
