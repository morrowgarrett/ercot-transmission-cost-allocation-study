# CBTCA

## Operational ledger proxy hierarchy
### Tier 1
Use direct congestion component if available.

### Tier 2
Use LMP - energy component - loss component if all fields are available.

### Tier 3
Use LMP - system lambda only when Tier 1 and Tier 2 are unavailable.
This is a congestion-plus-loss proxy, not pure congestion.

## Operational burden
OperationalBurdenRaw(u,y) = sum_t Proxy(u,t) * LoadBasis_operational(u,t)

Base-case operational load basis: gross load.
Net-aware operational sensitivities may also be tested.

## DER / BTM / storage treatment
Base case uses gross-load burden for operational scaling. Sensitivity runs may use net-aware load basis to test whether local offsets materially change inferred congestion burden.

## Export treatment
Exports are not directly credited in the base case. Net-aware sensitivities may test export Rules A, B, and C when the operational burden basis is switched from gross to net-aware load.

## Planning ledger
### Base-case reference window
Full calendar year.

### Base-case planning load basis
Gross load.

### Constraint score
ConstraintScore(c,W) = sum_{t in W} max(0, ShadowPrice(c,t)) * BindingFlag(c,t)

### Target set
C* = Top 20 constraints by ConstraintScore(c,W)
Sensitivity: Top 10, Top 40.

### Zone exposure proxy
Exposure(u,c,W) = [sum_{t in W_c} LoadBasis_planning(u,t) * CongestionProxy(u,t)] / [sum_j sum_{t in W_c} LoadBasis_planning(j,t) * CongestionProxy(j,t)]

### Planning burden
PlanningBurdenRaw(u,y) = sum_{c in C*} ConstraintScore(c,W) * Exposure(u,c,W)

Share_Planning(u,y) = PlanningBurdenRaw(u,y) / sum_j PlanningBurdenRaw(j,y)

## Combined share
Share_CBTCA(u,y) = w_o * Share_Operational(u,y) + w_p * Share_Planning(u,y)

Base case: w_o = 0.40, w_p = 0.60.

## Operational-ledger unavailable fallback
If no operational proxy tier is available, CBTCA runs in planning-only fallback mode:
- Share_CBTCA_fallback(u,y) = Share_Planning(u,y)
- output must be tagged `planning_only_fallback`
- confidence cannot exceed Low unless operational proxy is restored
