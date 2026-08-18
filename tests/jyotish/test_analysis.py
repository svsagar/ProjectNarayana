"""Tests for deterministic Jyotish chart analysis."""

import pytest

from src.narayana.jyotish.analysis import (
    BhavaAnalysis,
    BhavaLordRelationship,
    GrahaAnalysis,
    analyze_graha,
    calculate_chart_analysis,
)
from src.narayana.jyotish.birth_chart import JyotishBirthChart
from src.narayana.jyotish.graha import Graha
from src.narayana.jyotish.placement import (
    calculate_graha_placement,
)


def test_analyze_sun_exalted():
    placement = calculate_graha_placement(
        Graha.SURYA,
        10.0,
    )

    analysis = analyze_graha(placement)

    assert isinstance(analysis, GrahaAnalysis)
    assert analysis.placement is placement
    assert analysis.dignity_score == 5


def test_analyze_sun_own_sign():
    placement = calculate_graha_placement(
        Graha.SURYA,
        120.0,
    )

    analysis = analyze_graha(placement)

    assert analysis.dignity_score == 4


def test_analyze_sun_debilitated():
    placement = calculate_graha_placement(
        Graha.SURYA,
        190.0,
    )

    analysis = analyze_graha(placement)

    assert analysis.dignity_score == 0


def test_analyze_rejects_invalid_placement():
    with pytest.raises(
        TypeError,
        match="placement must be a GrahaPlacement",
    ):
        analyze_graha(None)


def test_chart_analysis_exposes_bhava_analysis():
    """
    Verify that every Bhava receives structural Rashi information
    derived from the chart's existing Bhava structure.
    """

    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=0.0,
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    assert len(analysis.bhava_analysis) == 12
    assert all(
        isinstance(item, BhavaAnalysis)
        for item in analysis.bhava_analysis
    )


def test_first_bhava_uses_first_bhava_cusp_rashi():
    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=0.0,
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    first = analysis.get_bhava_analysis(1)

    assert first.bhava_number == 1
    assert first.rashi_number == 1
    assert first.rashi_name == "Mesha"
    assert first.lord is Graha.MANGALA
    assert first.grahas == ()
    assert first.lord_bhava_number is None


def test_bhava_analysis_follows_cusp_rashi():
    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=0.0,
        bhava_cusps=(
            0.0,
            35.0,
            70.0,
            100.0,
            130.0,
            160.0,
            190.0,
            220.0,
            250.0,
            280.0,
            310.0,
            340.0,
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    assert analysis.get_bhava_analysis(1).rashi_number == 1
    assert analysis.get_bhava_analysis(2).rashi_number == 2
    assert analysis.get_bhava_analysis(3).rashi_number == 3
    assert analysis.get_bhava_analysis(7).rashi_number == 7
    assert analysis.get_bhava_analysis(12).rashi_number == 12


def test_bhava_analysis_rejects_invalid_number():
    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=0.0,
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    with pytest.raises(
        ValueError,
        match="bhava_number must be an integer between 1 and 12",
    ):
        analysis.get_bhava_analysis(0)

    with pytest.raises(
        ValueError,
        match="bhava_number must be an integer between 1 and 12",
    ):
        analysis.get_bhava_analysis(13)

    with pytest.raises(
        ValueError,
        match="bhava_number must be an integer between 1 and 12",
    ):
        analysis.get_bhava_analysis(True)


def test_bhava_lord_relationships_expose_all_twelve_bhavas():
    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=0.0,
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    assert len(analysis.bhava_lord_relationships) == 12
    assert all(
        isinstance(
            relationship,
            BhavaLordRelationship,
        )
        for relationship in analysis.bhava_lord_relationships
    )


def test_bhava_lord_relationship_follows_bhava_analysis():
    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=0.0,
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    for bhava_number in range(1, 13):
        bhava = analysis.get_bhava_analysis(bhava_number)
        relationship = analysis.get_bhava_lord_relationship(
            bhava_number
        )

        assert relationship.bhava_number == bhava.bhava_number
        assert relationship.rashi_number == bhava.rashi_number
        assert relationship.rashi_name == bhava.rashi_name
        assert relationship.lord is bhava.lord
        assert (
            relationship.lord_bhava_number
            == bhava.lord_bhava_number
        )


def test_bhava_lord_relationship_detects_same_bhava():
    """
    With an Aries ascendant and Mars placed in the 1st Bhava,
    the 1st Bhava lord occupies the same Bhava.
    """

    from src.narayana.jyotish.integration import (
        GrahaBhavaPlacement,
    )

    mars = GrahaBhavaPlacement(
        graha=Graha.MANGALA,
        longitude=10.0,
        rashi_number=1,
        rashi_name="Mesha",
        nakshatra_number=1,
        nakshatra_name="Ashwini",
        nakshatra_pada=1,
        bhava_number=1,
    )

    chart = JyotishBirthChart(
        placements=(mars,),
        ascendant_longitude=0.0,
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = analysis.get_bhava_lord_relationship(1)

    assert relationship.lord is Graha.MANGALA
    assert relationship.lord_bhava_number == 1
    assert relationship.house_distance == 1
    assert relationship.is_same_bhava is True
    assert relationship.lord_is_present is True


def test_bhava_lord_relationship_calculates_forward_house_distance():
    """
    With an Aries ascendant, Mars rules the 1st Bhava.
    If Mars occupies the 7th Bhava, the lord is seven houses
    from the Bhava it rules.
    """

    from src.narayana.jyotish.integration import (
        GrahaBhavaPlacement,
    )

    mars = GrahaBhavaPlacement(
        graha=Graha.MANGALA,
        longitude=190.0,
        rashi_number=7,
        rashi_name="Tula",
        nakshatra_number=14,
        nakshatra_name="Chitra",
        nakshatra_pada=1,
        bhava_number=7,
    )

    chart = JyotishBirthChart(
        placements=(mars,),
        ascendant_longitude=0.0,
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = analysis.get_bhava_lord_relationship(1)

    assert relationship.bhava_number == 1
    assert relationship.lord is Graha.MANGALA
    assert relationship.lord_bhava_number == 7
    assert relationship.house_distance == 7
    assert relationship.is_same_bhava is False


def test_bhava_lord_relationship_handles_missing_lord():
    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=0.0,
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = analysis.get_bhava_lord_relationship(1)

    assert relationship.lord is Graha.MANGALA
    assert relationship.lord_bhava_number is None
    assert relationship.house_distance is None
    assert relationship.is_same_bhava is False
    assert relationship.lord_is_present is False


def test_bhava_lord_relationship_rejects_invalid_number():
    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=0.0,
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    with pytest.raises(
        ValueError,
        match="bhava_number must be an integer between 1 and 12",
    ):
        analysis.get_bhava_lord_relationship(0)

    with pytest.raises(
        ValueError,
        match="bhava_number must be an integer between 1 and 12",
    ):
        analysis.get_bhava_lord_relationship(13)

    with pytest.raises(
        ValueError,
        match="bhava_number must be an integer between 1 and 12",
    ):
        analysis.get_bhava_lord_relationship(True)


def test_bhava_lord_relationships_are_ordered_by_bhava():
    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=0.0,
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    assert tuple(
        relationship.bhava_number
        for relationship in analysis.bhava_lord_relationships
    ) == tuple(range(1, 13))

def test_bhava_rashi_follows_ascendant_in_whole_sign_sequence():
    """
    Bhava Rashi assignment follows the Ascendant Rashi
    sequentially through the twelve Rashis.
    """
    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=30.0,  # Vrishabha
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    expected = (
        2,   # 1st Bhava - Vrishabha
        3,   # 2nd - Mithuna
        4,   # 3rd - Karka
        5,   # 4th - Simha
        6,   # 5th - Kanya
        7,   # 6th - Tula
        8,   # 7th - Vrishchika
        9,   # 8th - Dhanu
        10,  # 9th - Makara
        11,  # 10th - Kumbha
        12,  # 11th - Meena
        1,   # 12th - Mesha
    )

    actual = tuple(
        analysis.get_bhava_analysis(
            bhava_number
        ).rashi_number
        for bhava_number in range(1, 13)
    )

    assert actual == expected


def test_bhava_rashi_assignment_wraps_after_meena():
    """
    Bhava Rashi assignment wraps from Meena back to Mesha.
    """
    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=330.0,  # Meena
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    assert (
        analysis.get_bhava_analysis(1).rashi_number
        == 12
    )

    assert (
        analysis.get_bhava_analysis(2).rashi_number
        == 1
    )

    assert (
        analysis.get_bhava_analysis(3).rashi_number
        == 2
    )

    assert (
        analysis.get_bhava_analysis(12).rashi_number
        == 11
    )


def test_bhava_lord_follows_assigned_bhava_rashi():
    """
    The Bhava lord must always be the lord of the
    Rashi assigned to that Bhava.
    """
    chart = JyotishBirthChart(
        placements=(),
        ascendant_longitude=30.0,  # Vrishabha
        bhava_cusps=tuple(
            float(number * 30)
            for number in range(12)
        ),
        astronomy_result=None,
    )

    analysis = calculate_chart_analysis(chart)

    expected_lords = (
        Graha.SHUKRA,   # Vrishabha
        Graha.BUDHA,    # Mithuna
        Graha.CHANDRA,  # Karka
        Graha.SURYA,    # Simha
        Graha.BUDHA,    # Kanya
        Graha.SHUKRA,   # Tula
        Graha.MANGALA,  # Vrishchika
        Graha.GURU,     # Dhanu
        Graha.SHANI,    # Makara
        Graha.SHANI,    # Kumbha
        Graha.GURU,     # Meena
        Graha.MANGALA,  # Mesha
    )

    actual = tuple(
        analysis.get_bhava_analysis(
            bhava_number
        ).lord
        for bhava_number in range(1, 13)
    )

    assert actual == expected_lords
