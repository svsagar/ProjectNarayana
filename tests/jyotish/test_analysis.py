"""Tests for deterministic Jyotish chart analysis."""

from datetime import date, time

import pytest

from src.narayana.astronomy.models import (
    BirthInput,
    CalculationConfig,
)

from src.narayana.jyotish.analysis import (
    ChartAnalysis,
    RASHI_LORDS,
    calculate_chart_analysis,
    get_rashi_lord,
)
from src.narayana.jyotish.api import calculate_jyotish_birth_chart
from src.narayana.jyotish.graha import Graha


def make_chart():
    return calculate_jyotish_birth_chart(
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude=9.5916,
            longitude=76.5222,
        ),
        CalculationConfig(),
    )


@pytest.mark.parametrize(
    "rashi_number,expected_lord",
    [
        (1, Graha.MANGALA),
        (2, Graha.SHUKRA),
        (3, Graha.BUDHA),
        (4, Graha.CHANDRA),
        (5, Graha.SURYA),
        (6, Graha.BUDHA),
        (7, Graha.SHUKRA),
        (8, Graha.MANGALA),
        (9, Graha.GURU),
        (10, Graha.SHANI),
        (11, Graha.SHANI),
        (12, Graha.GURU),
    ],
)
def test_rashi_lords(
    rashi_number,
    expected_lord,
):
    assert get_rashi_lord(rashi_number) is expected_lord


def test_all_rashis_have_lords():
    assert len(RASHI_LORDS) == 12


@pytest.mark.parametrize(
    "invalid_rashi",
    [
        0,
        13,
        -1,
        1.0,
        "1",
        None,
        True,
    ],
)
def test_invalid_rashi_lord_input_is_rejected(
    invalid_rashi,
):
    with pytest.raises(
        ValueError,
        match="rashi_number must be an integer between 1 and 12",
    ):
        get_rashi_lord(invalid_rashi)


def test_chart_analysis_returns_expected_type():
    analysis = calculate_chart_analysis(
        make_chart()
    )

    assert isinstance(analysis, ChartAnalysis)


def test_analysis_contains_all_twelve_rashis():
    analysis = calculate_chart_analysis(
        make_chart()
    )

    assert len(analysis.rashi_occupancy) == 12


def test_analysis_contains_all_twelve_bhavas():
    analysis = calculate_chart_analysis(
        make_chart()
    )

    assert len(analysis.bhava_occupancy) == 12


def test_rashi_occupancy_is_in_canonical_order():
    analysis = calculate_chart_analysis(
        make_chart()
    )

    assert [
        item.rashi_number
        for item in analysis.rashi_occupancy
    ] == list(range(1, 13))


def test_bhava_occupancy_is_in_canonical_order():
    analysis = calculate_chart_analysis(
        make_chart()
    )

    assert [
        item.bhava_number
        for item in analysis.bhava_occupancy
    ] == list(range(1, 13))


def test_each_rashi_has_correct_lord():
    analysis = calculate_chart_analysis(
        make_chart()
    )

    for occupancy in analysis.rashi_occupancy:
        assert occupancy.lord is get_rashi_lord(
            occupancy.rashi_number
        )


def test_ascendant_rashi_is_consistent():
    chart = make_chart()
    analysis = calculate_chart_analysis(chart)

    expected_rashi = chart.placements[0].rashi_number

    assert analysis.ascendant_rashi_number in range(1, 13)
    assert analysis.ascendant_rashi_name
    assert analysis.ascendant_rashi_lord is get_rashi_lord(
        analysis.ascendant_rashi_number
    )


def test_rashi_occupancy_contains_all_chart_grahas():
    chart = make_chart()
    analysis = calculate_chart_analysis(chart)

    occupied = tuple(
        graha
        for rashi in analysis.rashi_occupancy
        for graha in rashi.grahas
    )

    assert set(occupied) == {
        placement.graha
        for placement in chart.placements
    }


def test_bhava_occupancy_contains_all_chart_grahas():
    chart = make_chart()
    analysis = calculate_chart_analysis(chart)

    occupied = tuple(
        graha
        for bhava in analysis.bhava_occupancy
        for graha in bhava.grahas
    )

    assert set(occupied) == {
        placement.graha
        for placement in chart.placements
    }


def test_rashi_occupancy_lookup():
    analysis = calculate_chart_analysis(
        make_chart()
    )

    result = analysis.get_rashi_occupancy(1)

    assert result.rashi_number == 1
    assert result.rashi_name == "Mesha"
    assert result.lord is Graha.MANGALA


def test_bhava_occupancy_lookup():
    analysis = calculate_chart_analysis(
        make_chart()
    )

    result = analysis.get_bhava_occupancy(1)

    assert result.bhava_number == 1


def test_rashi_lord_lookup_from_analysis():
    analysis = calculate_chart_analysis(
        make_chart()
    )

    assert (
        analysis.get_rashi_lord(5)
        is Graha.SURYA
    )


@pytest.mark.parametrize(
    "invalid_rashi",
    [0, 13, -1, 1.0, "1", None, True],
)
def test_analysis_rashi_lookup_rejects_invalid_input(
    invalid_rashi,
):
    analysis = calculate_chart_analysis(
        make_chart()
    )

    with pytest.raises(
        ValueError,
        match="rashi_number must be an integer between 1 and 12",
    ):
        analysis.get_rashi_occupancy(invalid_rashi)


@pytest.mark.parametrize(
    "invalid_bhava",
    [0, 13, -1, 1.0, "1", None, True],
)
def test_analysis_bhava_lookup_rejects_invalid_input(
    invalid_bhava,
):
    analysis = calculate_chart_analysis(
        make_chart()
    )

    with pytest.raises(
        ValueError,
        match="bhava_number must be an integer between 1 and 12",
    ):
        analysis.get_bhava_occupancy(invalid_bhava)


def test_invalid_chart_is_rejected():
    with pytest.raises(
        TypeError,
        match="chart must be a JyotishBirthChart",
    ):
        calculate_chart_analysis(None)