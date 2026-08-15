"""Tests for the complete Graha chart structure."""

import pytest

from src.narayana.jyotish.chart import (
    GrahaChart,
    calculate_graha_chart,
)
from src.narayana.jyotish.graha import GRAHAS, Graha


def complete_longitudes():
    return {
        Graha.SURYA: 0.0,
        Graha.CHANDRA: 30.0,
        Graha.MANGALA: 60.0,
        Graha.BUDHA: 90.0,
        Graha.GURU: 120.0,
        Graha.SHUKRA: 150.0,
        Graha.SHANI: 180.0,
        Graha.RAHU: 210.0,
        Graha.KETU: 240.0,
    }


def test_complete_graha_chart():
    chart = calculate_graha_chart(
        complete_longitudes()
    )

    assert isinstance(chart, GrahaChart)
    assert len(chart.placements) == 9


def test_chart_contains_all_nine_grahas():
    chart = calculate_graha_chart(
        complete_longitudes()
    )

    assert tuple(
        placement.graha
        for placement in chart.placements
    ) == GRAHAS


@pytest.mark.parametrize(
    "graha,expected_longitude",
    [
        (Graha.SURYA, 0.0),
        (Graha.CHANDRA, 30.0),
        (Graha.MANGALA, 60.0),
        (Graha.BUDHA, 90.0),
        (Graha.GURU, 120.0),
        (Graha.SHUKRA, 150.0),
        (Graha.SHANI, 180.0),
        (Graha.RAHU, 210.0),
        (Graha.KETU, 240.0),
    ],
)
def test_chart_preserves_longitudes(graha, expected_longitude):
    chart = calculate_graha_chart(
        complete_longitudes()
    )

    placement = chart.get_placement(graha)

    assert placement.longitude == expected_longitude


def test_get_placement_returns_correct_graha():
    chart = calculate_graha_chart(
        complete_longitudes()
    )

    placement = chart.get_placement(Graha.SURYA)

    assert placement.graha is Graha.SURYA
    assert placement.rashi_number == 1
    assert placement.rashi_name == "Mesha"


def test_chart_is_in_canonical_graha_order():
    chart = calculate_graha_chart(
        complete_longitudes()
    )

    assert [
        placement.graha
        for placement in chart.placements
    ] == list(GRAHAS)


@pytest.mark.parametrize(
    "graha",
    [
        "Sun",
        "Surya",
        1,
        None,
        True,
    ],
)
def test_get_placement_rejects_invalid_graha(graha):
    chart = calculate_graha_chart(
        complete_longitudes()
    )

    with pytest.raises(TypeError, match="graha must be a Graha"):
        chart.get_placement(graha)


def test_missing_graha_is_rejected():
    longitudes = complete_longitudes()
    del longitudes[Graha.KETU]

    with pytest.raises(
        ValueError,
        match="Missing Graha longitudes: Ketu",
    ):
        calculate_graha_chart(longitudes)


def test_unexpected_graha_is_rejected():
    longitudes = complete_longitudes()
    longitudes["Sun"] = 120.0  # type: ignore[index]

    with pytest.raises(
        ValueError,
        match="Unexpected Graha longitudes",
    ):
        calculate_graha_chart(longitudes)


@pytest.mark.parametrize(
    "invalid_longitudes",
    [
        None,
        [],
        (),
        "invalid",
        123,
    ],
)
def test_invalid_longitudes_container_is_rejected(
    invalid_longitudes,
):
    with pytest.raises(
        TypeError,
        match="longitudes must be a dictionary",
    ):
        calculate_graha_chart(invalid_longitudes)


def test_chart_is_immutable():
    chart = calculate_graha_chart(
        complete_longitudes()
    )

    with pytest.raises(AttributeError):
        chart.placements = ()


def test_placements_are_immutable():
    chart = calculate_graha_chart(
        complete_longitudes()
    )

    with pytest.raises(AttributeError):
        chart.placements[0].longitude = 100.0