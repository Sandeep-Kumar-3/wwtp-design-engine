import pytest

from app.calculations.filtration import (
    design_filtration,
)


def test_filtration():

    result = design_filtration(
        design_flow_m3_day=10000,
        filtration_rate_m3_m2_day=10,
        number_of_filters=5,
        filter_length_to_width_ratio=1.5,
    )

    assert result.total_area_m2 == pytest.approx(1000)

    assert result.area_per_filter_m2 == pytest.approx(200)

    assert result.filter_width_m == pytest.approx(
        (200 / 1.5) ** 0.5
    )

    assert result.filter_length_m == pytest.approx(
        result.filter_width_m * 1.5
    )

    assert result.standby_filters == 1
    assert result.operating_filters == 4


def test_invalid_filtration_rate():

    with pytest.raises(ValueError):

        design_filtration(
            design_flow_m3_day=10000,
            filtration_rate_m3_m2_day=0,
            number_of_filters=5,
        )