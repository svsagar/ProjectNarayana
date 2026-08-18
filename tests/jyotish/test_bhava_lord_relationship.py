"""Tests for deterministic Bhava Lord Relationship analysis."""

import pytest

from src.narayana.jyotish.analysis import (
    BhavaLordRelationship,
    calculate_chart_analysis,
)
from src.narayana.jyotish.birth_chart import JyotishBirthChart
from src.narayana.jyotish.dignity import Dignity
from src.narayana.jyotish.graha import Graha
from src.narayana.jyotish.placement import (
    calculate_graha_placement,
)


def make_chart(
    *,
    placements=(),
    ascendant_longitude=0.0,
    bhava_cusps=None,
):
    """Create a lightweight JyotishBirthChart for relationship tests."""

    if bhava_cusps is None:
        bhava_cusps = tuple(
            float(number * 30)
            for number in range(12)
        )

    return JyotishBirthChart(
        placements=tuple(placements),
        ascendant_longitude=ascendant_longitude,
        bhava_cusps=tuple(bhava_cusps),
        astronomy_result=None,
    )


def test_bhava_lord_relationship_type_is_exposed():
    chart = make_chart()

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(1)
    )

    assert isinstance(
        relationship,
        BhavaLordRelationship,
    )


def test_bhava_lord_relationship_has_correct_bhava_number():
    chart = make_chart()

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(5)
    )

    assert relationship.lord is Graha.SURYA


def test_bhava_lord_relationship_exposes_lord():
    chart = make_chart(
        ascendant_longitude=0.0,
    )

    analysis = calculate_chart_analysis(chart)

    # Aries rises, therefore the 1st Bhava lord is Mars.
    relationship = (
        analysis.get_bhava_lord_relationship(1)
    )

    assert relationship.lord is Graha.MANGALA


def test_bhava_lord_relationship_exposes_lord_bhava():
    # Aries rises. Mars is placed in the 1st Bhava.
    placement = calculate_graha_placement(
        Graha.MANGALA,
        10.0,
    )

    chart = make_chart(
        placements=(placement,),
        ascendant_longitude=0.0,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(1)
    )

    assert relationship.lord is Graha.MANGALA
    assert relationship.lord_bhava_number == 1


def test_bhava_lord_relationship_exposes_lord_rashi():
    # Aries rises. Mars at 10° is in Mesha.
    placement = calculate_graha_placement(
        Graha.MANGALA,
        10.0,
    )

    chart = make_chart(
        placements=(placement,),
        ascendant_longitude=0.0,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(1)
    )

    assert relationship.lord_rashi_number == 1
    assert relationship.lord_rashi_name == "Mesha"


def test_bhava_lord_relationship_handles_lord_without_placement():
    chart = make_chart()

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(1)
    )

    assert relationship.lord is Graha.MANGALA
    assert relationship.lord_bhava_number is None
    assert relationship.lord_rashi_number is None
    assert relationship.lord_rashi_name is None
    assert relationship.lord_dignity is None
    assert relationship.lord_dignity_score is None


def test_bhava_lord_relationship_for_second_bhava():
    # Aries rises:
    # 1st Bhava = Mesha, lord Mars
    # 2nd Bhava = Vrishabha, lord Venus
    chart = make_chart(
        ascendant_longitude=0.0,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(2)
    )

    assert relationship.lord is Graha.SHUKRA


def test_bhava_lord_relationship_for_tenth_bhava():
    # Aries rises:
    # 10th Bhava = Makara, lord Saturn.
    chart = make_chart(
        ascendant_longitude=0.0,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(10)
    )

    assert relationship.lord is Graha.SHANI
    assert relationship.lord_rashi_number is None
    assert relationship.lord_bhava_number is None


def test_bhava_lord_relationship_follows_ascendant():
    # Taurus rises:
    # 1st Bhava = Vrishabha, lord Venus.
    chart = make_chart(
        ascendant_longitude=30.0,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(1)
    )

    assert relationship.lord is Graha.SHUKRA
    assert relationship.lord_rashi_number is None


def test_bhava_lord_relationship_for_taurus_ascendant_second_bhava():
    # Taurus rises:
    # 2nd Bhava = Mithuna, lord Mercury.
    chart = make_chart(
        ascendant_longitude=30.0,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(2)
    )

    assert relationship.lord is Graha.BUDHA


def test_lord_rashi_and_dignity_are_exposed():
    # Mars at 280 degrees is in Makara (10) and exalted.
    placement = calculate_graha_placement(
        Graha.MANGALA,
        280.0,
    )

    chart = make_chart(
        placements=(placement,),
        ascendant_longitude=0.0,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(1)
    )

    assert relationship.lord is Graha.MANGALA
    assert relationship.lord_rashi_number == 10
    assert relationship.lord_rashi_name == "Makara"
    assert relationship.lord_dignity == Dignity.EXALTED


def test_lord_dignity_score_is_exposed():
    # Mars at 280 degrees is exalted in Makara.
    placement = calculate_graha_placement(
        Graha.MANGALA,
        280.0,
    )

    chart = make_chart(
        placements=(placement,),
        ascendant_longitude=0.0,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(1)
    )

    assert relationship.lord_dignity_score == 5


def test_lord_relationship_tracks_lord_placement_bhava():
    # Aries rises.
    # Mars at 280° is in Makara.
    # With the supplied 30° Bhava cusps, this is the 10th Bhava.
    placement = calculate_graha_placement(
        Graha.MANGALA,
        280.0,
    )

    chart = make_chart(
        placements=(placement,),
        ascendant_longitude=0.0,
    )

    analysis = calculate_chart_analysis(chart)

    relationship = (
        analysis.get_bhava_lord_relationship(1)
    )

    assert relationship.lord is Graha.MANGALA
    assert relationship.lord_bhava_number == 10
    assert relationship.lord_rashi_number == 10
    assert relationship.lord_rashi_name == "Makara"


def test_relationships_are_available_for_all_twelve_bhavas():
    chart = make_chart()

    analysis = calculate_chart_analysis(chart)

    relationships = tuple(
        analysis.get_bhava_lord_relationship(
            bhava_number
        )
        for bhava_number in range(1, 13)
    )

    assert len(relationships) == 12

    assert tuple(
        relationship.lord
        for relationship in relationships
    ) == (
        Graha.MANGALA,
        Graha.SHUKRA,
        Graha.BUDHA,
        Graha.CHANDRA,
        Graha.SURYA,
        Graha.BUDHA,
        Graha.SHUKRA,
        Graha.MANGALA,
        Graha.GURU,
        Graha.SHANI,
        Graha.SHANI,
        Graha.GURU,
    )

def test_relationship_lords_follow_rashi_lords():
    chart = make_chart(
        ascendant_longitude=0.0,
    )

    analysis = calculate_chart_analysis(chart)

    expected_lords = (
        Graha.MANGALA,  # 1 Mesha
        Graha.SHUKRA,   # 2 Vrishabha
        Graha.BUDHA,    # 3 Mithuna
        Graha.CHANDRA,  # 4 Karka
        Graha.SURYA,    # 5 Simha
        Graha.BUDHA,    # 6 Kanya
        Graha.SHUKRA,   # 7 Tula
        Graha.MANGALA,  # 8 Vrishchika
        Graha.GURU,     # 9 Dhanu
        Graha.SHANI,    # 10 Makara
        Graha.SHANI,    # 11 Kumbha
        Graha.GURU,     # 12 Meena
    )

    actual_lords = tuple(
        analysis.get_bhava_lord_relationship(
            bhava_number
        ).lord
        for bhava_number in range(1, 13)
    )

    assert actual_lords == expected_lords


def test_bhava_lord_relationship_rejects_invalid_bhava_number():
    chart = make_chart()

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


def test_bhava_lord_relationship_is_deterministic():
    placement = calculate_graha_placement(
        Graha.MANGALA,
        280.0,
    )

    chart = make_chart(
        placements=(placement,),
        ascendant_longitude=0.0,
    )

    analysis_one = calculate_chart_analysis(chart)
    analysis_two = calculate_chart_analysis(chart)

    assert (
        analysis_one.get_bhava_lord_relationship(1)
        == analysis_two.get_bhava_lord_relationship(1)
    )