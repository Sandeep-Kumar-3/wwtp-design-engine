from app.calculations.tertiary import (
    design_filtration,
)

from app.calculations.disinfection import (
    design_chlorination,
    design_uv,
)

from app.calculations.final_effluent import (
    calculate_final_effluent,
)


def test_filtration():

    result = design_filtration(
        average_flow_m3_day=10000
    )

    assert result.required_filter_area_m2 > 0
    assert result.number_of_filters == 4


def test_chlorination():

    result = design_chlorination(
        peak_flow_m3_day=25000
    )

    assert result.chlorine_required_kg_day > 0
    assert result.contact_tank_volume_m3 > 0


def test_uv():

    result = design_uv(
        peak_flow_m3_day=25000
    )

    assert result.required_uv_power_kw > 0


def test_final_effluent():

    result = calculate_final_effluent(
        average_flow_m3_day=10000,
        influent_bod_mg_l=250,
        influent_tss_mg_l=300,
        target_bod_mg_l=20,
        target_tss_mg_l=10,
    )

    assert result.bod_removal_percent > 90
    assert result.tss_removal_percent > 90
    assert result.bod_load_kg_day == 200
    assert result.tss_load_kg_day == 100