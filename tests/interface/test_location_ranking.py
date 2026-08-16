"""Deterministic ranking of ambiguous location searches.

Indian place names and their well-established aliases should prefer the Indian
result, without turning India into an unconditional filter: an explicit country
qualifier always wins, and unrelated international queries are untouched.

The provider is mocked throughout. Payloads mirror the shape and the ordering
quirks of real Open-Meteo responses (which, for example, ranks Kochi, Japan
above Kochi, Kerala).
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from src.narayana.interface import http as interface_http
from src.narayana.interface.http import (
    INDIA_PREFERRED_NAMES,
    INDIAN_CITY_ALIASES,
    app,
    search_locations,
)

client = TestClient(app)


# --------------------------------------------------------------------------
# A small fake provider index
# --------------------------------------------------------------------------

def place(name, lat, lon, tz, country, code, admin1=None, population=None,
          feature="PPL"):
    return {
        "name": name, "latitude": lat, "longitude": lon, "timezone": tz,
        "country": country, "country_code": code, "admin1": admin1,
        "population": population, "feature_code": feature,
    }


KOCHI_IN = place("Kochi", 9.93988, 76.26022, "Asia/Kolkata", "India", "IN",
                 "Kerala", 633553)
KOCHI_JP = place("Kochi", 33.55, 133.53333, "Asia/Tokyo", "Japan", "JP",
                 "Kochi", 321999, "PPLA")
KOCHI_MH = place("Kochi", 19.1, 73.2, "Asia/Kolkata", "India", "IN", "Maharashtra")
THIRUVANANTHAPURAM = place("Thiruvananthapuram", 8.4855, 76.9492, "Asia/Kolkata",
                           "India", "IN", "Kerala", 743691, "PPLA")
BENGALURU = place("Bengaluru", 12.97194, 77.59369, "Asia/Kolkata", "India", "IN",
                  "Karnataka", 5104047, "PPLA")
MUMBAI = place("Mumbai", 19.07283, 72.88261, "Asia/Kolkata", "India", "IN",
               "Maharashtra", 12691836, "PPLA")
KOLKATA = place("Kolkata", 22.56263, 88.36304, "Asia/Kolkata", "India", "IN",
                "West Bengal", 4631392, "PPLA")
CHENNAI = place("Chennai", 13.08784, 80.27847, "Asia/Kolkata", "India", "IN",
                "Tamil Nadu", 4328063, "PPLA")

LONDON_UK = place("London", 51.50853, -0.12574, "Europe/London",
                  "United Kingdom", "GB", "England", 8961989, "PPLC")
LONDON_CA = place("London", 42.98339, -81.23304, "America/Toronto", "Canada",
                  "CA", "Ontario", 346765, "PPLA2")
NEW_YORK_US = place("New York", 40.71427, -74.00597, "America/New_York",
                    "United States", "US", "New York", 8804190, "PPL")

# Junk the real provider returns for "Cochin".
COCHIN_CA = place("Cochin", 53.08346, -108.33465, "America/Regina", "Canada",
                  "CA", "Saskatchewan")
COCHINESTI_RO = place("Cochinesti", 44.58094, 24.76339, "Europe/Bucharest",
                      "Romania", "RO", "Arges")


def install(monkeypatch, index):
    """Mock the provider. ``index`` maps (name.lower(), countryCode) -> results.

    A miss on an explicit country code falls back to the unrestricted list
    filtered by that code, mirroring provider behaviour.
    """
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        name = (request.url.params.get("name") or "").lower()
        code = request.url.params.get("countryCode")
        seen.append({"name": name, "countryCode": code})

        results = index.get(name, [])
        if code:
            results = [r for r in results if r["country_code"] == code]
        return httpx.Response(200, json={"results": results})

    monkeypatch.setattr(
        interface_http, "_geocoding_client",
        lambda: httpx.Client(transport=httpx.MockTransport(handler)),
    )
    return seen


INDEX = {
    # Provider order deliberately puts Japan first, as it really does.
    "kochi": [KOCHI_JP, KOCHI_IN, KOCHI_MH],
    "cochin": [COCHIN_CA, COCHINESTI_RO],
    "thiruvananthapuram": [THIRUVANANTHAPURAM],
    "trivandrum": [],
    "bengaluru": [BENGALURU],
    "bangalore": [BENGALURU],
    "mumbai": [MUMBAI],
    "bombay": [],
    "kolkata": [KOLKATA],
    "calcutta": [],
    "chennai": [CHENNAI],
    "madras": [],
    "london": [LONDON_UK, LONDON_CA],
    "new york": [NEW_YORK_US],
}


# --------------------------------------------------------------------------
# Indian preference for ambiguous bare names
# --------------------------------------------------------------------------

@pytest.mark.parametrize("query,expected_name,expected_admin1", [
    ("Kochi", "Kochi", "Kerala"),
    ("Cochin", "Kochi", "Kerala"),
    ("Trivandrum", "Thiruvananthapuram", "Kerala"),
    ("Bangalore", "Bengaluru", "Karnataka"),
    ("Bombay", "Mumbai", "Maharashtra"),
    ("Calcutta", "Kolkata", "West Bengal"),
    ("Madras", "Chennai", "Tamil Nadu"),
    ("Mumbai", "Mumbai", "Maharashtra"),
])
def test_indian_cities_and_aliases_rank_first(monkeypatch, query, expected_name,
                                              expected_admin1):
    install(monkeypatch, INDEX)
    results = search_locations(query)

    assert results, f"{query} returned nothing"
    top = results[0]
    assert top["name"] == expected_name
    assert top["admin1"] == expected_admin1
    assert top["country_code"] == "IN"
    assert top["timezone"] == "Asia/Kolkata"


def test_kochi_outranks_the_provider_first_result(monkeypatch):
    """Japan is returned first by the provider; India must still win."""
    install(monkeypatch, INDEX)
    results = search_locations("Kochi")

    assert results[0]["country"] == "India"
    assert results[0]["label"] == "Kochi, Kerala, India"
    # Japan is preserved for selection, not discarded.
    assert any(r["country"] == "Japan" for r in results)


def test_alias_is_translated_before_querying_the_provider(monkeypatch):
    seen = install(monkeypatch, INDEX)
    search_locations("Cochin")

    india_calls = [c for c in seen if c["countryCode"] == "IN"]
    assert india_calls, "an India-restricted call should be made"
    assert india_calls[0]["name"] == "kochi"
    # The unrestricted search still uses what the user typed.
    assert any(c["name"] == "cochin" and c["countryCode"] is None for c in seen)


def test_international_candidates_are_retained_for_selection(monkeypatch):
    install(monkeypatch, INDEX)
    results = search_locations("Cochin")

    assert results[0]["country_code"] == "IN"
    assert {r["country"] for r in results} & {"Canada", "Romania"}


# --------------------------------------------------------------------------
# India must not be an unconditional filter
# --------------------------------------------------------------------------

def test_london_still_resolves_to_the_united_kingdom(monkeypatch):
    install(monkeypatch, INDEX)
    results = search_locations("London")

    assert results[0]["country"] == "United Kingdom"
    assert results[0]["timezone"] == "Europe/London"


def test_new_york_still_resolves_to_the_united_states(monkeypatch):
    install(monkeypatch, INDEX)
    results = search_locations("New York")

    assert results[0]["country"] == "United States"
    assert results[0]["timezone"] == "America/New_York"


def test_no_india_call_is_made_for_a_non_indian_query(monkeypatch):
    seen = install(monkeypatch, INDEX)
    search_locations("London")
    assert all(call["countryCode"] is None for call in seen)


# --------------------------------------------------------------------------
# Explicit country context always wins
# --------------------------------------------------------------------------

def test_explicit_country_qualifier_beats_provider_order(monkeypatch):
    install(monkeypatch, INDEX)
    results = search_locations("London, Canada")

    assert results[0]["country"] == "Canada"
    assert results[0]["admin1"] == "Ontario"
    assert results[0]["timezone"] == "America/Toronto"


def test_explicit_country_qualifier_disables_the_india_preference(monkeypatch):
    seen = install(monkeypatch, INDEX)
    results = search_locations("Kochi, Japan")

    assert results[0]["country"] == "Japan"
    assert results[0]["timezone"] == "Asia/Tokyo"
    assert all(call["countryCode"] is None for call in seen)


def test_admin_region_qualifier_is_honoured(monkeypatch):
    install(monkeypatch, INDEX)
    results = search_locations("Kochi, Kerala")

    assert results[0]["admin1"] == "Kerala"
    assert results[0]["country_code"] == "IN"


# --------------------------------------------------------------------------
# Ranking mechanics
# --------------------------------------------------------------------------

def test_population_breaks_ties_between_same_named_places(monkeypatch):
    """Both are exact name matches with no qualifier; the larger city wins."""
    install(monkeypatch, {"london": [LONDON_CA, LONDON_UK]})   # UK second
    results = search_locations("London")
    assert results[0]["country"] == "United Kingdom"


def test_provider_order_is_the_final_tie_breaker(monkeypatch):
    first = place("Springfield", 1.0, 1.0, "UTC", "Country A", "AA")
    second = place("Springfield", 2.0, 2.0, "UTC", "Country B", "BB")
    install(monkeypatch, {"springfield": [first, second]})

    results = search_locations("Springfield")
    assert [r["country"] for r in results] == ["Country A", "Country B"]


def test_duplicate_positions_are_collapsed(monkeypatch):
    install(monkeypatch, {"mumbai": [MUMBAI]})
    results = search_locations("Mumbai")
    # Returned by both the India-restricted and unrestricted calls.
    assert len(results) == 1


def test_response_shape_is_unchanged(monkeypatch):
    install(monkeypatch, INDEX)
    body = client.get("/api/v1/location/search", params={"q": "Kochi"}).json()

    assert set(body) == {"query", "results"}
    assert set(body["results"][0]) == {
        "name", "latitude", "longitude", "timezone",
        "country", "country_code", "admin1", "admin2", "label",
    }


def test_india_call_failure_falls_back_to_the_general_search(monkeypatch):
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if request.url.params.get("countryCode") == "IN":
            raise httpx.ConnectError("boom", request=request)
        return httpx.Response(200, json={"results": [KOCHI_JP]})

    monkeypatch.setattr(
        interface_http, "_geocoding_client",
        lambda: httpx.Client(transport=httpx.MockTransport(handler)),
    )

    results = search_locations("Kochi")
    assert results[0]["country"] == "Japan"


def test_alias_table_is_small_and_consistent():
    assert len(INDIAN_CITY_ALIASES) <= 15
    for alias, canonical in INDIAN_CITY_ALIASES.items():
        assert alias == alias.lower()
        assert alias != canonical.lower()
        assert canonical.lower() in INDIA_PREFERRED_NAMES


# --------------------------------------------------------------------------
# The calculation stays independent of the geocoder
# --------------------------------------------------------------------------

def test_chart_endpoint_never_calls_the_geocoder(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError("the chart endpoint must not contact the geocoder")

    monkeypatch.setattr(
        interface_http, "_geocoding_client",
        lambda: httpx.Client(transport=httpx.MockTransport(handler)),
    )

    response = client.post("/api/v1/chart", json={
        "birth_date": "1978-08-17", "birth_time": "10:10:00",
        "timezone": "Asia/Kolkata", "latitude": 9.5916, "longitude": 76.5222,
        "place_name": "Alappuzha, India",
    })
    assert response.status_code == 200


def test_ranked_coordinates_reach_birthinput_unchanged(monkeypatch):
    install(monkeypatch, INDEX)
    top = search_locations("Cochin")[0]

    served = client.post("/api/v1/chart", json={
        "birth_date": "1978-08-17", "birth_time": "10:10:00",
        "timezone": top["timezone"], "latitude": top["latitude"],
        "longitude": top["longitude"], "place_name": top["label"],
    }).json()

    assert served["input"]["latitude"] == 9.93988
    assert served["input"]["longitude"] == 76.26022
    assert served["input"]["timezone"] == "Asia/Kolkata"
    assert served["input"]["place_name"] == "Kochi, Kerala, India"


def test_manual_override_still_beats_the_ranked_result(monkeypatch):
    install(monkeypatch, INDEX)
    top = search_locations("Kochi")[0]

    served = client.post("/api/v1/chart", json={
        "birth_date": "1978-08-17", "birth_time": "10:10:00",
        "timezone": "Asia/Tokyo", "latitude": 33.55, "longitude": 133.53333,
        "place_name": top["label"],
    }).json()

    # The submitted values win; place_name remains descriptive metadata only.
    assert served["input"]["latitude"] == 33.55
    assert served["input"]["timezone"] == "Asia/Tokyo"
    assert served["input"]["place_name"] == "Kochi, Kerala, India"
