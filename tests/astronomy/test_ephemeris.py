"""Tests for the Swiss Ephemeris backend."""

import pytest

from src.narayana.astronomy.ephemeris import SwissEphemerisBackend


VALIDATION_JD = 2443737.6944444445


def test_backend_reports_swiss_ephemeris_version():
    backend = SwissEphemerisBackend()

    assert backend.version == "2.10.03"


def test_sun_tropical_position():
    backend = SwissEphemerisBackend()

    position = backend.calculate_position(
        VALIDATION_JD,
        "Sun",
        zodiac="tropical",
    )

    assert position.body == "Sun"
    assert position.longitude == pytest.approx(143.9339186240063)
    assert position.latitude == pytest.approx(0.00010213004619766304)
    assert position.distance == pytest.approx(1.0123616056142324)
    assert position.speed_longitude == pytest.approx(0.9611605952492057)


def test_sun_lahiri_sidereal_position():
    backend = SwissEphemerisBackend()

    position = backend.calculate_position(
        VALIDATION_JD,
        "Sun",
        zodiac="sidereal",
        ayanamsa="lahiri",
    )

    assert position.body == "Sun"
    assert position.longitude == pytest.approx(120.37515673924287)
    assert position.latitude == pytest.approx(0.00010213004519595911)
    assert position.distance == pytest.approx(1.0123616056142324)
    assert position.speed_longitude == pytest.approx(0.9611171443874063)


def test_mean_node_position():
    backend = SwissEphemerisBackend()

    position = backend.calculate_position(
        VALIDATION_JD,
        "Mean Node",
        zodiac="tropical",
    )

    assert position.body == "Mean Node"
    assert position.longitude == pytest.approx(178.47109728576146)
    assert position.speed_longitude == pytest.approx(-0.05294859082931548)


def test_true_node_position():
    backend = SwissEphemerisBackend()

    position = backend.calculate_position(
        VALIDATION_JD,
        "True Node",
        zodiac="tropical",
    )

    assert position.body == "True Node"
    assert position.longitude == pytest.approx(177.0994291615304)
    assert position.speed_longitude == pytest.approx(-0.07363167678141651)


def test_sidereal_requires_ayanamsa():
    backend = SwissEphemerisBackend()

    with pytest.raises(
        ValueError,
        match="ayanamsa must be specified",
    ):
        backend.calculate_position(
            VALIDATION_JD,
            "Sun",
            zodiac="sidereal",
        )


def test_unknown_ayanamsa_is_rejected():
    backend = SwissEphemerisBackend()

    with pytest.raises(
        ValueError,
        match="Unsupported ayanamsa",
    ):
        backend.calculate_position(
            VALIDATION_JD,
            "Sun",
            zodiac="sidereal",
            ayanamsa="unknown",
        )


def test_unsupported_zodiac_is_rejected():
    backend = SwissEphemerisBackend()

    with pytest.raises(
        ValueError,
        match="Unsupported zodiac",
    ):
        backend.calculate_position(
            VALIDATION_JD,
            "Sun",
            zodiac="invalid",
        )


def test_unsupported_body_is_rejected():
    backend = SwissEphemerisBackend()

    with pytest.raises(
        ValueError,
        match="Unsupported celestial body",
    ):
        backend.calculate_position(
            VALIDATION_JD,
            "Pluto",
            zodiac="tropical",
        )
