import pytest

from src.comparison.metrics import (
    allocation_shares_by_zone,
    burden_shift_vs_baseline,
    concentration_metrics,
    gaming_exposure_metrics,
    revenue_sufficiency_check,
)
from src.comparison.scorecard import build_comparison_bundle, build_scorecard, run_methodology_suite
from src.comparison.synthetic_data import build_four_zone_synthetic_inputs, synthetic_dataset_metadata


def _comparison_inputs():
    return build_four_zone_synthetic_inputs()


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
    assert set(shares["zone"]) == {"NORTH", "SOUTH", "WEST", "HOUSTON"}


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


def test_synthetic_fixture_includes_high_btm_and_export_heavy_zone_behavior():
    inputs = _comparison_inputs()
    west_net = [row["load_mw"] for row in inputs.net_zonal_load if row["zone"] == "WEST"]
    houston_gross = [row["load_mw"] for row in inputs.zonal_load if row["zone"] == "HOUSTON"]
    assert min(west_net) < 0.0
    assert max(houston_gross) > max(row["load_mw"] for row in inputs.zonal_load if row["zone"] == "WEST")


def test_synthetic_fixture_metadata_documents_synthetic_vs_real_boundaries():
    metadata = synthetic_dataset_metadata()
    assert metadata.name == "four_zone_v1"
    assert "net_zonal_load" in metadata.synthetic_fields
    assert "shadow_price_series" in metadata.real_data_mapping
    assert any("export-heavy" in note or "high-BTM" in note for note in metadata.edge_cases)
