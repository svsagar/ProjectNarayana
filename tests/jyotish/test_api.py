"""Tests for the public Jyotish birth-chart API."""

from datetime import date, time

import pytest

from src.narayana.astronomy.models import (
    BirthInput,
    CalculationConfig,
)

from src.narayana.jyotish.api import (
    calculate_jyotish_birth_chart,
)
from src.narayana.jyotish.birth_chart import JyotishBirthChart


def make_birth_input() -> BirthInput:
    return BirthInput(
        birth_date=date(1978, 8, 17),
        birth_time=time(10, 10),
        timezone="Asia/Kolkata",
        latitude=9.5916,
        longitude=76.5222,
    )


def test_api_rejects_invalid_birth_input():
    with pytest.raises(
        TypeError,
        match="birth_input must be a BirthInput",
    ):
        calculate_jyotish_birth_chart(
            None,  # type: ignore[arg-type]
        )


def test_api_rejects_invalid_calculation_config():
    with pytest.raises(
        TypeError,
        match="calculation_config must be a CalculationConfig",
    ):
        calculate_jyotish_birth_chart(
            make_birth_input(),
            "invalid",  # type: ignore[arg-type]
        )


def test_default_calculation_config_is_supported(
    monkeypatch,
):
    called = {}

    def fake_calculate(
        birth_input,
        calculation_config,
    ):
        called["birth_input"] = birth_input
        called["calculation_config"] = calculation_config

        from src.narayana.astronomy.models import (
            AscendantPosition,
            AstronomyResult,
            CalculationMetadata,
            CelestialPosition,
            HouseCusps,
        )

        return AstronomyResult(
            birth_input=birth_input,
            calculation_config=calculation_config,
            calculation_metadata=CalculationMetadata(
                local_datetime=None,
                timezone_name="Asia/Kolkata",
                utc_datetime=None,
                latitude=birth_input.latitude,
                longitude=birth_input.longitude,
                coordinate_source=None,
                coordinate_precision=None,
                julian_day_ut=0.0,
                ephemeris_implementation="test",
                ephemeris_version="test",
                ayanamsa=calculation_config.ayanamsa,
                node_mode=calculation_config.node,
            ),
            positions=(
                CelestialPosition(
                    body="Sun",
                    longitude=0.0,
                    latitude=0.0,
                    distance=1.0,
                    speed_longitude=1.0,
                ),
                CelestialPosition(
                    body="Moon",
                    longitude=30.0,
                    latitude=0.0,
                    distance=1.0,
                    speed_longitude=1.0,
                ),
                CelestialPosition(
                    body="Mars",
                    longitude=60.0,
                    latitude=0.0,
                    distance=1.0,
                    speed_longitude=1.0,
                ),
                CelestialPosition(
                    body="Mercury",
                    longitude=90.0,
                    latitude=0.0,
                    distance=1.0,
                    speed_longitude=1.0,
                ),
                CelestialPosition(
                    body="Jupiter",
                    longitude=120.0,
                    latitude=0.0,
                    distance=1.0,
                    speed_longitude=1.0,
                ),
                CelestialPosition(
                    body="Venus",
                    longitude=150.0,
                    latitude=0.0,
                    distance=1.0,
                    speed_longitude=1.0,
                ),
                CelestialPosition(
                    body="Saturn",
                    longitude=180.0,
                    latitude=0.0,
                    distance=1.0,
                    speed_longitude=1.0,
                ),
                CelestialPosition(
                    body="Rahu",
                    longitude=210.0,
                    latitude=0.0,
                    distance=1.0,
                    speed_longitude=-1.0,
                ),
                CelestialPosition(
                    body="Ketu",
                    longitude=30.0,
                    latitude=0.0,
                    distance=1.0,
                    speed_longitude=-1.0,
                ),
            ),
            ascendant=AscendantPosition(
                longitude=15.0,
            ),
            houses=HouseCusps(
                cusps=(
                    0.0,
                    30.0,
                    60.0,
                    90.0,
                    120.0,
                    150.0,
                    180.0,
                    210.0,
                    240.0,
                    270.0,
                    300.0,
                    330.0,
                ),
            ),
            panchanga=None,
        )

    monkeypatch.setattr(
        "src.narayana.jyotish.api.calculate_astronomy",
        fake_calculate,
    )

    result = calculate_jyotish_birth_chart(
        make_birth_input(),
    )

    assert isinstance(result, JyotishBirthChart)
    assert len(result.placements) == 9

    assert called["birth_input"] == make_birth_input()
    assert called["calculation_config"] == CalculationConfig()


def test_explicit_calculation_config_is_forwarded(
    monkeypatch,
):
    received = {}

    def fake_calculate(
        birth_input,
        calculation_config,
    ):
        received["config"] = calculation_config

        from src.narayana.astronomy.models import (
            AscendantPosition,
            AstronomyResult,
            CalculationMetadata,
            CelestialPosition,
            HouseCusps,
        )

        positions = tuple(
            CelestialPosition(
                body=body,
                longitude=float(index * 30),
                latitude=0.0,
                distance=1.0,
                speed_longitude=0.0,
            )
            for index, body in enumerate(
                (
                    "Sun",
                    "Moon",
                    "Mars",
                    "Mercury",
                    "Jupiter",
                    "Venus",
                    "Saturn",
                    "Rahu",
                    "Ketu",
                )
            )
        )

        return AstronomyResult(
            birth_input=birth_input,
            calculation_config=calculation_config,
            calculation_metadata=CalculationMetadata(
                local_datetime=None,
                timezone_name="Asia/Kolkata",
                utc_datetime=None,
                latitude=birth_input.latitude,
                longitude=birth_input.longitude,
                coordinate_source=None,
                coordinate_precision=None,
                julian_day_ut=0.0,
                ephemeris_implementation="test",
                ephemeris_version="test",
                ayanamsa=calculation_config.ayanamsa,
                node_mode=calculation_config.node,
            ),
            positions=positions,
            ascendant=AscendantPosition(
                longitude=15.0,
            ),
            houses=HouseCusps(
                cusps=(
                    0.0,
                    30.0,
                    60.0,
                    90.0,
                    120.0,
                    150.0,
                    180.0,
                    210.0,
                    240.0,
                    270.0,
                    300.0,
                    330.0,
                ),
            ),
            panchanga=None,
        )

    monkeypatch.setattr(
        "src.narayana.jyotish.api.calculate_astronomy",
        fake_calculate,
    )

    config = CalculationConfig(
        zodiac="sidereal",
        ayanamsa="lahiri",
        node="true",
        ephemeris="swiss_ephemeris",
        house_system="placidus",
    )

    result = calculate_jyotish_birth_chart(
        make_birth_input(),
        config,
    )

    assert isinstance(result, JyotishBirthChart)
    assert received["config"] == config