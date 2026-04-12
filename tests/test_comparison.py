import pytest

from src.comparison.metrics import (
    allocation_shares_by_zone,
    burden_shift_vs_baseline,
    concentration_metrics,
    gaming_exposure_metrics,
    revenue_sufficiency_check,
)
from src.comparison.scorecard import build_comparison_bundle, build_scorecard, run_methodology_suite
from src.models.base import MethodologyInputs


def _summer_peaks():
    return {
        "2024-06": "2024-06-15T17:00:00Z",
        "2024-07": "2024-07-15T17:00:00Z",
        "2024-08": "2024-08-15T17:00:00Z",
        "2024-09": "2024-09-15T17:00:00Z",
    }


def _yearly_peaks():
    return {f"2024-{m:02d}": f"2024-{m:02d}-15T17:00:00Z" for m in range(1, 13)}


def _comparison_inputs():
    zonal_load = []
    net_zonal_load = []
    zonal_lmp_series = []
    system_lambda_series = []
    congestion_series = []
    shadow_price_series = []

    for m in range(1, 13):
        ts = f"2024-{m:02d}-15T17:00:00Z"
        zonal_load.extend(
            [
                {"timestamp": ts, "zone": "NORTH", "load_mw": 100.0 + m},
                {"timestamp": ts, "zone": "SOUTH", "load_mw": 90.0 + (13 - m)},
            ]
        )
        net_zonal_load.extend(
            [
                {"timestamp": ts, "zone": "NORTH", "load_mw": 80.0 + m},
                {"timestamp": ts, "zone": "SOUTH", "load_mw": 85.0 + (13 - m)},
            ]
        )
        zonal_lmp_series.extend(
            [
                {"timestamp": ts, "zone": "NORTH", "lmp": 36.0, "energy_component": 20.0, "loss_component": 4.0},
                {"timestamp": ts, "zone": "SOUTH", "lmp": 28.0, "energy_component": 20.0, "loss_component": 3.0},
            ]
        )
        system_lambda_series.append({"timestamp": ts, "system_lambda": 20.0})
        congestion_series.extend(
            [
                {"timestamp": ts, "zone": "NORTH", "congestion_component": 12.0},
                {"timestamp": ts, "zone": "SOUTH", "congestion_component": 5.0},
            ]
        )
        shadow_price_series.extend(
            [
                {"timestamp": ts, "constraint": "WEST_PATH", "shadow_price": 20.0, "binding_flag": 1},
                {"timestamp": ts, "constraint": "COAST_PATH", "shadow_price": 10.0, "binding_flag": 1},
            ]
        )

    return MethodologyInputs(
        year=2024,
        tcos_target_usd=1000.0,
        peak_intervals=_yearly_peaks(),
        zonal_load=zonal_load,
        net_zonal_load=net_zonal_load,
        zonal_lmp_series=zonal_lmp_series,
        system_lambda_series=system_lambda_series,
        congestion_series=congestion_series,
        shadow_price_series=shadow_price_series,
        metadata={"export_rule": "A"},
    )


def test_run_methodology_suite_returns_all_core_models():
    results = run_methodology_suite(_comparison_inputs())
    names = {result.methodology for result in results}
    assert names == {"4cp", "4cp_net_load", "12cp", "12cp_net_load", "hybrid_vol_12cp_nl", "cbtca"}


def test_build_comparison_bundle_scorecard_contains_all_seven_methodologies():
    bundle = build_comparison_bundle(_comparison_inputs())
    names = set(bundle["scorecard"]["methodology"])
    assert names == {"4cp", "4cp_net_load", "12cp", "12cp_net_load", "hybrid_vol_12cp_nl", "cbtca", "cbtca_sensitivities"}


def test_metric_tables_have_expected_columns():
    results = run_methodology_suite(_comparison_inputs())
    shares = allocation_shares_by_zone(results)
    shifts = burden_shift_vs_baseline(results)
    revenue = revenue_sufficiency_check(results)
    concentration = concentration_metrics(results)

    assert {"methodology", "zone", "share", "allocation_usd"}.issubset(shares.columns)
    assert {"methodology", "zone", "share_shift", "allocation_shift_usd"}.issubset(shifts.columns)
    assert revenue["within_tolerance"].all()
    assert {"methodology", "hhi", "max_zone_share"}.issubset(concentration.columns)


def test_scorecard_and_bundle_include_sensitivity_family_row():
    bundle = build_comparison_bundle(
        _comparison_inputs(),
        sensitivity_params=[{"label": "weights_50_50", "operational_weight": 0.5, "planning_weight": 0.5}],
    )
    scorecard = bundle["scorecard"]
    assert "cbtca_sensitivities" in set(scorecard["methodology"])
    assert scorecard.loc[scorecard["methodology"] == "cbtca_sensitivities", "status"].iloc[0] == "scenario_family"
    assert not bundle["allocation_shares"].empty
    assert not bundle["burden_shift"].empty


def test_burden_shift_vs_4cp_is_calculated_correctly_for_known_case():
    results = run_methodology_suite(_comparison_inputs())
    shifts = burden_shift_vs_baseline(results)
    row = shifts[(shifts["methodology"] == "cbtca") & (shifts["zone"] == "NORTH")].iloc[0]
    baseline = next(result for result in results if result.methodology == "4cp")
    cbtca = next(result for result in results if result.methodology == "cbtca")
    assert row["baseline_share"] == pytest.approx(baseline.shares["NORTH"])
    assert row["candidate_share"] == pytest.approx(cbtca.shares["NORTH"])
    assert row["share_shift"] == pytest.approx(cbtca.shares["NORTH"] - baseline.shares["NORTH"])


def test_gaming_exposure_metrics_include_cbtca_sensitivity_family_scores():
    bundle = build_comparison_bundle(_comparison_inputs())
    metrics = gaming_exposure_metrics(
        [type("R", (), {"methodology": "cbtca_sensitivities", "year": 2024})()]
    )
    row = metrics.iloc[0]
    assert row["gaming_exposure_score"] == pytest.approx(0.30)
    assert row["peak_dependence_score"] == pytest.approx(0.25)
    assert row["annualization_score"] == pytest.approx(0.75)


def test_scorecard_retains_baseline_rows():
    results = run_methodology_suite(_comparison_inputs())
    scorecard = build_scorecard(results)
    baseline = scorecard[scorecard["methodology"] == "4cp"]
    assert len(baseline) == 1
    assert bool(baseline.iloc[0]["within_tolerance"]) is True
