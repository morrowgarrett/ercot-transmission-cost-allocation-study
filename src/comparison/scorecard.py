from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import pandas as pd

from src.comparison.metrics import (
    allocation_shares_by_zone,
    burden_shift_vs_baseline,
    concentration_metrics,
    gaming_exposure_metrics,
    revenue_sufficiency_check,
    summarize_sensitivity_family,
)
from src.models import (
    CBTCAModel,
    FourCPModel,
    FourCPNetLoadModel,
    HybridVol12CPNLModel,
    MethodologyInputs,
    MethodologyResult,
    TwelveCPModel,
    TwelveCPNetLoadModel,
    build_sensitivity_cases,
    load_sensitivity_matrix,
)


DEFAULT_MODEL_SPECS = [
    ("4cp", FourCPModel(), {}),
    ("4cp_net_load", FourCPNetLoadModel(), {}),
    ("12cp", TwelveCPModel(), {}),
    ("12cp_net_load", TwelveCPNetLoadModel(), {}),
    ("hybrid_vol_12cp_nl", HybridVol12CPNLModel(), {"alpha": 0.40}),
    ("cbtca", CBTCAModel(), {}),
]


def _derive_peak_maps(inputs: MethodologyInputs) -> tuple[Dict[str, str], Dict[str, str]]:
    annual = {key: value for key, value in inputs.peak_intervals.items() if key.startswith(f"{inputs.year}-")}
    summer = {key: value for key, value in annual.items() if key.split("-")[-1] in {"06", "07", "08", "09"}}
    return summer, annual


def _apply_peak_map(inputs: MethodologyInputs, peak_map: Dict[str, str]) -> MethodologyInputs:
    clone = deepcopy(inputs)
    clone.peak_intervals = peak_map
    return clone


def _default_sensitivity_matrix_path() -> str:
    return str(Path(__file__).resolve().parents[1] / "config" / "sensitivity_matrix.yaml")


def run_methodology_suite(
    inputs: MethodologyInputs,
    model_specs: Sequence[tuple[str, object, Dict]] | None = None,
) -> List[MethodologyResult]:
    model_specs = model_specs or DEFAULT_MODEL_SPECS
    summer_peaks, annual_peaks = _derive_peak_maps(inputs)
    results: List[MethodologyResult] = []
    for methodology_name, model, params in model_specs:
        model_inputs = inputs
        if methodology_name in {"4cp", "4cp_net_load"}:
            model_inputs = _apply_peak_map(inputs, summer_peaks)
        elif methodology_name in {"12cp", "12cp_net_load", "hybrid_vol_12cp_nl"}:
            model_inputs = _apply_peak_map(inputs, annual_peaks)
        result = model.run(model_inputs, params=params)
        result.methodology = methodology_name
        result.assumptions.setdefault("tcos_target_usd", inputs.tcos_target_usd)
        results.append(result)
    return results


def build_scorecard(
    results: Sequence[MethodologyResult],
    baseline_methodology: str = "4cp",
    cbtca_sensitivity_results: List[MethodologyResult] | None = None,
) -> pd.DataFrame:
    revenue = revenue_sufficiency_check(results)
    concentration = concentration_metrics(results)
    gaming = gaming_exposure_metrics(results)
    shifts = burden_shift_vs_baseline(results, baseline_methodology=baseline_methodology)
    if shifts.empty:
        avg_shift = pd.DataFrame(columns=["methodology", "mean_absolute_share_shift_vs_4cp"])
    else:
        avg_shift = (
            shifts.groupby("methodology", as_index=False)["share_shift"]
            .agg(lambda s: s.abs().mean())
            .rename(columns={"share_shift": "mean_absolute_share_shift_vs_4cp"})
        )

    scorecard = revenue.merge(concentration, on=["methodology", "year"], how="left")
    scorecard = scorecard.merge(gaming, on=["methodology", "year"], how="left")
    scorecard = scorecard.merge(avg_shift, on="methodology", how="left")
    scorecard["status"] = "complete"

    if cbtca_sensitivity_results is not None:
        baseline_cbtca = next(result for result in results if result.methodology == "cbtca")
        sensitivity_row = summarize_sensitivity_family(cbtca_sensitivity_results, baseline_cbtca)
        sensitivity_metrics = gaming_exposure_metrics(
            [MethodologyResult(methodology="cbtca_sensitivities", year=baseline_cbtca.year, shares={}, allocations_usd={})]
        ).iloc[0].to_dict()
        sensitivity_row.update(
            {
                "year": baseline_cbtca.year,
                "allocated_total_usd": sum(baseline_cbtca.allocations_usd.values()),
                "allocated_tcos_usd": sum(baseline_cbtca.allocations_usd.values()),
                "target_total_usd": baseline_cbtca.assumptions.get("tcos_target_usd", sum(baseline_cbtca.allocations_usd.values())),
                "target_tcos_usd": baseline_cbtca.assumptions.get("tcos_target_usd", sum(baseline_cbtca.allocations_usd.values())),
                "difference_usd": 0.0,
                "gap_usd": 0.0,
                "within_tolerance": True,
                "revenue_sufficient": True,
                "hhi": scorecard.loc[scorecard["methodology"] == "cbtca", "hhi"].iloc[0],
                "max_zone_share": scorecard.loc[scorecard["methodology"] == "cbtca", "max_zone_share"].iloc[0],
                "zone_count": scorecard.loc[scorecard["methodology"] == "cbtca", "zone_count"].iloc[0],
                "mean_absolute_share_shift_vs_4cp": None,
                "status": "scenario_family",
                **{k: v for k, v in sensitivity_metrics.items() if k not in {"methodology", "year"}},
            }
        )
        scorecard = pd.concat([scorecard, pd.DataFrame([sensitivity_row])], ignore_index=True, sort=False)

    return scorecard.sort_values(["year", "methodology"]).reset_index(drop=True)


def build_scorecard_table(
    results: Sequence[MethodologyResult],
    cbtca_sensitivity_results: List[MethodologyResult],
    target_tcos_usd: float,
) -> pd.DataFrame:
    scorecard = build_scorecard(results, cbtca_sensitivity_results=cbtca_sensitivity_results)
    scorecard.loc[scorecard["methodology"] == "cbtca_sensitivities", ["target_total_usd", "target_tcos_usd"]] = target_tcos_usd
    return scorecard


def build_comparison_bundle(
    inputs: MethodologyInputs,
    sensitivity_params: Iterable[Dict] | None = None,
    baseline_methodology: str = "4cp",
) -> Dict[str, pd.DataFrame | List[MethodologyResult]]:
    results = run_methodology_suite(inputs)
    if sensitivity_params is not None:
        cbtca_sensitivity_results = []
        for scenario in sensitivity_params:
            result = CBTCAModel().run(inputs, params=scenario)
            label = scenario.get("label", "unnamed")
            result.methodology = f"cbtca_sensitivity_{label}"
            result.assumptions["sensitivity_family"] = "ad_hoc"
            result.assumptions["sensitivity_label"] = label
            cbtca_sensitivity_results.append(result)
    else:
        matrix = load_sensitivity_matrix(_default_sensitivity_matrix_path())
        cbtca_sensitivity_results = build_sensitivity_cases(inputs, matrix=matrix)

    return {
        "results": results,
        "cbtca_sensitivity_results": cbtca_sensitivity_results,
        "allocation_shares": allocation_shares_by_zone(results),
        "burden_shift": burden_shift_vs_baseline(results, baseline_methodology=baseline_methodology),
        "scorecard": build_scorecard(results, baseline_methodology=baseline_methodology, cbtca_sensitivity_results=cbtca_sensitivity_results),
    }


def run_comparison_bundle(
    inputs: MethodologyInputs,
    model_params: Dict[str, Dict] | None = None,
    sensitivity_matrix_path: str | None = None,
) -> Dict[str, object]:
    model_params = model_params or {}
    results = []
    summer_peaks, annual_peaks = _derive_peak_maps(inputs)
    for methodology_name, model, default_params in DEFAULT_MODEL_SPECS:
        params = {**default_params, **model_params.get(methodology_name, {})}
        model_inputs = inputs
        if methodology_name in {"4cp", "4cp_net_load"}:
            model_inputs = _apply_peak_map(inputs, summer_peaks)
        elif methodology_name in {"12cp", "12cp_net_load", "hybrid_vol_12cp_nl"}:
            model_inputs = _apply_peak_map(inputs, annual_peaks)
        result = model.run(model_inputs, params=params)
        result.methodology = methodology_name
        result.assumptions.setdefault("tcos_target_usd", inputs.tcos_target_usd)
        results.append(result)

    matrix_path = sensitivity_matrix_path or _default_sensitivity_matrix_path()
    matrix = load_sensitivity_matrix(matrix_path)
    cbtca_sensitivity_results = build_sensitivity_cases(inputs, params=model_params.get("cbtca", {}), matrix=matrix)
    return {
        "results": results,
        "cbtca_sensitivity_results": cbtca_sensitivity_results,
        "scorecard": build_scorecard_table(results, cbtca_sensitivity_results, inputs.tcos_target_usd),
        "allocations_by_zone": allocation_shares_by_zone(results),
        "burden_shift": burden_shift_vs_baseline(results),
    }
