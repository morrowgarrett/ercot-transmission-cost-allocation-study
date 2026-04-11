from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, Tuple

from .base import MethodologyInputs, MethodologyModel, MethodologyResult


class FourCPModel(MethodologyModel):
    name = "4cp"
    required_months = {"06", "07", "08", "09"}

    def _validate_peak_intervals(self, peak_intervals: Dict[str, str]) -> None:
        if not peak_intervals:
            raise ValueError("peak_intervals must map summer months to coincident-peak timestamps")
        months = {key.split('-')[-1] for key in peak_intervals.keys()}
        if months != self.required_months or len(peak_intervals) != 4:
            raise ValueError("FourCPModel requires exactly four peak intervals for months 06, 07, 08, and 09")

    def _select_rows(self, rows: Iterable[Dict[str, Any]], target_timestamps: set[str]) -> Tuple[defaultdict[str, float], list[str]]:
        zone_totals = defaultdict(float)
        matched_rows = 0
        seen = set()
        warnings: list[str] = []
        duplicate_count = 0
        for row in rows:
            ts = row.get("timestamp")
            if ts in target_timestamps:
                zone = row["zone"]
                key = (zone, ts)
                if key in seen:
                    duplicate_count += 1
                else:
                    seen.add(key)
                zone_totals[zone] += float(row["load_mw"])
                matched_rows += 1
        if matched_rows == 0:
            raise ValueError("no zonal load rows matched the provided peak_intervals")
        if duplicate_count:
            warnings.append(f"detected {duplicate_count} duplicate zone+timestamp rows; values were summed")
        return zone_totals, warnings

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
                "note": "4CP baseline implementation using provided summer coincident-peak timestamps",
            },
            warnings=warnings,
        )
