import pytest

from app.calculations.flow import calculate_flow


def test_10_mld_flow():
    result = calculate_flow(10, peak_factor=2.5)

    assert result.average_m3_day == 10000
    assert result.average_m3_hour == pytest.approx(416.6667)
    assert result.average_m3_sec == pytest.approx(0.1157407407, rel=1e-6)

    assert result.peak_mld == 25
    assert result.peak_m3_day == 25000