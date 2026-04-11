from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict

from .base import MethodologyInputs, MethodologyModel, MethodologyResult
from .twelve_cp_net_load import TwelveCPNetLoadModel


class HybridVol12CPNLModel(MethodologyModel):
    name = "hybrid_vol_12cp_nl"

    def run(self, inputs: MethodologyInputs, params: Dict[str, Any] | None = None) -> MethodologyResult:
        params = params or {}
        alpha = float(params.get("alpha", 0.40))
        if not 0.0 <= alpha <= 1.0:
            raise ValueError("alpha must be between 0 and 1")

        if not inputs.zonal_load:
            raise ValueError("zonal_load is required for HybridVol12CPNLModel volumetric component")

        vol_totals = defaultdict(float)
        for row in inputs.zonal_load:
            vol_totals[row["zone"]] += float(row["load_mw"])
        vol_total = sum(vol_totals.values())
        if vol_total <= 0:
            raise ValueError("zonal_load volumetric totals must sum to a positive value")
        vol_shares = {zone: total / vol_total for zone, total in vol_totals.items()}

        peak_result = TwelveCPNetLoadModel().run(inputs, params=params)
        peak_shares = peak_result.shares

        all_zones = set(vol_shares) | set(peak_shares)
        shares = {
            zone: alpha * vol_shares.get(zone, 0.0) + (1 - alpha) * peak_shares.get(zone, 0.0)
            for zone in all_zones
        }
        total_share = sum(shares.values())
        if total_share <= 0:
            raise ValueError("hybrid shares must sum to a positive value")
        shares = {zone: value / total_share for zone, value in shares.items()}
        allocations = {zone: share * inputs.tcos_target_usd for zone, share in shares.items()}

        warnings = list(peak_result.warnings)
        return MethodologyResult(
            methodology=self.name,
            year=inputs.year,
            shares=shares,
            allocations_usd=allocations,
            assumptions={
                "alpha": alpha,
                "volumetric_load_basis": "gross",
                "peak_component": "12cp_net_load",
                "export_rule": inputs.metadata.get("export_rule", "unspecified"),
                "preprocessing_required": True,
            },
            warnings=warnings,
        )
