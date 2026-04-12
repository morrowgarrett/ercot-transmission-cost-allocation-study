import os
import pytest

from src.models import CBTCAModel, CBTCASensitivityModel, MethodologyInputs, build_sensitivity_cases, load_sensitivity_matrix

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _yearly_peaks():
    return {f"2024-{m:02d}": f"2024-{m:02d}-15T17:00:00Z" for m in range(1, 13)}


def _seasonal_inputs(include_direct_congestion=True, include_decomposed=True):
    zonal_load = []
    net_zonal_load = []
    zonal_lmp_series = []
    system_lambda_series = []
    congestion_series = []
    shadow_price_series = []

    for m in range(1, 13):
        ts = f"2024-{m:02d}-15T17:00:00Z"
        north_load = 120.0 if m in {6, 7, 8, 9} else 100.0
        south_load = 80.0 if m in {6, 7, 8, 9} else 90.0
        zonal_load.extend(
            [
                {"timestamp": ts, "zone": "NORTH", "load_mw": north_load},
                {"timestamp": ts, "zone": "SOUTH", "load_mw": south_load},
            ]
        )
        net_zonal_load.extend(
            [
                {"timestamp": ts, "zone": "NORTH", "load_mw": north_load - 20.0},
                {"timestamp": ts, "zone": "SOUTH", "load_mw": south_load - 10.0},
            ]
        )
        system_lambda_series.append({"timestamp": ts, "system_lambda": 20.0})

        north_congestion = 12.0 if m in {6, 7, 8, 9} else 4.0
        south_congestion = 4.0 if m in {6, 7, 8, 9} else 8.0
        if include_decomposed:
            zonal_lmp_series.extend(
                [
                    {
                        "timestamp": ts,
                        "zone": "NORTH",
                        "lmp": 35.0,
                        "energy_component": 20.0,
                        "loss_component": 3.0,
                    },
                    {
                        "timestamp": ts,
                        "zone": "SOUTH",
                        "lmp": 27.0,
                        "energy_component": 20.0,
                        "loss_component": 3.0,
                    },
                ]
            )
        else:
            zonal_lmp_series.extend(
                [
                    {"timestamp": ts, "zone": "NORTH", "lmp": 35.0},
                    {"timestamp": ts, "zone": "SOUTH", "lmp": 27.0},
                ]
            )

        if include_direct_congestion:
            congestion_series.extend(
                [
                    {"timestamp": ts, "zone": "NORTH", "congestion_component": north_congestion},
                    {"timestamp": ts, "zone": "SOUTH", "congestion_component": south_congestion},
                ]
            )

        shadow_price_series.extend(
            [
                {"timestamp": ts, "constraint": "WEST_PATH", "shadow_price": 25.0 if m in {6,7,8,9} else 8.0, "binding_flag": 1},
                {"timestamp": ts, "constraint": "COAST_PATH", "shadow_price": 8.0 if m in {6,7,8,9} else 20.0, "binding_flag": 1},
            ]
        )

    return MethodologyInputs(
        year=2024,
        tcos_target_usd=1200.0,
        peak_intervals=_yearly_peaks(),
        zonal_load=zonal_load,
        net_zonal_load=net_zonal_load,
        zonal_lmp_series=zonal_lmp_series,
        system_lambda_series=system_lambda_series,
        congestion_series=congestion_series,
        shadow_price_series=shadow_price_series,
        metadata={"export_rule": "A"},
    )


def _equal_load_inputs():
    inputs = _seasonal_inputs(include_direct_congestion=True, include_decomposed=True)
    for row in inputs.zonal_load:
        row["load_mw"] = 100.0
    for row in inputs.net_zonal_load:
        row["load_mw"] = 100.0
    for row in inputs.congestion_series:
        row["congestion_component"] = 10.0
    for row in inputs.zonal_lmp_series:
        row["lmp"] = 35.0
        row["energy_component"] = 20.0
        row["loss_component"] = 5.0
    return inputs


def _regression_inputs():
    peak_intervals = _yearly_peaks()
    zonal_load = []
    net_zonal_load = []
    congestion_series = []
    zonal_lmp_series = []
    system_lambda_series = []
    shadow_price_series = []
    for m in range(1, 13):
        ts = peak_intervals[f"2024-{m:02d}"]
        zonal_load.extend(
            [
                {"timestamp": ts, "zone": "NORTH", "load_mw": 120.0},
                {"timestamp": ts, "zone": "SOUTH", "load_mw": 80.0},
            ]
        )
        net_zonal_load.extend(
            [
                {"timestamp": ts, "zone": "NORTH", "load_mw": 120.0},
                {"timestamp": ts, "zone": "SOUTH", "load_mw": 80.0},
            ]
        )
        congestion_series.extend(
            [
                {"timestamp": ts, "zone": "NORTH", "congestion_component": 10.0},
                {"timestamp": ts, "zone": "SOUTH", "congestion_component": 5.0},
            ]
        )
        zonal_lmp_series.extend(
            [
                {"timestamp": ts, "zone": "NORTH", "lmp": 30.0, "energy_component": 15.0, "loss_component": 5.0},
                {"timestamp": ts, "zone": "SOUTH", "lmp": 25.0, "energy_component": 15.0, "loss_component": 5.0},
            ]
        )
        system_lambda_series.append({"timestamp": ts, "system_lambda": 15.0})
        shadow_price_series.extend(
            [
                {"timestamp": ts, "constraint": "C1", "shadow_price": 10.0, "binding_flag": 1},
                {"timestamp": ts, "constraint": "C2", "shadow_price": 5.0, "binding_flag": 1},
            ]
        )
    return MethodologyInputs(
        year=2024,
        tcos_target_usd=1200.0,
        peak_intervals=peak_intervals,
        zonal_load=zonal_load,
        net_zonal_load=net_zonal_load,
        zonal_lmp_series=zonal_lmp_series,
        system_lambda_series=system_lambda_series,
        congestion_series=congestion_series,
        shadow_price_series=shadow_price_series,
        metadata={"export_rule": "A"},
    )


def test_cbtca_direct_proxy_happy_path():
    model = CBTCAModel()
    inputs = _seasonal_inputs(include_direct_congestion=True)
    result = model.run(inputs)
    assert result.methodology == "cbtca"
    assert sum(result.shares.values()) == pytest.approx(1.0)
    assert sum(result.allocations_usd.values()) == pytest.approx(1200.0)
    assert result.assumptions["mode"] == "combined"
    assert result.assumptions["resolved_operational_proxy_tier"] == "tier1_direct"
    assert result.shares["NORTH"] > result.shares["SOUTH"]


def test_cbtca_prefers_decomposed_proxy_before_lambda_fallback():
    model = CBTCAModel()
    inputs = _seasonal_inputs(include_direct_congestion=False, include_decomposed=True)
    result = model.run(inputs)
    assert result.assumptions["resolved_operational_proxy_tier"] == "tier2_decomposed"
    assert result.assumptions["confidence"] == "Moderate"


def test_cbtca_falls_back_to_congestion_plus_loss_when_needed():
    model = CBTCAModel()
    inputs = _seasonal_inputs(include_direct_congestion=False, include_decomposed=False)
    result = model.run(inputs)
    assert result.assumptions["resolved_operational_proxy_tier"] == "tier3_congestion_plus_loss"
    assert result.assumptions["confidence"] == "Low"
    assert any("congestion-plus-loss" in warning or "congestion-plus-loss" in str(result.warnings) for warning in result.warnings)


def test_cbtca_can_run_planning_only_fallback_when_operational_basis_missing():
    model = CBTCAModel()
    inputs = _seasonal_inputs(include_direct_congestion=False, include_decomposed=True)
    inputs.zonal_load = []
    result = model.run(inputs, params={"operational_load_basis": "gross", "planning_load_basis": "net"})
    assert result.assumptions["mode"] == "planning_only_fallback"
    assert result.assumptions["operational_weight"] == 0.0
    assert result.assumptions["planning_weight"] == 1.0
    assert sum(result.shares.values()) == pytest.approx(1.0)


def test_cbtca_requires_planning_signal():
    model = CBTCAModel()
    inputs = _seasonal_inputs()
    inputs.shadow_price_series = []
    inputs.planning_constraint_summary = []
    inputs.zonal_lmp_series = []
    with pytest.raises(ValueError, match="planning"):
        model.run(inputs)


def test_cbtca_preserves_signed_congestion_proxy_values():
    model = CBTCAModel()
    inputs = _seasonal_inputs(include_direct_congestion=True)
    for row in inputs.congestion_series:
        if row["zone"] == "SOUTH":
            row["congestion_component"] = -abs(row["congestion_component"])
    result = model.run(inputs)
    assert any("signed congestion burden was preserved" in warning for warning in result.warnings)
    assert result.shares["NORTH"] > result.shares["SOUTH"]


def test_cbtca_rejects_zero_congestion_signal():
    model = CBTCAModel()
    inputs = _seasonal_inputs(include_direct_congestion=True, include_decomposed=True)
    for row in inputs.congestion_series:
        row["congestion_component"] = 0.0
    for row in inputs.zonal_lmp_series:
        row["lmp"] = 20.0
        row["energy_component"] = 20.0
        row["loss_component"] = 0.0
    with pytest.raises(ValueError, match="planning burden"):
        model.run(inputs)


def test_cbtca_equal_loads_and_equal_proxies_produce_equal_shares():
    model = CBTCAModel()
    inputs = _equal_load_inputs()
    result = model.run(inputs)
    assert result.shares["NORTH"] == pytest.approx(0.5)
    assert result.shares["SOUTH"] == pytest.approx(0.5)


def test_cbtca_rejects_invalid_proxy_tier_name():
    model = CBTCAModel()
    with pytest.raises(ValueError, match="unsupported congestion proxy tier"):
        model.run(_seasonal_inputs(), params={"congestion_proxy_tier": "bogus"})


def test_cbtca_rejects_invalid_load_basis_name():
    model = CBTCAModel()
    with pytest.raises(ValueError, match="unsupported load basis"):
        model.run(_seasonal_inputs(), params={"operational_load_basis": "weird"})


def test_cbtca_regression_pins_known_allocation_shares():
    model = CBTCAModel()
    result = model.run(_regression_inputs())
    assert result.shares["NORTH"] == pytest.approx(0.75)
    assert result.shares["SOUTH"] == pytest.approx(0.25)
    assert result.allocations_usd["NORTH"] == pytest.approx(900.0)
    assert result.allocations_usd["SOUTH"] == pytest.approx(300.0)


def test_cbtca_sensitivity_model_normalizes_weights():
    model = CBTCASensitivityModel()
    inputs = _seasonal_inputs()
    result = model.run(inputs, params={"operational_weight": 2.0, "planning_weight": 3.0})
    assert result.assumptions["operational_weight"] == pytest.approx(0.4)
    assert result.assumptions["planning_weight"] == pytest.approx(0.6)


def test_build_sensitivity_cases_covers_multiple_specified_families():
    inputs = _seasonal_inputs()
    matrix = load_sensitivity_matrix(os.path.join(PROJECT_ROOT, "src/config/sensitivity_matrix.yaml"))
    results = build_sensitivity_cases(inputs, matrix=matrix)
    families = {result.assumptions["sensitivity_family"] for result in results}
    assert {"operational_planning_weights", "congestion_proxy_tiers", "export_rules", "planning_windows", "target_set_sizes", "outlier_caps"}.issubset(families)
    assert len(results) == 19
