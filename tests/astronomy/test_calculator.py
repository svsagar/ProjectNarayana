"""Tests for the canonical Astronomy Engine calculation orchestration."""

from datetime import date, time

import pytest

from src.narayana.astronomy.calculator import calculate
from src.narayana.astronomy.models import BirthInput, CalculationConfig


VALIDATION_BIRTH = BirthInput(
    birth_date=date(1978, 8, 17),
    birth_time=time(10, 10),
    timezone="Asia/Kolkata",
    latitude=9.5916,
    longitude=76.5222,
)


def test_calculate_returns_requested_bodies():
    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="mean",
    )

    result = calculate(
        VALIDATION_BIRTH,
        config,
        bodies=("Sun", "Moon"),
    )

    assert result.birth_input == VALIDATION_BIRTH
    assert result.calculation_config == config
    assert result.calculation_metadata.julian_day_ut == pytest.approx(
        2443737.6944444445
    )
    assert [position.body for position in result.positions] == ["Sun", "Moon"]


def test_calculate_mean_node_mode_is_supported():
    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="mean",
    )

    result = calculate(
        VALIDATION_BIRTH,
        config,
        bodies=("Mean Node",),
    )

    assert len(result.positions) == 1
    assert result.positions[0].body == "Mean Node"


def test_calculate_true_node_mode_is_supported():
    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="true",
    )

    result = calculate(
        VALIDATION_BIRTH,
        config,
        bodies=("True Node",),
    )

    assert len(result.positions) == 1
    assert result.positions[0].body == "True Node"

    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="true",
    )

    result = calculate(
        VALIDATION_BIRTH,
        config,
        bodies=("Rahu",),
    )

    position = result.positions[0]

    assert position.body == "Rahu"
    assert position.longitude == pytest.approx(153.54066727676695)