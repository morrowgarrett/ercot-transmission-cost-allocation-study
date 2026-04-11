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
