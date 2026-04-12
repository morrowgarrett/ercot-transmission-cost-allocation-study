from __future__ import annotations

from typing import Dict, Iterable, List


def apply_export_rule(raw_rows: Iterable[dict], rule: str) -> List[dict]:
    """Apply export preprocessing Rule A/B/C to raw net-load-like rows.

    Expected row shape includes:
    - timestamp
    - zone
    - raw_net_load_mw

    Returns rows with `load_mw` and optional export indicators.
    This module centralizes preprocessing so v1 baseline models can consume
    already-processed `net_zonal_load` inputs.
    """
    out = []
    for row in raw_rows:
        raw = float(row['raw_net_load_mw'])
        if rule == 'A':
            out.append({**row, 'load_mw': max(0.0, raw)})
        elif rule == 'B':
            out.append({**row, 'load_mw': raw})
        elif rule == 'C':
            export_mw = max(0.0, -raw)
            out.append({
                **row,
                'load_mw': max(0.0, raw),
                'export_mw': export_mw,
                'export_interval_flag': 1 if export_mw > 0 else 0,
            })
        else:
            raise ValueError(f'Unknown export rule: {rule}')
    return out
