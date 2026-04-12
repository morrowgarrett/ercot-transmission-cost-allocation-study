from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Tuple

import yaml

from .base import MethodologyInputs, MethodologyModel, MethodologyResult


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def _percentile(sorted_values: List[float], percentile: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (len(sorted_values) - 1) * (percentile / 100.0)
    lower = int(rank)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = rank - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def _normalize_weights(op_weight: float, pl_weight: float) -> Tuple[float, float]:
    total = op_weight + pl_weight
    if total <= 0:
        raise ValueError("operational and planning weights must sum to a positive value")
    return op_weight / total, pl_weight / total


def _filter_rows_by_window(rows: Iterable[Dict[str, Any]], window: str, year: int) -> List[Dict[str, Any]]:
    filtered = []
    for row in rows:
        timestamp = str(row.get("timestamp", ""))
        if not timestamp.startswith(f"{year}-"):
            continue
        if window == "summer_only":
            month = timestamp[5:7]
            if month not in {"06", "07", "08", "09"}:
                continue
        filtered.append(row)
    return filtered


def _build_lambda_map(rows: Iterable[Dict[str, Any]]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for row in rows:
        timestamp = str(row.get("timestamp"))
        value = row.get("system_lambda")
        if value is None:
            value = row.get("load_mw")
        if value is None:
            value = row.get("value")
        if timestamp:
            out[timestamp] = _safe_float(value)
    return out


def _select_load_basis(inputs: MethodologyInputs, basis: str) -> List[Dict[str, Any]]:
    if basis == "gross":
        rows = inputs.zonal_load
    elif basis == "net":
        rows = inputs.net_zonal_load
    else:
        raise ValueError(f"unsupported load basis: {basis}")
    if not rows:
        raise ValueError(f"{basis} zonal load rows are required for CBTCA load basis")
    return rows


def _aggregate_zone_values(rows: Iterable[Dict[str, Any]], value_key: str) -> Dict[str, float]:
    totals = defaultdict(float)
    for row in rows:
        zone = row.get("zone")
        if zone is None:
            continue
        totals[str(zone)] += _safe_float(row.get(value_key))
    return dict(totals)


def _normalize_proxy_tier_name(tier: str | None) -> str | None:
    aliases = {
        None: None,
        "auto": "auto",
        "direct": "tier1_direct",
        "tier1_direct": "tier1_direct",
        "decomposed": "tier2_decomposed",
        "tier2_decomposed": "tier2_decomposed",
        "congestion_plus_loss": "tier3_congestion_plus_loss",
        "tier3_congestion_plus_loss": "tier3_congestion_plus_loss",
    }
    if tier not in aliases:
        raise ValueError(f"unsupported congestion proxy tier: {tier}")
    return aliases[tier]


def _prepare_operational_proxy(
    inputs: MethodologyInputs,
    tier: str | None = None,
) -> Tuple[Dict[Tuple[str, str], float], str | None, List[str]]:
    warnings: List[str] = []
    tier = _normalize_proxy_tier_name(tier)

    if tier in (None, "auto", "tier1_direct") and inputs.congestion_series:
        proxy = {}
        for row in inputs.congestion_series:
            zone = row.get("zone")
            timestamp = row.get("timestamp")
            if zone is None or timestamp is None:
                continue
            value = row.get("congestion_mw")
            if value is None:
                value = row.get("congestion_component")
            if value is None:
                value = row.get("value")
            proxy[(str(zone), str(timestamp))] = _safe_float(value)
        if proxy:
            return proxy, "tier1_direct", warnings

    if tier in (None, "auto", "tier2_decomposed") and inputs.zonal_lmp_series:
        proxy = {}
        available = False
        for row in inputs.zonal_lmp_series:
            zone = row.get("zone")
            timestamp = row.get("timestamp")
            lmp = row.get("lmp")
            energy = row.get("energy_component")
            loss = row.get("loss_component")
            if zone is None or timestamp is None or lmp is None:
                continue
            if energy is None or loss is None:
                continue
            available = True
            proxy[(str(zone), str(timestamp))] = _safe_float(lmp) - _safe_float(energy) - _safe_float(loss)
        if available:
            return proxy, "tier2_decomposed", warnings
        if tier == "tier2_decomposed":
            warnings.append("requested decomposed congestion proxy tier, but energy/loss components were unavailable")

    if tier in (None, "auto", "tier3_congestion_plus_loss") and inputs.zonal_lmp_series and inputs.system_lambda_series:
        lambda_map = _build_lambda_map(inputs.system_lambda_series)
        proxy = {}
        for row in inputs.zonal_lmp_series:
            zone = row.get("zone")
            timestamp = row.get("timestamp")
            lmp = row.get("lmp")
            if zone is None or timestamp is None or lmp is None:
                continue
            if str(timestamp) not in lambda_map:
                continue
            proxy[(str(zone), str(timestamp))] = _safe_float(lmp) - lambda_map[str(timestamp)]
        if proxy:
            warnings.append("operational congestion proxy fell back to lmp_minus_system_lambda; this is congestion-plus-loss, not pure congestion")
            return proxy, "tier3_congestion_plus_loss", warnings

    return {}, None, warnings


def _apply_proxy_cap(
    proxy_map: Dict[Tuple[str, str], float],
    outlier_cap_pctile: float | None,
) -> Tuple[Dict[Tuple[str, str], float], int, bool]:
    if not proxy_map:
        return {}, 0, False

    had_negative = any(value < 0 for value in proxy_map.values())
    capped_map = dict(proxy_map)

    if outlier_cap_pctile is None:
        return capped_map, 0, had_negative

    nonzero_abs_values = sorted(abs(value) for value in capped_map.values() if value != 0)
    if not nonzero_abs_values:
        return capped_map, 0, had_negative

    cap = _percentile(nonzero_abs_values, outlier_cap_pctile)
    capped = 0
    for key, value in list(capped_map.items()):
        if abs(value) > cap:
            capped_map[key] = cap if value > 0 else -cap
            capped += 1
    return capped_map, capped, had_negative


def _compute_operational_share(
    inputs: MethodologyInputs,
    load_basis: str,
    proxy_tier: str | None,
    outlier_cap_pctile: float | None,
) -> Tuple[Dict[str, float], Dict[str, Any], List[str]]:
    warnings: List[str] = []
    proxy_map, resolved_tier, proxy_warnings = _prepare_operational_proxy(inputs, tier=proxy_tier)
    warnings.extend(proxy_warnings)
    if not proxy_map:
        return {}, {"resolved_proxy_tier": None, "planning_only_fallback": True}, warnings

    proxy_map, capped_values, had_negative = _apply_proxy_cap(proxy_map, outlier_cap_pctile)
    if capped_values:
        warnings.append(f"capped {capped_values} operational proxy observations at the {outlier_cap_pctile}th percentile by absolute magnitude")
    if had_negative:
        warnings.append("operational proxy contains negative values; signed congestion burden was preserved per methodology spec")

    try:
        load_rows = _select_load_basis(inputs, load_basis)
    except ValueError as exc:
        warnings.append(str(exc))
        return {}, {"resolved_proxy_tier": resolved_tier, "planning_only_fallback": True}, warnings

    burden = defaultdict(float)
    matched = 0
    for row in load_rows:
        zone = row.get("zone")
        timestamp = row.get("timestamp")
        if zone is None or timestamp is None:
            continue
        key = (str(zone), str(timestamp))
        if key not in proxy_map:
            continue
        matched += 1
        burden[str(zone)] += _safe_float(row.get("load_mw")) * proxy_map[key]

    total = sum(burden.values())
    if matched == 0 or total <= 0:
        return {}, {"resolved_proxy_tier": resolved_tier, "planning_only_fallback": True}, warnings

    shares = {zone: value / total for zone, value in burden.items()}
    return shares, {
        "resolved_proxy_tier": resolved_tier,
        "planning_only_fallback": False,
        "matched_operational_rows": matched,
        "operational_outlier_cap_pctile": outlier_cap_pctile,
    }, warnings


def _extract_constraint_scores(
    inputs: MethodologyInputs,
    planning_window: str,
    year: int,
) -> Tuple[Dict[str, float], Dict[str, List[str]], List[str]]:
    warnings: List[str] = []
    filtered_shadow_rows = _filter_rows_by_window(inputs.shadow_price_series, planning_window, year)
    if filtered_shadow_rows:
        scores = defaultdict(float)
        timestamps = defaultdict(list)
        for row in filtered_shadow_rows:
            constraint = row.get("constraint") or row.get("constraint_name") or row.get("name")
            timestamp = row.get("timestamp")
            if constraint is None or timestamp is None:
                continue
            shadow_price = row.get("shadow_price")
            if shadow_price is None:
                shadow_price = row.get("value")
            binding_flag = row.get("binding_flag")
            if binding_flag is None:
                binding_flag = 1 if _safe_float(shadow_price) > 0 else 0
            contribution = max(0.0, _safe_float(shadow_price)) * _safe_float(binding_flag)
            if contribution <= 0:
                continue
            scores[str(constraint)] += contribution
            timestamps[str(constraint)].append(str(timestamp))
        if scores:
            return dict(scores), {k: sorted(set(v)) for k, v in timestamps.items()}, warnings

    filtered_summary = _filter_rows_by_window(inputs.planning_constraint_summary, planning_window, year)
    if filtered_summary:
        scores = {}
        timestamps = {}
        for row in filtered_summary:
            constraint = row.get("constraint") or row.get("constraint_name") or row.get("name")
            if constraint is None:
                continue
            score = row.get("constraint_score")
            if score is None:
                score = row.get("score")
            scores[str(constraint)] = max(0.0, _safe_float(score))
            if row.get("timestamps"):
                timestamps[str(constraint)] = sorted({str(value) for value in row["timestamps"]})
        if scores:
            warnings.append("planning constraint scores came from planning_constraint_summary, not raw shadow prices")
            return scores, timestamps, warnings

    raise ValueError("CBTCA planning ledger requires shadow_price_series or planning_constraint_summary for constraint scoring")


def _compute_planning_share(
    inputs: MethodologyInputs,
    load_basis: str,
    planning_window: str,
    target_set_size: int,
    proxy_tier: str | None,
) -> Tuple[Dict[str, float], Dict[str, Any], List[str]]:
    warnings: List[str] = []
    proxy_map, resolved_tier, proxy_warnings = _prepare_operational_proxy(inputs, tier=proxy_tier)
    warnings.extend(proxy_warnings)
    if not proxy_map:
        raise ValueError("CBTCA planning ledger requires a congestion proxy via direct congestion, decomposed LMP, or zonal LMP plus system lambda")

    proxy_map, _, had_negative = _apply_proxy_cap(proxy_map, None)
    if had_negative:
        warnings.append("planning exposure uses signed congestion proxy values per methodology spec")

    scores, timestamps_by_constraint, score_warnings = _extract_constraint_scores(inputs, planning_window, inputs.year)
    warnings.extend(score_warnings)
    ranked_constraints = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    selected = ranked_constraints[: max(1, target_set_size)]

    load_rows = _select_load_basis(inputs, load_basis)
    load_map = defaultdict(float)
    for row in load_rows:
        zone = row.get("zone")
        timestamp = row.get("timestamp")
        if zone is None or timestamp is None:
            continue
        load_map[(str(zone), str(timestamp))] += _safe_float(row.get("load_mw"))

    planning_burden = defaultdict(float)
    for constraint, score in selected:
        timestamps = timestamps_by_constraint.get(constraint)
        if not timestamps:
            timestamps = sorted({timestamp for _, timestamp in load_map.keys()})
        exposure_raw = defaultdict(float)
        for zone, timestamp in load_map.keys():
            if timestamp not in timestamps:
                continue
            exposure_raw[zone] += load_map[(zone, timestamp)] * proxy_map.get((zone, timestamp), 0.0)
        exposure_total = sum(exposure_raw.values())
        if exposure_total <= 0:
            continue
        for zone, value in exposure_raw.items():
            planning_burden[zone] += score * (value / exposure_total)

    total = sum(planning_burden.values())
    if total <= 0:
        raise ValueError("CBTCA planning ledger could not produce positive planning burden")

    shares = {zone: value / total for zone, value in planning_burden.items()}
    return shares, {
        "resolved_proxy_tier": resolved_tier,
        "planning_window": planning_window,
        "target_set_size": target_set_size,
        "selected_constraints": [constraint for constraint, _ in selected],
    }, warnings


def _combine_shares(
    operational_shares: Dict[str, float],
    planning_shares: Dict[str, float],
    operational_weight: float,
    planning_weight: float,
) -> Dict[str, float]:
    all_zones = set(operational_shares) | set(planning_shares)
    if not all_zones:
        raise ValueError("CBTCA could not produce any zonal shares")
    combined = {
        zone: operational_weight * operational_shares.get(zone, 0.0) + planning_weight * planning_shares.get(zone, 0.0)
        for zone in all_zones
    }
    total = sum(combined.values())
    if total <= 0:
        raise ValueError("CBTCA combined shares must sum to a positive value")
    return {zone: value / total for zone, value in combined.items()}


def _confidence_label(mode: str, proxy_tier: str | None, used_shadow_prices: bool) -> str:
    if mode == "planning_only_fallback":
        return "Low"
    if proxy_tier == "tier1_direct" and used_shadow_prices:
        return "High"
    if proxy_tier in {"tier1_direct", "tier2_decomposed"}:
        return "Moderate"
    return "Low"


class CBTCAModel(MethodologyModel):
    name = "cbtca"

    def run(self, inputs: MethodologyInputs, params: Dict[str, Any] | None = None) -> MethodologyResult:
        params = params or {}
        op_weight = _safe_float(params.get("operational_weight", 0.40))
        pl_weight = _safe_float(params.get("planning_weight", 0.60))
        op_weight, pl_weight = _normalize_weights(op_weight, pl_weight)

        proxy_tier = params.get("congestion_proxy_tier", "auto")
        operational_load_basis = params.get("operational_load_basis", "gross")
        planning_load_basis = params.get("planning_load_basis", "gross")
        planning_window = params.get("planning_reference_window", params.get("planning_window", "full_year"))
        target_set_size = int(params.get("planning_target_set_size", params.get("target_set_size", 20)))
        outlier_cap_pctile = params.get("outlier_percentile", params.get("outlier_cap_pctile", 99.5))
        if outlier_cap_pctile == "none":
            outlier_cap_pctile = None
        elif outlier_cap_pctile is not None:
            outlier_cap_pctile = float(outlier_cap_pctile)

        planning_shares, planning_meta, warnings = _compute_planning_share(
            inputs=inputs,
            load_basis=planning_load_basis,
            planning_window=planning_window,
            target_set_size=target_set_size,
            proxy_tier=proxy_tier,
        )

        operational_shares, operational_meta, operational_warnings = _compute_operational_share(
            inputs=inputs,
            load_basis=operational_load_basis,
            proxy_tier=proxy_tier,
            outlier_cap_pctile=outlier_cap_pctile,
        )
        warnings.extend(operational_warnings)

        mode = "combined"
        combined_op_weight = op_weight
        combined_pl_weight = pl_weight
        if operational_meta.get("planning_only_fallback"):
            mode = "planning_only_fallback"
            combined_op_weight = 0.0
            combined_pl_weight = 1.0
            warnings.append("operational ledger unavailable; CBTCA ran in planning-only fallback mode")

        shares = _combine_shares(planning_shares if mode == "planning_only_fallback" else operational_shares, planning_shares, combined_op_weight, combined_pl_weight)
        allocations = {zone: share * inputs.tcos_target_usd for zone, share in shares.items()}
        confidence = _confidence_label(mode, planning_meta.get("resolved_proxy_tier") or operational_meta.get("resolved_proxy_tier"), bool(inputs.shadow_price_series))

        assumptions = {
            "operational_weight": combined_op_weight,
            "planning_weight": combined_pl_weight,
            "mode": mode,
            "operational_load_basis": operational_load_basis,
            "planning_load_basis": planning_load_basis,
            "planning_window": planning_window,
            "target_set_size": target_set_size,
            "outlier_cap_pctile": outlier_cap_pctile,
            "resolved_operational_proxy_tier": operational_meta.get("resolved_proxy_tier"),
            "resolved_planning_proxy_tier": planning_meta.get("resolved_proxy_tier"),
            "selected_constraints": planning_meta.get("selected_constraints", []),
            "confidence": confidence,
            "export_rule": inputs.metadata.get("export_rule", "unspecified"),
            "method_note": "CBTCA v1 shared-engine implementation preserves signed congestion proxies, uses normalized operational/planning ledgers, and explicitly labels fallback modes.",
        }

        return MethodologyResult(
            methodology=self.name,
            year=inputs.year,
            shares=shares,
            allocations_usd=allocations,
            assumptions=assumptions,
            warnings=warnings,
        )


class CBTCASensitivityModel(CBTCAModel):
    name = "cbtca_sensitivities"


def load_sensitivity_matrix(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def build_sensitivity_cases(inputs: MethodologyInputs, params: Dict[str, Any] | None = None, matrix: Dict[str, Any] | None = None) -> List[MethodologyResult]:
    params = deepcopy(params or {})
    matrix = matrix or {}
    cbtca_matrix = matrix.get("cbtca", {})
    model = CBTCAModel()
    results: List[MethodologyResult] = []

    def _run_case(label: str, family: str, overrides: Dict[str, Any]) -> None:
        scenario_params = deepcopy(params)
        scenario_params.update(overrides)
        result = model.run(inputs, params=scenario_params)
        result.methodology = f"cbtca_sensitivity_{label}"
        result.assumptions["sensitivity_family"] = family
        result.assumptions["sensitivity_label"] = label
        results.append(result)

    for op_weight, pl_weight in cbtca_matrix.get("operational_planning_weights", []):
        _run_case(
            label=f"weights_{int(op_weight * 100)}_{int(pl_weight * 100)}",
            family="operational_planning_weights",
            overrides={"operational_weight": op_weight, "planning_weight": pl_weight},
        )

    for tier in cbtca_matrix.get("congestion_proxy_tiers", []):
        _run_case(
            label=tier,
            family="congestion_proxy_tiers",
            overrides={"congestion_proxy_tier": tier},
        )

    for rule in cbtca_matrix.get("export_rules", []):
        _run_case(
            label=f"export_rule_{rule.lower()}",
            family="export_rules",
            overrides={
                "operational_load_basis": "net",
                "planning_load_basis": "net",
                "export_rule": rule,
            },
        )

    for window in cbtca_matrix.get("planning_windows", []):
        if window not in {"full_year", "summer_only"}:
            continue
        _run_case(
            label=f"planning_window_{window}",
            family="planning_windows",
            overrides={"planning_reference_window": window},
        )

    for size in cbtca_matrix.get("target_set_sizes", []):
        _run_case(
            label=f"target_set_{size}",
            family="target_set_sizes",
            overrides={"planning_target_set_size": int(size)},
        )

    for cap in cbtca_matrix.get("outlier_caps", []):
        _run_case(
            label=f"outlier_cap_{str(cap).replace('.', '_')}",
            family="outlier_caps",
            overrides={"outlier_percentile": cap},
        )

    return results
