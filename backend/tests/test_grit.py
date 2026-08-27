import pytest

from app.calculations.grit import design_grit_chamber


def test_grit_design():

    result = design_grit_chamber(
        peak_flow_m3_day=25000,
        number_of_units=2,
        detention_time_s=60,
        horizontal_velocity_m_s=0.30,
        water_depth_m=1.0,
    )

    peak_flow_m3_s = 25000 / 86400
    flow_per_unit = peak_flow_m3_s / 2

    expected_volume = flow_per_unit * 60

    assert result.peak_flow_m3_s == pytest.approx(
        peak_flow_m3_s
    )

    assert result.volume_per_unit_m3 == pytest.approx(
        expected_volume
    )

    assert result.total_volume_m3 == pytest.approx(
        expected_volume * 2
    )

    expected_area = flow_per_unit / 0.30

    assert result.width_m == pytest.approx(
        expected_area / 1.0
    )


def test_invalid_grit_flow():

    with pytest.raises(ValueError):

        design_grit_chamber(
            peak_flow_m3_day=0,
            number_of_units=2,
            detention_time_s=60,
            horizontal_velocity_m_s=0.30,
            water_depth_m=1.0,
        )