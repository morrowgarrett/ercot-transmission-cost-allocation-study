from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class MethodologyInputs:
    year: int
    tcos_target_usd: float
    system_load: List[Dict[str, Any]] = field(default_factory=list)
    zonal_load: List[Dict[str, Any]] = field(default_factory=list)
    net_zonal_load: List[Dict[str, Any]] = field(default_factory=list)
    peak_intervals: Dict[str, str] = field(default_factory=dict)
    zonal_lmp_series: List[Dict[str, Any]] = field(default_factory=list)
    system_lambda_series: List[Dict[str, Any]] = field(default_factory=list)
    congestion_series: List[Dict[str, Any]] = field(default_factory=list)
    shadow_price_series: List[Dict[str, Any]] = field(default_factory=list)
    zone_shift_factors: Dict[str, Dict[str, float]] = field(default_factory=dict)
    planning_facilities: List[Dict[str, Any]] = field(default_factory=list)
    planning_constraint_summary: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MethodologyResult:
    methodology: str
    year: int
    shares: Dict[str, float]
    allocations_usd: Dict[str, float]
    assumptions: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


class MethodologyModel:
    name = "base"

    def run(self, inputs: MethodologyInputs, params: Dict[str, Any] | None = None) -> MethodologyResult:
        raise NotImplementedError
