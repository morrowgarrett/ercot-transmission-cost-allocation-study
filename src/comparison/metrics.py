from __future__ import annotations

from typing import Dict, Iterable, List

import pandas as pd

from src.models.base import MethodologyResult


GAMING_EXPOSURE_SCORES = {
    "4cp": {"gaming_exposure_score": 0.90, "peak_dependence_score": 1.00, "annualization_score": 0.05},
    "4cp_net_load": {"gaming_exposure_score": 0.75, "peak_dependence_score": 1.00, "annualization_score": 0.10},
    "12cp": {"gaming_exposure_score": 0.55, "peak_dependence_score": 0.70, "annualization_score": 0.35},
    "12cp_net_load": {"gaming_exposure_score": 0.45, "peak_dependence_score": 0.70, "annualization_score": 0.40},
    "hybrid_vol_12cp_nl": {"gaming_exposure_score": 0.35, "peak_dependence_score": 0.45, "annualization_score": 0.60},
    "cbtca": {"gaming_exposure_score": 0.25, "peak_dependence_score": 0.20, "annualization_score": 0.80},
    "cbtca_sensitivities": {"gaming_exposure_score": 0.30, "peak_dependence_score": 0.25, "annualization_score": 0.75},
}


def allocation_shares_by_zone(results: Iterable[MethodologyResult]) -> pd.DataFrame:
    rows: List[dict] = []
    for result in results:
        total = sum(result.allocations_usd.values()) or 1.0
        for zone, share in sorted(result.shares.items()):
            rows.append(
                {
                    "methodology": result.methodology,
                    "year": result.year,
                    "zone": zone,
                    "share": share,
                    "allocation_usd": result.allocations_usd.get(zone, 0.0),
                    "allocation_pct": result.allocations_usd.get(zone, 0.0) / total,
                }
            )
    return pd.DataFrame(rows)


def allocations_by_zone(results: Iterable[MethodologyResult]) -> pd.DataFrame:
    return allocation_shares_by_zone(results)


def burden_shift_vs_baseline(results: Iterable[MethodologyResult], baseline_methodology: str = "4cp") -> pd.DataFrame:
    result_map = {result.methodology: result for result in results}
    if baseline_methodology not in result_map:
        raise ValueError(f"baseline methodology {baseline_methodology!r} not found")
    baseline = result_map[baseline_methodology]
    rows: List[dict] = []
    for methodology, result in result_map.items():
        if methodology == baseline_methodology:
            continue
        zones = set(baseline.shares) | set(result.shares)
        for zone in sorted(zones):
            baseline_share = baseline.shares.get(zone, 0.0)
            candidate_share = result.shares.get(zone, 0.0)
            rows.append(
                {
                    "baseline_methodology": baseline_methodology,
                    "methodology": methodology,
                    "year": result.year,
                    "zone": zone,
                    "baseline_share": baseline_share,
                    "incumbent_share": baseline_share,
                    "candidate_share": candidate_share,
                    "share": candidate_share,
                    "share_shift": candidate_share - baseline_share,
                    "allocation_shift_usd": result.allocations_usd.get(zone, 0.0) - baseline.allocations_usd.get(zone, 0.0),
                }
            )
    return pd.DataFrame(rows)


def burden_shift_vs_incumbent(results: Iterable[MethodologyResult], incumbent: str = "4cp") -> pd.DataFrame:
    return burden_shift_vs_baseline(results, baseline_methodology=incumbent)


def revenue_sufficiency_check(results: Iterable[MethodologyResult], tolerance: float = 1e-6) -> pd.DataFrame:
    rows: List[dict] = []
    for result in results:
        total = sum(result.allocations_usd.values())
        target = float(result.assumptions.get("tcos_target_usd", total))
        rows.append(
            {
                "methodology": result.methodology,
                "year": result.year,
                "allocated_total_usd": total,
                "allocated_tcos_usd": total,
                "target_total_usd": target,
                "target_tcos_usd": target,
                "difference_usd": total - target,
                "gap_usd": total - target,
                "within_tolerance": abs(total - target) <= tolerance,
                "revenue_sufficient": abs(total - target) <= tolerance,
            }
        )
    return pd.DataFrame(rows)


def revenue_sufficiency(results: Iterable[MethodologyResult], target_tcos_usd: float | None = None) -> pd.DataFrame:
    frame = revenue_sufficiency_check(results)
    if target_tcos_usd is not None:
        frame["target_tcos_usd"] = target_tcos_usd
        frame["gap_usd"] = frame["allocated_tcos_usd"] - target_tcos_usd
        frame["revenue_sufficient"] = frame["gap_usd"].abs() <= 1e-6
    return frame


def concentration_metrics(results: Iterable[MethodologyResult]) -> pd.DataFrame:
    rows: List[dict] = []
    for result in results:
        shares = list(result.shares.values())
        hhi = sum(share * share for share in shares)
        max_share = max(shares) if shares else 0.0
        rows.append(
            {
                "methodology": result.methodology,
                "year": result.year,
                "hhi": hhi,
                "max_zone_share": max_share,
                "zone_count": len(shares),
            }
        )
    return pd.DataFrame(rows)


def gaming_exposure_metrics(results: Iterable[MethodologyResult]) -> pd.DataFrame:
    rows: List[dict] = []
    for result in results:
        key = result.methodology
        if key.startswith("cbtca_sensitivity"):
            key = "cbtca_sensitivities"
        scores = GAMING_EXPOSURE_SCORES.get(
            key,
            {"gaming_exposure_score": 0.50, "peak_dependence_score": 0.50, "annualization_score": 0.50},
        )
        rows.append(
            {
                "methodology": result.methodology,
                "year": result.year,
                **scores,
                "gaming_exposure_label": "higher is worse",
            }
        )
    return pd.DataFrame(rows)


def summarize_sensitivity_family(results: List[MethodologyResult], baseline: MethodologyResult) -> Dict[str, float | str]:
    if not results:
        return {
            "methodology": "cbtca_sensitivities",
            "scenario_count": 0,
            "max_zone_delta": 0.0,
            "mean_zone_delta": 0.0,
            "confidence": baseline.assumptions.get("confidence", "Low"),
        }

    deltas = []
    for result in results:
        all_zones = set(result.shares) | set(baseline.shares)
        deltas.extend(abs(result.shares.get(zone, 0.0) - baseline.shares.get(zone, 0.0)) for zone in all_zones)
    return {
        "methodology": "cbtca_sensitivities",
        "scenario_count": len(results),
        "max_zone_delta": max(deltas) if deltas else 0.0,
        "mean_zone_delta": sum(deltas) / len(deltas) if deltas else 0.0,
        "confidence": baseline.assumptions.get("confidence", "Low"),
    }
