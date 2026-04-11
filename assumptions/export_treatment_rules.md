# Export Treatment Rules

Rules A, B, and C are preprocessing rules applied before net-load model execution. Net-load models consume `net_zonal_load` that should already reflect the selected rule. The selected rule must also be passed as `metadata.export_rule`.

## Rule A
Floor exports at zero obligation.

## Rule B
Allow signed net load, including negative values.

## Rule C
Use zero-floor obligation plus a separate export usage indicator:
- export_mw = max(0, -raw_net_load)
- export_interval_flag = 1 if export_mw > 0 else 0
- export_share_of_peak = export_mw / sum(export_mw across units) when applicable

Rule C does not grant direct negative allocation. It surfaces export intensity for reporting and sensitivity analysis.
