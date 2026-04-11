from __future__ import annotations

from typing import Any, Dict

from .base import MethodologyInputs, MethodologyResult
from .four_cp import FourCPModel


class TwelveCPModel(FourCPModel):
    name = "12cp"

    def _validate_peak_intervals(self, peak_intervals: Dict[str, str]) -> None:
        if not peak_intervals:
            raise ValueError("peak_intervals must map all calendar months to coincident-peak timestamps")
        months = {key.split('-')[-1] for key in peak_intervals.keys()}
        expected = {f"{m:02d}" for m in range(1, 13)}
        if months != expected or len(peak_intervals) != 12:
            raise ValueError("TwelveCPModel requires exactly twelve peak intervals for months 01 through 12")

    def run(self, inputs: MethodologyInputs, params: Dict[str, Any] | None = None) -> MethodologyResult:
        self._validate_peak_intervals(inputs.peak_intervals)
        target_timestamps = set(inputs.peak_intervals.values())
        zone_totals, warnings = self._select_rows(inputs.zonal_load, target_timestamps)
        grand_total = sum(zone_totals.values())
        if grand_total <= 0:
            raise ValueError("matched coincident-peak zonal loads must sum to a positive value")

        shares = {zone: total / grand_total for zone, total in zone_totals.items()}
        allocations = {zone: share * inputs.tcos_target_usd for zone, share in shares.items()}
        return MethodologyResult(
            methodology=self.name,
            year=inputs.year,
            shares=shares,
            allocations_usd=allocations,
            assumptions={
                "peak_intervals": inputs.peak_intervals,
                "load_basis": "gross",
                "note": "12CP baseline implementation using provided monthly coincident-peak timestamps",
            },
            warnings=warnings,
        )
