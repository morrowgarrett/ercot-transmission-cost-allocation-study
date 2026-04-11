from __future__ import annotations

from typing import Any, Dict

from .base import MethodologyInputs, MethodologyResult
from .twelve_cp import TwelveCPModel


class TwelveCPNetLoadModel(TwelveCPModel):
    name = "12cp_net_load"

    def run(self, inputs: MethodologyInputs, params: Dict[str, Any] | None = None) -> MethodologyResult:
        self._validate_peak_intervals(inputs.peak_intervals)
        if not inputs.net_zonal_load:
            raise ValueError("net_zonal_load is required for TwelveCPNetLoadModel")
        target_timestamps = set(inputs.peak_intervals.values())
        zone_totals, warnings = self._select_rows(inputs.net_zonal_load, target_timestamps)
        grand_total = sum(zone_totals.values())
        if grand_total <= 0:
            raise ValueError("matched coincident-peak net zonal loads must sum to a positive value")

        shares = {zone: total / grand_total for zone, total in zone_totals.items()}
        allocations = {zone: share * inputs.tcos_target_usd for zone, share in shares.items()}
        export_rule = inputs.metadata.get("export_rule", "unspecified")
        if export_rule == "unspecified":
            warnings.append("export_rule metadata not provided")
        return MethodologyResult(
            methodology=self.name,
            year=inputs.year,
            shares=shares,
            allocations_usd=allocations,
            assumptions={
                "peak_intervals": inputs.peak_intervals,
                "load_basis": "net",
                "export_rule": export_rule,
                "preprocessing_required": True,
            },
            warnings=warnings,
        )
