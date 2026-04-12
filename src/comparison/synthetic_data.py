from __future__ import annotations

from dataclasses import dataclass

from src.models.base import MethodologyInputs


ZONES = ["NORTH", "SOUTH", "WEST", "HOUSTON"]


@dataclass(frozen=True)
class SyntheticDatasetMetadata:
    name: str
    description: str
    synthetic_fields: dict[str, str]
    real_data_mapping: dict[str, str]
    edge_cases: list[str]


def yearly_peaks(year: int = 2024) -> dict[str, str]:
    return {f"{year}-{m:02d}": f"{year}-{m:02d}-15T17:00:00Z" for m in range(1, 13)}


def build_four_zone_synthetic_inputs(year: int = 2024, export_rule: str = "A") -> MethodologyInputs:
    peak_intervals = yearly_peaks(year)
    zonal_load = []
    net_zonal_load = []
    zonal_lmp_series = []
    system_lambda_series = []
    congestion_series = []
    shadow_price_series = []

    gross_profiles = {
        "NORTH": [118, 120, 122, 125, 128, 136, 140, 142, 138, 130, 124, 120],
        "SOUTH": [86, 88, 90, 92, 95, 100, 104, 106, 102, 96, 90, 88],
        "WEST": [72, 70, 68, 64, 62, 60, 58, 56, 58, 64, 68, 70],
        "HOUSTON": [108, 110, 112, 116, 120, 126, 130, 132, 128, 122, 116, 112],
    }
    net_profiles = {
        "NORTH": [110, 112, 114, 116, 118, 124, 128, 130, 126, 120, 116, 112],
        "SOUTH": [80, 82, 84, 86, 88, 92, 96, 98, 94, 90, 84, 82],
        "WEST": [18, 10, 2, -4, -8, -14, -18, -22, -12, -2, 6, 12],
        "HOUSTON": [104, 106, 108, 110, 114, 120, 124, 126, 122, 116, 110, 108],
    }
    direct_congestion = {
        "NORTH": [9, 9, 10, 11, 12, 14, 16, 17, 15, 12, 10, 9],
        "SOUTH": [4, 4, 5, 5, 6, 7, 8, 8, 7, 6, 5, 4],
        "WEST": [11, 10, 9, 8, 7, 6, 5, 4, 6, 8, 9, 10],
        "HOUSTON": [5, 5, 6, 7, 8, 10, 11, 12, 10, 8, 6, 5],
    }
    lmp_components = {
        "NORTH": {"energy": 22.0, "loss": 3.0},
        "SOUTH": {"energy": 22.0, "loss": 2.0},
        "WEST": {"energy": 22.0, "loss": 4.0},
        "HOUSTON": {"energy": 22.0, "loss": 3.0},
    }

    for month in range(1, 13):
        ts = peak_intervals[f"{year}-{month:02d}"]
        system_lambda_series.append({"timestamp": ts, "system_lambda": 22.0})
        for zone in ZONES:
            gross = float(gross_profiles[zone][month - 1])
            net = float(net_profiles[zone][month - 1])
            proxy = float(direct_congestion[zone][month - 1])
            loss = lmp_components[zone]["loss"]
            energy = lmp_components[zone]["energy"]
            lmp = energy + loss + proxy
            zonal_load.append({"timestamp": ts, "zone": zone, "load_mw": gross})
            net_zonal_load.append({"timestamp": ts, "zone": zone, "load_mw": net})
            zonal_lmp_series.append(
                {
                    "timestamp": ts,
                    "zone": zone,
                    "lmp": lmp,
                    "energy_component": energy,
                    "loss_component": loss,
                }
            )
            congestion_series.append({"timestamp": ts, "zone": zone, "congestion_component": proxy})

        shadow_price_series.extend(
            [
                {
                    "timestamp": ts,
                    "constraint": "WEST_TX_EXPORT",
                    "shadow_price": 28.0 if month in {6, 7, 8, 9} else 12.0,
                    "binding_flag": 1,
                },
                {
                    "timestamp": ts,
                    "constraint": "HOUSTON_IMPORT",
                    "shadow_price": 20.0 if month in {6, 7, 8, 9} else 10.0,
                    "binding_flag": 1,
                },
                {
                    "timestamp": ts,
                    "constraint": "NORTH_RAMP",
                    "shadow_price": 16.0 if month in {12, 1, 2} else 8.0,
                    "binding_flag": 1,
                },
            ]
        )

    return MethodologyInputs(
        year=year,
        tcos_target_usd=1000.0,
        peak_intervals=peak_intervals,
        zonal_load=zonal_load,
        net_zonal_load=net_zonal_load,
        zonal_lmp_series=zonal_lmp_series,
        system_lambda_series=system_lambda_series,
        congestion_series=congestion_series,
        shadow_price_series=shadow_price_series,
        metadata={
            "export_rule": export_rule,
            "synthetic_dataset": "four_zone_v1",
            "notes": [
                "WEST is intentionally export-heavy in net-load terms during summer months",
                "WEST approximates a high-BTM / renewable-overbuild zone with negative net-load intervals",
                "HOUSTON is a high-load coastal import zone",
                "NORTH is a large diversified load center",
            ],
        },
    )


def synthetic_dataset_metadata() -> SyntheticDatasetMetadata:
    return SyntheticDatasetMetadata(
        name="four_zone_v1",
        description="Synthetic four-zone ERCOT-like comparison fixture with one high-BTM/export-heavy zone and one high-load coastal zone.",
        synthetic_fields={
            "zonal_load": "monthly synthetic gross-load profiles by zone",
            "net_zonal_load": "monthly synthetic net-load profiles, including negative WEST summer intervals",
            "zonal_lmp_series": "synthetic zonal prices assembled from energy + loss + congestion components",
            "system_lambda_series": "flat synthetic system lambda baseline",
            "congestion_series": "synthetic direct congestion proxies by zone/month",
            "shadow_price_series": "synthetic constraint-score drivers for planning ledger tests",
        },
        real_data_mapping={
            "zonal_load": "ERCOT or vendor zonal load series",
            "net_zonal_load": "preprocessed net load after Rule A/B/C export treatment",
            "zonal_lmp_series": "DA zonal LMP with energy/loss decomposition where available",
            "system_lambda_series": "system lambda or equivalent energy baseline",
            "congestion_series": "direct congestion component when available",
            "shadow_price_series": "binding shadow price / constraint records for planning target-set construction",
        },
        edge_cases=[
            "WEST includes negative net-load intervals to mimic an export-heavy / high-BTM zone",
            "HOUSTON remains a high gross-load import-heavy zone",
            "summer months intensify WEST and HOUSTON constraint stress",
            "all four ERCOT load zones are represented instead of a toy two-zone split",
        ],
    )
