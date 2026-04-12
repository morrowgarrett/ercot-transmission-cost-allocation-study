import pytest

from src.models.base import MethodologyInputs
from src.models.four_cp import FourCPModel
from src.models.four_cp_net_load import FourCPNetLoadModel
from src.models.twelve_cp import TwelveCPModel
from src.models.twelve_cp_net_load import TwelveCPNetLoadModel
from src.models.hybrid_vol_12cp_nl import HybridVol12CPNLModel


def summer_peaks():
    return {
        "2024-06": "2024-06-15T17:00:00Z",
        "2024-07": "2024-07-20T18:00:00Z",
        "2024-08": "2024-08-21T19:00:00Z",
        "2024-09": "2024-09-05T20:00:00Z",
    }


def yearly_peaks():
    return {f"2024-{m:02d}": f"2024-{m:02d}-15T17:00:00Z" for m in range(1, 13)}


def test_four_cp_uses_only_provided_peak_intervals():
    model = FourCPModel()
    inputs = MethodologyInputs(
        year=2024,
        tcos_target_usd=100.0,
        peak_intervals=summer_peaks(),
        zonal_load=[
            {"timestamp": "2024-06-15T17:00:00Z", "zone": "NORTH", "load_mw": 60.0},
            {"timestamp": "2024-06-15T17:00:00Z", "zone": "SOUTH", "load_mw": 40.0},
            {"timestamp": "2024-07-20T18:00:00Z", "zone": "NORTH", "load_mw": 50.0},
            {"timestamp": "2024-07-20T18:00:00Z", "zone": "SOUTH", "load_mw": 50.0},
            {"timestamp": "2024-08-21T19:00:00Z", "zone": "NORTH", "load_mw": 55.0},
            {"timestamp": "2024-08-21T19:00:00Z", "zone": "SOUTH", "load_mw": 45.0},
            {"timestamp": "2024-09-05T20:00:00Z", "zone": "NORTH", "load_mw": 65.0},
            {"timestamp": "2024-09-05T20:00:00Z", "zone": "SOUTH", "load_mw": 35.0},
            {"timestamp": "2024-01-01T00:00:00Z", "zone": "NORTH", "load_mw": 999.0},
        ],
    )
    result = model.run(inputs)
    assert round(sum(result.shares.values()), 10) == 1.0
    assert round(sum(result.allocations_usd.values()), 10) == 100.0
    assert result.shares["NORTH"] == 230.0 / 400.0
    assert result.shares["SOUTH"] == 170.0 / 400.0


def test_four_cp_duplicate_rows_emit_warning():
    model = FourCPModel()
    inputs = MethodologyInputs(
        year=2024,
        tcos_target_usd=100.0,
        peak_intervals=summer_peaks(),
        zonal_load=[
            {"timestamp": "2024-06-15T17:00:00Z", "zone": "NORTH", "load_mw": 10.0},
            {"timestamp": "2024-06-15T17:00:00Z", "zone": "NORTH", "load_mw": 5.0},
            {"timestamp": "2024-07-20T18:00:00Z", "zone": "NORTH", "load_mw": 10.0},
            {"timestamp": "2024-08-21T19:00:00Z", "zone": "NORTH", "load_mw": 10.0},
            {"timestamp": "2024-09-05T20:00:00Z", "zone": "NORTH", "load_mw": 10.0},
        ],
    )
    result = model.run(inputs)
    assert any("duplicate zone+timestamp" in w for w in result.warnings)


def test_four_cp_net_load_happy_path():
    model = FourCPNetLoadModel()
    inputs = MethodologyInputs(
        year=2024,
        tcos_target_usd=100.0,
        peak_intervals=summer_peaks(),
        net_zonal_load=[
            {"timestamp": "2024-06-15T17:00:00Z", "zone": "NORTH", "load_mw": 30.0},
            {"timestamp": "2024-06-15T17:00:00Z", "zone": "SOUTH", "load_mw": 70.0},
            {"timestamp": "2024-07-20T18:00:00Z", "zone": "NORTH", "load_mw": 40.0},
            {"timestamp": "2024-07-20T18:00:00Z", "zone": "SOUTH", "load_mw": 60.0},
            {"timestamp": "2024-08-21T19:00:00Z", "zone": "NORTH", "load_mw": 50.0},
            {"timestamp": "2024-08-21T19:00:00Z", "zone": "SOUTH", "load_mw": 50.0},
            {"timestamp": "2024-09-05T20:00:00Z", "zone": "NORTH", "load_mw": 60.0},
            {"timestamp": "2024-09-05T20:00:00Z", "zone": "SOUTH", "load_mw": 40.0},
        ],
        metadata={"export_rule": "A"},
    )
    result = model.run(inputs)
    assert round(sum(result.shares.values()), 10) == 1.0
    assert round(sum(result.allocations_usd.values()), 10) == 100.0
    assert result.shares["NORTH"] == 180.0 / 400.0
    assert result.shares["SOUTH"] == 220.0 / 400.0
    assert result.assumptions["export_rule"] == "A"


def test_twelve_cp_happy_path():
    model = TwelveCPModel()
    peaks = yearly_peaks()
    rows = []
    north = 0.0
    south = 0.0
    for m in range(1, 13):
        ts = f"2024-{m:02d}-15T17:00:00Z"
        n = float(m)
        s = float(13 - m)
        north += n
        south += s
        rows.append({"timestamp": ts, "zone": "NORTH", "load_mw": n})
        rows.append({"timestamp": ts, "zone": "SOUTH", "load_mw": s})
    inputs = MethodologyInputs(year=2024, tcos_target_usd=120.0, peak_intervals=peaks, zonal_load=rows)
    result = model.run(inputs)
    assert round(sum(result.shares.values()), 10) == 1.0
    assert round(sum(result.allocations_usd.values()), 10) == 120.0
    assert result.shares["NORTH"] == north / (north + south)
    assert result.shares["SOUTH"] == south / (north + south)


def test_twelve_cp_net_load_happy_path():
    model = TwelveCPNetLoadModel()
    peaks = yearly_peaks()
    rows = []
    north = 0.0
    south = 0.0
    for m in range(1, 13):
        ts = f"2024-{m:02d}-15T17:00:00Z"
        n = float(2 * m)
        s = float(24 - 2 * m)
        north += n
        south += s
        rows.append({"timestamp": ts, "zone": "NORTH", "load_mw": n})
        rows.append({"timestamp": ts, "zone": "SOUTH", "load_mw": s})
    inputs = MethodologyInputs(
        year=2024,
        tcos_target_usd=240.0,
        peak_intervals=peaks,
        net_zonal_load=rows,
        metadata={"export_rule": "B"},
    )
    result = model.run(inputs)
    assert round(sum(result.shares.values()), 10) == 1.0
    assert round(sum(result.allocations_usd.values()), 10) == 240.0
    assert result.shares["NORTH"] == north / (north + south)
    assert result.shares["SOUTH"] == south / (north + south)
    assert result.assumptions["export_rule"] == "B"


def test_hybrid_happy_path():
    model = HybridVol12CPNLModel()
    peaks = yearly_peaks()
    gross_rows = []
    net_rows = []
    for m in range(1, 13):
        ts = f"2024-{m:02d}-15T17:00:00Z"
        gross_rows.append({"timestamp": ts, "zone": "NORTH", "load_mw": 80.0})
        gross_rows.append({"timestamp": ts, "zone": "SOUTH", "load_mw": 20.0})
        net_rows.append({"timestamp": ts, "zone": "NORTH", "load_mw": 40.0})
        net_rows.append({"timestamp": ts, "zone": "SOUTH", "load_mw": 60.0})
    inputs = MethodologyInputs(
        year=2024,
        tcos_target_usd=100.0,
        peak_intervals=peaks,
        zonal_load=gross_rows,
        net_zonal_load=net_rows,
        metadata={"export_rule": "C"},
    )
    result = model.run(inputs, params={"alpha": 0.4})
    assert round(sum(result.shares.values()), 10) == 1.0
    assert round(sum(result.allocations_usd.values()), 10) == 100.0
    assert result.shares["NORTH"] == pytest.approx(0.4 * 0.8 + 0.6 * 0.4)
    assert result.shares["SOUTH"] == pytest.approx(0.4 * 0.2 + 0.6 * 0.6)


def test_hybrid_warns_when_volumetric_rows_do_not_cover_annual_energy_basis():
    model = HybridVol12CPNLModel()
    peaks = yearly_peaks()
    inputs = MethodologyInputs(
        year=2024,
        tcos_target_usd=100.0,
        peak_intervals=peaks,
        zonal_load=[
            {"timestamp": "2024-01-15T17:00:00Z", "zone": "NORTH", "load_mw": 80.0},
            {"timestamp": "2024-01-15T17:00:00Z", "zone": "SOUTH", "load_mw": 20.0},
        ],
        net_zonal_load=[
            {"timestamp": f"2024-{m:02d}-15T17:00:00Z", "zone": "NORTH", "load_mw": 40.0}
            for m in range(1, 13)
        ]
        + [
            {"timestamp": f"2024-{m:02d}-15T17:00:00Z", "zone": "SOUTH", "load_mw": 60.0}
            for m in range(1, 13)
        ],
    )
    result = model.run(inputs, params={"alpha": 0.4})
    assert any("annual-energy floor" in warning for warning in result.warnings)


def test_four_cp_requires_peak_intervals():
    model = FourCPModel()
    inputs = MethodologyInputs(year=2024, tcos_target_usd=100.0, zonal_load=[])
    with pytest.raises(ValueError, match="peak_intervals"):
        model.run(inputs)


def test_four_cp_requires_matching_rows():
    model = FourCPModel()
    inputs = MethodologyInputs(
        year=2024,
        tcos_target_usd=100.0,
        peak_intervals=summer_peaks(),
        zonal_load=[{"timestamp": "2024-01-01T00:00:00Z", "zone": "NORTH", "load_mw": 50.0}],
    )
    with pytest.raises(ValueError, match="no zonal load rows matched"):
        model.run(inputs)


def test_four_cp_requires_positive_total_load():
    model = FourCPModel()
    inputs = MethodologyInputs(
        year=2024,
        tcos_target_usd=100.0,
        peak_intervals=summer_peaks(),
        zonal_load=[
            {"timestamp": "2024-06-15T17:00:00Z", "zone": "NORTH", "load_mw": 0.0},
            {"timestamp": "2024-07-20T18:00:00Z", "zone": "NORTH", "load_mw": 0.0},
            {"timestamp": "2024-08-21T19:00:00Z", "zone": "NORTH", "load_mw": 0.0},
            {"timestamp": "2024-09-05T20:00:00Z", "zone": "NORTH", "load_mw": 0.0},
        ],
    )
    with pytest.raises(ValueError, match="must sum to a positive value"):
        model.run(inputs)


def test_four_cp_net_load_requires_net_series():
    model = FourCPNetLoadModel()
    inputs = MethodologyInputs(year=2024, tcos_target_usd=100.0, peak_intervals=summer_peaks())
    with pytest.raises(ValueError, match="net_zonal_load"):
        model.run(inputs)


def test_twelve_cp_requires_twelve_months():
    model = TwelveCPModel()
    inputs = MethodologyInputs(
        year=2024,
        tcos_target_usd=100.0,
        peak_intervals={"2024-06": "2024-06-15T17:00:00Z"},
        zonal_load=[],
    )
    with pytest.raises(ValueError, match="exactly twelve"):
        model.run(inputs)


def test_twelve_cp_net_load_requires_net_series():
    model = TwelveCPNetLoadModel()
    inputs = MethodologyInputs(year=2024, tcos_target_usd=100.0, peak_intervals=yearly_peaks())
    with pytest.raises(ValueError, match="net_zonal_load"):
        model.run(inputs)
