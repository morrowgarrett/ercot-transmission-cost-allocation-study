# Net Load Definition

Base raw net load:
raw_net_load(u,t) = L_gross(u,t) - G_local(u,t) - S_dis(u,t) + S_chg(u,t)

## Rule A, floor at zero
NL_A(u,t) = max(0, raw_net_load(u,t))

## Rule B, signed net load
NL_B(u,t) = raw_net_load(u,t)

## Rule C, export-neutral with explicit export indicator
NL_C(u,t) = max(0, raw_net_load(u,t))
ExportIndicator(u,t) = max(0, -raw_net_load(u,t))

Rule C does not grant direct negative allocation. It records export intensity separately so net-exporting intervals are visible in reporting and sensitivity analysis.
