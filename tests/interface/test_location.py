"""Tests for the location-resolution layer.

The external geocoding provider is always mocked: these tests never depend on
live Open-Meteo availability. Location resolution only produces *inputs* for
BirthInput -- it takes no part in any astronomical or Jyotish calculation.
"""

from datetime import date, time

import httpx
import pytest
from fastapi.testclient import TestClient

from src.narayana.astronomy.models import BirthInput, CalculationConfig
from src.narayana.interface import http as interface_http
from src.narayana.interface.http import (
    GEOCODING_URL,
    LocationServiceError,
    app,
    search_locations,
)
from src.narayana.jyotish.api import calculate_jyotish_birth_chart

client = TestClient(app)


# --------------------------------------------------------------------------
# Provider mocking
# --------------------------------------------------------------------------

KOTTAYAM = {
    "name": "Kottayam",
    "latitude": 9.59273,
    "longitude": 76.52213,
    "timezone": "Asia/Kolkata",
    "country": "India",
    "country_code": "IN",
    "admin1": "Kerala",
    "admin2": "Kottayam",
}

MUMBAI = {
    "name": "Mumbai",
    "latitude": 19.07283,
    "longitude": 72.88261,
    "timezone": "Asia/Kolkata",
    "country": "India",
    "country_code": "IN",
    "admin1": "Maharashtra",
}

LONDON = {
    "name": "London",
    "latitude": 51.50853,
    "longitude": -0.12574,
    "timezone": "Europe/London",
    "country": "United Kingdom",
    "country_code": "GB",
    "admin1": "England",
}

LONDON_ONTARIO = {
    "name": "London",
    "latitude": 42.98339,
    "longitude": -81.23304,
    "timezone": "America/Toronto",
    "country": "Canada",
    "country_code": "CA",
    "admin1": "Ontario",
}


def install_provider(monkeypatch, handler):
    """Route the interface's geocoding client through a mock transport."""

    def factory() -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(interface_http, "_geocoding_client", factory)


def respond_with(payload, status_code=200):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == httpx.URL(GEOCODING_URL).path
        return httpx.Response(status_code, json=payload)

    return handler


# --------------------------------------------------------------------------
# Successful resolution
# --------------------------------------------------------------------------

def test_successful_resolution_returns_normalised_candidate(monkeypatch):
    install_provider(monkeypatch, respond_with({"results": [KOTTAYAM]}))

    response = client.get("/api/v1/location/search", params={"q": "Kottayam"})
    assert response.status_code == 200
    body = response.json()

    assert body["query"] == "Kottayam"
    assert len(body["results"]) == 1

    result = body["results"][0]
    assert result["name"] == "Kottayam"
    assert result["latitude"] == KOTTAYAM["latitude"]
    assert result["longitude"] == KOTTAYAM["longitude"]
    assert result["timezone"] == "Asia/Kolkata"
    assert result["country"] == "India"
    assert result["country_code"] == "IN"
    assert result["admin1"] == "Kerala"
    assert result["admin2"] == "Kottayam"
    assert result["label"] == "Kottayam, Kerala, India"


def test_query_and_count_are_forwarded_to_the_provider(monkeypatch):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["name"] = request.url.params.get("name")
        seen["count"] = request.url.params.get("count")
        return httpx.Response(200, json={"results": [KOTTAYAM]})

    install_provider(monkeypatch, handler)
    client.get("/api/v1/location/search", params={"q": "Kottayam", "count": 5})

    assert seen["name"] == "Kottayam"
    assert seen["count"] == "5"


def test_multiple_candidates_are_all_returned(monkeypatch):
    install_provider(monkeypatch, respond_with({"results": [LONDON, LONDON_ONTARIO]}))

    body = client.get("/api/v1/location/search", params={"q": "London"}).json()
    assert len(body["results"]) == 2

    labels = [r["label"] for r in body["results"]]
    assert labels == ["London, England, United Kingdom", "London, Ontario, Canada"]

    # Distinct coordinates and timezones must survive normalisation, so the
    # user can tell the candidates apart before choosing.
    assert body["results"][0]["timezone"] == "Europe/London"
    assert body["results"][1]["timezone"] == "America/Toronto"
    assert body["results"][0]["latitude"] != body["results"][1]["latitude"]


# --------------------------------------------------------------------------
# Empty / no result
# --------------------------------------------------------------------------

def test_no_results_key_is_reported_as_empty(monkeypatch):
    """Open-Meteo omits "results" entirely when nothing matches."""
    install_provider(monkeypatch, respond_with({"generationtime_ms": 0.5}))

    response = client.get("/api/v1/location/search", params={"q": "zzzzzzzzzz"})
    assert response.status_code == 200
    assert response.json()["results"] == []


def test_empty_results_list_is_reported_as_empty(monkeypatch):
    install_provider(monkeypatch, respond_with({"results": []}))
    response = client.get("/api/v1/location/search", params={"q": "zzzzzzzzzz"})
    assert response.status_code == 200
    assert response.json()["results"] == []


def test_blank_query_is_rejected():
    assert client.get("/api/v1/location/search", params={"q": ""}).status_code == 422
    assert client.get("/api/v1/location/search").status_code == 422

    with pytest.raises(ValueError):
        search_locations("   ")


# --------------------------------------------------------------------------
# Provider failure modes
# --------------------------------------------------------------------------

def test_network_failure_returns_503_with_manual_entry_advice(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    install_provider(monkeypatch, handler)
    response = client.get("/api/v1/location/search", params={"q": "Kottayam"})

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert "unavailable" in detail.lower()
    assert "manually" in detail.lower()


def test_timeout_returns_503(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    install_provider(monkeypatch, handler)
    assert client.get(
        "/api/v1/location/search", params={"q": "Kottayam"}
    ).status_code == 503


def test_provider_error_status_returns_503(monkeypatch):
    install_provider(monkeypatch, respond_with({"error": True}, status_code=500))
    assert client.get(
        "/api/v1/location/search", params={"q": "Kottayam"}
    ).status_code == 503


def test_invalid_json_returns_503(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"<html>not json</html>")

    install_provider(monkeypatch, handler)
    assert client.get(
        "/api/v1/location/search", params={"q": "Kottayam"}
    ).status_code == 503


@pytest.mark.parametrize("payload", [
    ["unexpected", "list"],
    {"results": "not-a-list"},
    {"results": {"name": "Kottayam"}},
])
def test_malformed_response_structure_returns_503(monkeypatch, payload):
    install_provider(monkeypatch, respond_with(payload))
    assert client.get(
        "/api/v1/location/search", params={"q": "Kottayam"}
    ).status_code == 503


def test_results_without_usable_coordinates_are_reported_as_malformed(monkeypatch):
    install_provider(monkeypatch, respond_with({"results": [
        {"name": "Nowhere"},                                  # no coordinates
        {"name": "Bad", "latitude": "x", "longitude": 1.0, "timezone": "UTC"},
        {"latitude": 1.0, "longitude": 1.0, "timezone": "UTC"},  # no name
    ]}))

    with pytest.raises(LocationServiceError):
        search_locations("Kottayam")

    assert client.get(
        "/api/v1/location/search", params={"q": "Kottayam"}
    ).status_code == 503


def test_out_of_range_coordinates_are_discarded(monkeypatch):
    install_provider(monkeypatch, respond_with({"results": [
        dict(KOTTAYAM, name="Impossible", latitude=120.0),
        KOTTAYAM,
    ]}))

    results = search_locations("Kottayam")
    assert [r["name"] for r in results] == ["Kottayam"]


def test_partial_results_keep_the_usable_candidates(monkeypatch):
    install_provider(monkeypatch, respond_with({"results": [
        {"name": "Broken"},
        MUMBAI,
    ]}))

    results = search_locations("Mumbai")
    assert len(results) == 1
    assert results[0]["latitude"] == MUMBAI["latitude"]


# --------------------------------------------------------------------------
# Propagation into the calculation
# --------------------------------------------------------------------------

def chart_request(candidate: dict) -> dict:
    """The request the UI builds from a resolved location."""
    return {
        "birth_date": "1978-08-17",
        "birth_time": "10:10:00",
        "timezone": candidate["timezone"],
        "latitude": candidate["latitude"],
        "longitude": candidate["longitude"],
        "place_name": candidate["label"],
    }


@pytest.mark.parametrize("raw", [KOTTAYAM, MUMBAI, LONDON])
def test_resolved_values_propagate_into_the_chart_calculation(monkeypatch, raw):
    install_provider(monkeypatch, respond_with({"results": [raw]}))

    resolved = client.get(
        "/api/v1/location/search", params={"q": raw["name"]}
    ).json()["results"][0]

    served = client.post("/api/v1/chart", json=chart_request(resolved)).json()

    # Latitude, longitude and timezone reach the calculation unchanged.
    assert served["input"]["latitude"] == raw["latitude"]
    assert served["input"]["longitude"] == raw["longitude"]
    assert served["input"]["timezone"] == raw["timezone"]
    assert served["input"]["place_name"] == resolved["label"]

    # And the chart equals a direct core call with those exact values.
    expected = calculate_jyotish_birth_chart(
        BirthInput(
            birth_date=date(1978, 8, 17),
            birth_time=time(10, 10),
            timezone=raw["timezone"],
            latitude=raw["latitude"],
            longitude=raw["longitude"],
            place_name=resolved["label"],
        ),
        CalculationConfig(),
    )
    assert served["ascendant"]["longitude"] == expected.ascendant_longitude
    assert served["metadata"]["julian_day_ut"] == (
        expected.astronomy_result.calculation_metadata.julian_day_ut
    )


def test_different_locations_produce_different_charts(monkeypatch):
    charts = {}
    for raw in (KOTTAYAM, MUMBAI, LONDON):
        install_provider(monkeypatch, respond_with({"results": [raw]}))
        resolved = client.get(
            "/api/v1/location/search", params={"q": raw["name"]}
        ).json()["results"][0]
        charts[raw["name"]] = client.post(
            "/api/v1/chart", json=chart_request(resolved)
        ).json()

    ascendants = {name: c["ascendant"]["longitude"] for name, c in charts.items()}
    assert len(set(ascendants.values())) == 3

    # A different timezone must shift the moment of birth, and therefore the
    # Julian Day, even for the same civil clock time.
    assert charts["Kottayam"]["metadata"]["julian_day_ut"] == (
        charts["Mumbai"]["metadata"]["julian_day_ut"]
    )
    assert charts["London"]["metadata"]["julian_day_ut"] != (
        charts["Kottayam"]["metadata"]["julian_day_ut"]
    )


def test_manual_override_after_resolution_is_honoured(monkeypatch):
    """The calculation uses the final form values, not the resolved ones."""
    install_provider(monkeypatch, respond_with({"results": [KOTTAYAM]}))
    resolved = client.get(
        "/api/v1/location/search", params={"q": "Kottayam"}
    ).json()["results"][0]

    overridden = dict(
        chart_request(resolved),
        latitude=19.07283,
        longitude=72.88261,
        timezone="Asia/Kolkata",
    )
    served = client.post("/api/v1/chart", json=overridden).json()

    assert served["input"]["latitude"] == 19.07283
    assert served["input"]["longitude"] == 72.88261
    assert served["input"]["latitude"] != resolved["latitude"]

    baseline = client.post("/api/v1/chart", json=chart_request(resolved)).json()
    assert served["ascendant"]["longitude"] != baseline["ascendant"]["longitude"]


def test_resolution_endpoint_does_not_affect_the_chart_contract(monkeypatch):
    """The calculation endpoint never calls the geocoder."""
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError("The chart endpoint must not contact the geocoder")

    install_provider(monkeypatch, handler)

    response = client.post("/api/v1/chart", json={
        "birth_date": "1978-08-17",
        "birth_time": "10:10:00",
        "timezone": "Asia/Kolkata",
        "latitude": 9.5916,
        "longitude": 76.5222,
        "place_name": "Alappuzha, India",
    })
    assert response.status_code == 200
