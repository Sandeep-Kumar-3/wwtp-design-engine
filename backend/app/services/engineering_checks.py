from typing import Any, Dict, List


def _check(label: str, value: float, low: float | None = None, high: float | None = None, unit: str = "") -> Dict[str, Any]:
    passed = True
    if low is not None:
        passed = passed and value >= low
    if high is not None:
        passed = passed and value <= high
    if low is not None and high is not None:
        criterion = f"{low:g}–{high:g} {unit}".strip()
    elif low is not None:
        criterion = f">= {low:g} {unit}".strip()
    elif high is not None:
        criterion = f"<= {high:g} {unit}".strip()
    else:
        criterion = "Informational"
    return {
        "label": label,
        "value": value,
        "unit": unit,
        "criterion": criterion,
        "status": "PASS" if passed else "REVIEW",
        "severity": "normal" if passed else "warning",
    }


def build_engineering_checks(
    design_basis: Dict[str, Any],
    criteria: Dict[str, Any],
    primary: Dict[str, Any],
    biological: Dict[str, Any],
    secondary: Dict[str, Any],
    filtration: Dict[str, Any],
    disinfection: Dict[str, Any],
    hydraulic_profile: Dict[str, Any],
) -> Dict[str, Any]:
    bio_criteria = criteria["biological_process"]
    sc_criteria = criteria["secondary_clarifier"]
    filt_criteria = criteria["filtration"]
    dis_criteria = criteria["disinfection"]

    checks: List[Dict[str, Any]] = []
    checks.append(_check(
        "Peak flow / average flow",
        design_basis["peak_factor"], 1.0, None, "x"
    ))
    checks.append(_check(
        "Primary clarifier surface overflow rate",
        primary["surface_overflow_rate_m3_m2_day"],
        20.0, 40.0, "m³/m²·d"
    ))
    calculated_fm = biological["biological"].get(
        "calculated_f_m_ratio",
        biological["biological"]["f_m_ratio_kg_bod_kg_mlvss_day"],
    )
    checks.append(_check(
        "Calculated aeration F/M ratio",
        calculated_fm,
        0.10, 0.40, "kg BOD/kg MLVSS·d"
    ))
    checks.append(_check(
        "Aeration MLSS",
        biological["biological"]["mlss_mg_l"],
        1500.0, 5000.0, "mg/L"
    ))
    checks.append(_check(
        "Secondary clarifier peak surface overflow rate",
        secondary.get("peak_surface_overflow_rate_m3_m2_day", secondary["surface_overflow_rate_m3_m2_day"]),
        15.0, 35.0, "m³/m²·d"
    ))
    checks.append(_check(
        "Filtration rate",
        filtration["filtration_rate_m3_m2_day"],
        5.0, 15.0, "m³/m²·d"
    ))
    checks.append(_check(
        "Operating filter area",
        filtration.get("area_per_operating_filter_m2", filtration["area_per_filter_m2"]),
        0.0, None, "m²/filter"
    ))
    checks.append(_check(
        "Disinfection contact time",
        disinfection["contact_time_min"],
        15.0, 60.0, "min"
    ))

    total_headloss = hydraulic_profile.get("total_headloss_m", 0.0)
    checks.append(_check(
        "Calculated hydraulic headloss",
        total_headloss, None, 3.0, "m"
    ))

    review_count = sum(c["status"] != "PASS" for c in checks)
    return {
        "status": "REVIEW REQUIRED" if review_count else "PASS",
        "pass_count": len(checks) - review_count,
        "review_count": review_count,
        "total_checks": len(checks),
        "checks": checks,
        "criteria_basis": {
            "biological_process": bio_criteria["process"],
            "secondary_clarifier": sc_criteria["surface_overflow_rate_m3_m2_day"],
            "filtration_rate": filt_criteria["filtration_rate_m3_m2_day"],
            "disinfection_contact_time_min": dis_criteria["contact_time_min"],
        },
        "note": "Preliminary engineering checks using configured project criteria. Final design requires project-specific verification and applicable standards.",
    }
