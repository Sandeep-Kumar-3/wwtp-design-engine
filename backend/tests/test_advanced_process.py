import pytest

from app.calculations.filtration import design_filtration


# ============================================================
# ADVANCED PROCESS — FILTRATION
# ============================================================

def test_filtration():
    result = design_filtration(
        flow_m3_day=10000,
        filtration_rate_m3_m2_hr=8,
        number_of_filters=4,
    )

    assert result.required_filter_area_m2 > 0
    assert result.area_per_filter_m2 > 0
    assert result.filter_length_m > 0
    assert result.filter_width_m > 0
    assert result.backwash_flow_m3_hr > 0


def test_invalid_filtration():
    with pytest.raises(ValueError):
        design_filtration(
            flow_m3_day=10000,
            number_of_filters=0,
        )


def test_filtration_design_dimensions():
    result = design_filtration(
        flow_m3_day=10000,
        filtration_rate_m3_m2_day=10,
        number_of_filters=5,
        filter_length_to_width_ratio=1.5,
    )

    assert result.required_filter_area_m2 == pytest.approx(1000)
    assert result.area_per_filter_m2 == pytest.approx(200)

    expected_width = (200 / 1.5) ** 0.5
    expected_length = expected_width * 1.5

    assert result.filter_width_m == pytest.approx(expected_width)
    assert result.filter_length_m == pytest.approx(expected_length)


def test_filtration_standby_filters():
    result = design_filtration(
        flow_m3_day=10000,
        filtration_rate_m3_m2_day=10,
        number_of_filters=5,
    )

    assert result.standby_filters == 1


def test_filtration_backwash():
    result = design_filtration(
        flow_m3_day=10000,
        filtration_rate_m3_m2_hr=8,
        number_of_filters=4,
    )

    assert result.backwash_flow_m3_hr > 0


def test_invalid_filtration_rate():
    with pytest.raises(ValueError):
        design_filtration(
            flow_m3_day=10000,
            filtration_rate_m3_m2_hr=0,
            number_of_filters=4,
        )