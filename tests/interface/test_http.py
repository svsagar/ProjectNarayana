"""Tests for the HTTP interface layer.

These tests verify the *integration contract only*: that the HTTP layer
forwards requests to the existing application API, and that every value it
serves is identical to what the calculation core returns. They deliberately do
not re-assert astronomical or Jyotish correctness -- that is already covered by
the astronomy and jyotish suites.
"""

from datetime import date, time

import pytest
from fastapi.testclient import TestClient

from src.narayana.astronomy.models import BirthInput, CalculationConfig
from src.narayana.interface.http import app
from src.narayana.jyotish.api import calculate_jyotish_birth_chart
from src.narayana.jyotish.dignity import get_dignity
from src.narayana.jyotish.graha import get_graha_name

client = TestClient(app)

VALID_REQUEST = {
    "birth_date": "1978-08-17",
    "birth_time": "10:10:00",
    "timezone": "Asia/Kolkata",
    "latitude": 9.5916,
    "longitude": 76.5222,
    "place_name": "Alappuzha, India",
}


def reference_chart():
    return calculate_jyotish_birth_chart(
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude=9.5916,
            longitude=76.5222,
            place_name="Alappuzha, India",
        ),
        CalculationConfig(),
    )


def test_health_reports_core_and_ephemeris():
    body = client.get("/api/v1/health").json()
    assert body["status"] == "ok"
    assert body["ephemeris_version"]


def test_config_options_come_from_the_core():
    body = client.get("/api/v1/config/options").json()
    defaults = CalculationConfig()

    assert body["defaults"]["zodiac"] == defaults.zodiac
    assert body["defaults"]["ayanamsa"] == defaults.ayanamsa
    assert body["defaults"]["node"] == defaults.node
    assert body["defaults"]["house_system"] == defaults.house_system

    # The UI must never offer an ayanamsa the ephemeris backend cannot apply.
    from src.narayana.astronomy.ephemeris import SwissEphemerisBackend

    offered = {option["value"] for option in body["ayanamsas"]}
    assert offered == set(SwissEphemerisBackend._AYANAMSA_MAP)
    assert {option["value"] for option in body["nodes"]} == {"mean", "true"}


def test_chart_response_matches_the_calculation_core_exactly():
    """The HTTP layer must not recompute or alter any domain value."""
    expected = reference_chart()
    response = client.post("/api/v1/chart", json=VALID_REQUEST)
    assert response.status_code == 200
    served = response.json()

    assert served["ascendant"]["longitude"] == expected.ascendant_longitude
    assert len(served["grahas"]) == len(expected.placements)

    served_by_graha = {g["graha"]: g for g in served["grahas"]}
    for placement in expected.placements:
        graha = served_by_graha[placement.graha.value]
        assert graha["english"] == get_graha_name(placement.graha)
        assert graha["longitude"] == placement.longitude
        assert graha["rashi_number"] == placement.rashi_number
        assert graha["rashi_name"] == placement.rashi_name
        assert graha["nakshatra_number"] == placement.nakshatra_number
        assert graha["nakshatra_name"] == placement.nakshatra_name
        assert graha["nakshatra_pada"] == placement.nakshatra_pada
        assert graha["bhava_number"] == placement.bhava_number
        assert graha["dignity"] == get_dignity(
            placement.graha, placement.rashi_number
        ).value

    served_cusps = [b["cusp_longitude"] for b in served["bhavas"]]
    assert served_cusps == list(expected.bhava_cusps)

    metadata = expected.astronomy_result.calculation_metadata
    assert served["metadata"]["julian_day_ut"] == metadata.julian_day_ut
    assert served["metadata"]["ephemeris_version"] == metadata.ephemeris_version


def test_panchanga_matches_the_core():
    expected = reference_chart().astronomy_result.panchanga
    served = client.post("/api/v1/chart", json=VALID_REQUEST).json()["panchanga"]

    assert served["tithi"]["number"] == expected.tithi
    assert served["tithi"]["name"] == expected.tithi_name
    assert served["tithi"]["paksha"] == expected.tithi_paksha
    assert served["nakshatra"]["number"] == expected.nakshatra
    assert served["nakshatra"]["pada"] == expected.nakshatra_pada
    assert served["yoga"]["number"] == expected.yoga
    assert served["karana"]["number"] == expected.karana
    assert served["vara"]["number"] == expected.vara


def test_configuration_is_forwarded_to_the_core():
    payload = dict(VALID_REQUEST, config={
        "zodiac": "sidereal",
        "ayanamsa": "lahiri",
        "node": "true",
        "house_system": "placidus",
    })
    served = client.post("/api/v1/chart", json=payload).json()
    assert served["config"]["node"] == "true"
    assert served["metadata"]["node_mode"] == "true"

    expected = calculate_jyotish_birth_chart(
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone="Asia/Kolkata",
            latitude=9.5916,
            longitude=76.5222,
        ),
        CalculationConfig(node="true"),
    )
    served_rahu = next(g for g in served["grahas"] if g["graha"] == "Rahu")
    expected_rahu = expected.get_placement(
        next(p.graha for p in expected.placements if p.graha.value == "Rahu")
    )
    assert served_rahu["longitude"] == expected_rahu.longitude


def test_chart_endpoint_is_deterministic():
    first = client.post("/api/v1/chart", json=VALID_REQUEST).json()
    second = client.post("/api/v1/chart", json=VALID_REQUEST).json()
    assert first == second


@pytest.mark.parametrize("patch", [
    {"latitude": 120.0},
    {"longitude": -400.0},
    {"birth_date": "not-a-date"},
    {"birth_time": "25:00"},
])
def test_invalid_input_returns_422(patch):
    response = client.post("/api/v1/chart", json=dict(VALID_REQUEST, **patch))
    assert response.status_code == 422


def test_missing_required_field_returns_422():
    payload = {k: v for k, v in VALID_REQUEST.items() if k != "birth_date"}
    assert client.post("/api/v1/chart", json=payload).status_code == 422


def test_unknown_timezone_returns_422():
    response = client.post("/api/v1/chart", json=dict(VALID_REQUEST, timezone="Mars/Olympus"))
    assert response.status_code == 422
    assert "timezone" in response.json()["detail"].lower()


def test_unsupported_ayanamsa_is_rejected_by_the_core():
    response = client.post("/api/v1/chart", json=dict(VALID_REQUEST, config={
        "zodiac": "sidereal",
        "ayanamsa": "not_a_real_ayanamsa",
        "node": "mean",
        "house_system": "placidus",
    }))
    assert response.status_code == 422
    assert "ayanamsa" in response.json()["detail"].lower()


def test_unsupported_node_is_rejected_by_the_core():
    response = client.post("/api/v1/chart", json=dict(VALID_REQUEST, config={
        "zodiac": "sidereal",
        "ayanamsa": "lahiri",
        "node": "wobbly",
        "house_system": "placidus",
    }))
    assert response.status_code == 422
    assert "node" in response.json()["detail"].lower()


def test_web_interface_is_served():
    page = client.get("/")
    assert page.status_code == 200
    assert "NARAYANA" in page.text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/styles.css").status_code == 200
