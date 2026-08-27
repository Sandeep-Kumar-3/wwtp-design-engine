import pytest

from app.calculations.screening import design_screen


def test_screen_design():

    result = design_screen(
        peak_flow_m3_day=25000,
        number_of_channels=2,
        approach_velocity_m_s=0.8,
        water_depth_m=1.2,
        bar_spacing_m=0.025,
        open_area_ratio=0.60,
    )

    assert result.design_flow_m3_s == pytest.approx(
        25000 / 86400
    )

    assert result.flow_per_channel_m3_s == pytest.approx(
        25000 / 86400 / 2
    )

    assert result.channel_area_m2 == pytest.approx(
        (25000 / 86400 / 2) / 0.8
    )

    assert result.channel_width_m == pytest.approx(
        ((25000 / 86400 / 2) / 0.8) / 1.2
    )


def test_invalid_screen_flow():

    with pytest.raises(ValueError):

        design_screen(
            peak_flow_m3_day=0,
            number_of_channels=2,
            approach_velocity_m_s=0.8,
            water_depth_m=1.2,
            bar_spacing_m=0.025,
        )