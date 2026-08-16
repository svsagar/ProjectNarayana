"""HTTP interface for Project Narayana.

This module is a *presentation boundary only*. It performs request validation,
calls the existing application API, and serialises the returned domain objects.

No astronomical or Jyotish calculation is performed here or in the browser.
Every value served originates from:

    src.narayana.jyotish.api.calculate_jyotish_birth_chart()
        -> src.narayana.astronomy.calculator.calculate()
            -> Swiss Ephemeris

Run with:
    uvicorn src.narayana.interface.http:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from datetime import date as _date, time as _time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfoNotFoundError

import httpx
import swisseph as swe
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.narayana.astronomy.ephemeris import SwissEphemerisBackend
from src.narayana.astronomy.models import (
    AstronomyResult,
    BirthInput,
    CalculationConfig,
)
from src.narayana.astronomy.panchanga import (
    get_karana_name,
    get_nakshatra_name as get_panchanga_nakshatra_name,
    get_yoga_name,
)
from src.narayana.jyotish.analysis import calculate_chart_analysis
from src.narayana.jyotish.api import calculate_jyotish_birth_chart
from src.narayana.jyotish.birth_chart import JyotishBirthChart
from src.narayana.jyotish.dignity import get_dignity, get_dignity_score
from src.narayana.jyotish.graha import get_graha_name
from src.narayana.jyotish.rashi import get_rashi_name, get_rashi_number

WEB_DIR = Path(__file__).parent / "web"
VERSION_FILE = Path(__file__).resolve().parents[3] / "VERSION.txt"

# The zodiac vocabulary enforced by SwissEphemerisBackend.
SUPPORTED_ZODIACS = ("sidereal", "tropical")

# Open-Meteo geocoding provider. Used only to resolve a place name into
# coordinates and an IANA timezone for the birth input; it takes no part in
# any astronomical or Jyotish calculation.
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
GEOCODING_TIMEOUT_SECONDS = 8.0
GEOCODING_DEFAULT_COUNT = 5
GEOCODING_MAX_COUNT = 10

# Weekday labels for the Vara integer (isoweekday: Monday = 1).
# Calendar formatting only -- the value itself comes from the core.
_WEEKDAY_LABELS = (
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
)

app = FastAPI(
    title="Narayana",
    version=VERSION_FILE.read_text().strip() if VERSION_FILE.is_file() else "0.0.0",
    description="Deterministic Indian Jyotish and astronomy calculation platform.",
)


# --------------------------------------------------------------------------
# Request schemas
# --------------------------------------------------------------------------

class ConfigRequest(BaseModel):
    """Mirrors src.narayana.astronomy.models.CalculationConfig."""

    zodiac: str = CalculationConfig().zodiac
    ayanamsa: str = CalculationConfig().ayanamsa
    node: str = CalculationConfig().node
    house_system: str = CalculationConfig().house_system


class ChartRequest(BaseModel):
    birth_date: _date = Field(..., description="Local date of birth.")
    birth_time: _time = Field(..., description="Local time of birth.")
    timezone: str = Field(..., min_length=1, description="IANA timezone name.")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    place_name: str | None = Field(None, max_length=200)
    config: ConfigRequest = Field(default_factory=ConfigRequest)


# --------------------------------------------------------------------------
# Presentation helpers (formatting only -- no domain logic)
# --------------------------------------------------------------------------

def format_dms(degrees: float) -> str:
    """Render a degree value as ``DD° MM' SS"``."""
    total = round(abs(degrees) * 3600.0)
    d, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{'-' if degrees < 0 else ''}{d}\u00b0 {m:02d}' {s:02d}\""


def _serialise_panchanga(result: AstronomyResult) -> dict[str, Any] | None:
    panchanga = result.panchanga
    if panchanga is None:
        return None

    vara = panchanga.vara
    return {
        "tithi": {
            "number": panchanga.tithi,
            "name": panchanga.tithi_name,
            "paksha": panchanga.tithi_paksha,
        },
        "nakshatra": {
            "number": panchanga.nakshatra,
            "name": get_panchanga_nakshatra_name(panchanga.nakshatra),
            "pada": panchanga.nakshatra_pada,
        },
        "yoga": {"number": panchanga.yoga, "name": get_yoga_name(panchanga.yoga)},
        "karana": {"number": panchanga.karana, "name": get_karana_name(panchanga.karana)},
        "vara": {
            "number": vara,
            "weekday": _WEEKDAY_LABELS[vara - 1] if vara else None,
        },
    }


def _serialise_chart(chart: JyotishBirthChart) -> dict[str, Any]:
    """Convert core domain objects into the JSON contract used by the UI."""
    result = chart.astronomy_result
    metadata = result.calculation_metadata
    analysis = calculate_chart_analysis(chart)

    # Speed comes straight from the ephemeris; keyed by astronomy body name.
    english_to_speed = {
        position.body: position.speed_longitude
        for position in result.positions
    }

    grahas = []
    for placement in chart.placements:
        english = get_graha_name(placement.graha)
        dignity = get_dignity(placement.graha, placement.rashi_number)
        speed = english_to_speed.get(english)
        grahas.append(
            {
                "graha": placement.graha.value,
                "english": english,
                "longitude": placement.longitude,
                "longitude_dms": format_dms(placement.longitude),
                "degrees_in_rashi": placement.longitude % 30.0,
                "degrees_in_rashi_dms": format_dms(placement.longitude % 30.0),
                "rashi_number": placement.rashi_number,
                "rashi_name": placement.rashi_name,
                "rashi_lord": analysis.get_rashi_lord(placement.rashi_number).value,
                "nakshatra_number": placement.nakshatra_number,
                "nakshatra_name": placement.nakshatra_name,
                "nakshatra_pada": placement.nakshatra_pada,
                "bhava_number": placement.bhava_number,
                "dignity": dignity.value,
                "dignity_score": get_dignity_score(
                    placement.graha, placement.rashi_number
                ),
                "speed_longitude": speed,
                "retrograde": None if speed is None else speed < 0.0,
            }
        )

    ascendant_longitude = chart.ascendant_longitude
    bhavas = []
    for index, cusp in enumerate(chart.bhava_cusps):
        number = index + 1
        rashi_number = get_rashi_number(cusp)
        bhavas.append(
            {
                "bhava_number": number,
                "cusp_longitude": cusp,
                "cusp_dms": format_dms(cusp),
                "rashi_number": rashi_number,
                "rashi_name": get_rashi_name(rashi_number),
                "rashi_lord": analysis.get_rashi_lord(rashi_number).value,
                "occupants": [
                    graha.value
                    for graha in analysis.get_bhava_occupancy(number).grahas
                ],
            }
        )

    return {
        "input": {
            "birth_date": result.birth_input.birth_date.isoformat(),
            "birth_time": result.birth_input.birth_time.strftime("%H:%M:%S"),
            "place_name": result.birth_input.place_name,
            "latitude": metadata.latitude,
            "longitude": metadata.longitude,
            "timezone": metadata.timezone_name,
            "local_datetime": metadata.local_datetime.isoformat(),
            "utc_datetime": metadata.utc_datetime.isoformat(),
        },
        "config": {
            "zodiac": result.calculation_config.zodiac,
            "ayanamsa": result.calculation_config.ayanamsa,
            "node": result.calculation_config.node,
            "house_system": result.calculation_config.house_system,
            "ephemeris": result.calculation_config.ephemeris,
        },
        "metadata": {
            "julian_day_ut": metadata.julian_day_ut,
            "ephemeris_implementation": metadata.ephemeris_implementation,
            "ephemeris_version": metadata.ephemeris_version,
            "ayanamsa": metadata.ayanamsa,
            "node_mode": metadata.node_mode,
        },
        "ascendant": {
            "longitude": ascendant_longitude,
            "longitude_dms": format_dms(ascendant_longitude),
            "degrees_in_rashi_dms": format_dms(ascendant_longitude % 30.0),
            "rashi_number": analysis.ascendant_rashi_number,
            "rashi_name": analysis.ascendant_rashi_name,
            "rashi_lord": analysis.ascendant_rashi_lord.value,
        },
        "grahas": grahas,
        "bhavas": bhavas,
        "panchanga": _serialise_panchanga(result),
    }


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------

@app.get("/api/v1/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": app.version,
        "ephemeris_version": SwissEphemerisBackend().version,
    }


# --------------------------------------------------------------------------
# Location resolution
#
# Resolves a free-text place into coordinates and an IANA timezone so the user
# does not have to type them. It only produces *inputs* for BirthInput; it is
# never consulted during calculation.
# --------------------------------------------------------------------------

class LocationServiceError(RuntimeError):
    """The geocoding provider could not be reached or returned nonsense."""


def _geocoding_client() -> httpx.Client:
    """Client factory. Tests replace this to inject a mock transport."""
    return httpx.Client(timeout=GEOCODING_TIMEOUT_SECONDS)


def _build_label(candidate: dict[str, Any]) -> str:
    """Human-readable, auditable location label."""
    parts = [
        candidate.get("name"),
        candidate.get("admin1"),
        candidate.get("country"),
    ]
    seen: list[str] = []
    for part in parts:
        if part and part not in seen:
            seen.append(str(part))
    return ", ".join(seen)


def _normalise_candidate(raw: Any) -> dict[str, Any] | None:
    """Keep only the fields the interface needs; reject unusable entries."""
    if not isinstance(raw, dict):
        return None

    name = raw.get("name")
    latitude = raw.get("latitude")
    longitude = raw.get("longitude")
    timezone = raw.get("timezone")

    if not isinstance(name, str) or not name.strip():
        return None
    if isinstance(latitude, bool) or not isinstance(latitude, (int, float)):
        return None
    if isinstance(longitude, bool) or not isinstance(longitude, (int, float)):
        return None
    if not isinstance(timezone, str) or not timezone.strip():
        return None
    if not (-90.0 <= float(latitude) <= 90.0):
        return None
    if not (-180.0 <= float(longitude) <= 180.0):
        return None

    candidate = {
        "name": name.strip(),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "timezone": timezone.strip(),
        "country": raw.get("country"),
        "country_code": raw.get("country_code"),
        "admin1": raw.get("admin1"),
        "admin2": raw.get("admin2"),
    }
    candidate["label"] = _build_label(candidate)
    return candidate


def search_locations(query: str, count: int = GEOCODING_DEFAULT_COUNT) -> list[dict[str, Any]]:
    """Resolve a place name into normalised location candidates.

    Raises:
        ValueError: the query is empty.
        LocationServiceError: the provider is unreachable, returned an error
            status, or returned a payload that cannot be interpreted.
    """
    text = (query or "").strip()
    if not text:
        raise ValueError("A place name is required.")

    count = max(1, min(int(count), GEOCODING_MAX_COUNT))

    try:
        with _geocoding_client() as client:
            response = client.get(
                GEOCODING_URL,
                params={"name": text, "count": count, "format": "json"},
            )
    except httpx.HTTPError as exc:
        raise LocationServiceError(f"Geocoding request failed: {exc}") from exc

    if response.status_code != 200:
        raise LocationServiceError(
            f"Geocoding provider returned HTTP {response.status_code}."
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise LocationServiceError("Geocoding provider returned invalid JSON.") from exc

    if not isinstance(payload, dict):
        raise LocationServiceError("Unexpected geocoding response structure.")

    # Open-Meteo omits "results" entirely when nothing matches.
    raw_results = payload.get("results", [])
    if raw_results is None:
        raw_results = []
    if not isinstance(raw_results, list):
        raise LocationServiceError("Unexpected geocoding response structure.")

    candidates = [
        normalised
        for normalised in (_normalise_candidate(item) for item in raw_results)
        if normalised is not None
    ]

    # The provider claimed matches but none were usable: treat as malformed
    # rather than silently reporting "no results".
    if raw_results and not candidates:
        raise LocationServiceError("Geocoding response contained no usable location data.")

    return candidates


@app.get("/api/v1/location/search")
def location_search(
    q: str = Query(..., min_length=1, description="Free-text place name."),
    count: int = Query(GEOCODING_DEFAULT_COUNT, ge=1, le=GEOCODING_MAX_COUNT),
) -> dict[str, Any]:
    """Resolve a place name into candidate coordinates and timezone."""
    try:
        results = search_locations(q, count)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LocationServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Location service unavailable. You may enter latitude, "
                "longitude and timezone manually."
            ),
        ) from exc

    return {"query": q.strip(), "results": results}


@app.get("/api/v1/config/options")
def config_options() -> dict[str, Any]:
    """Configuration vocabularies, derived from the core so the UI can never
    offer a setting the calculation engine does not implement."""
    defaults = CalculationConfig()
    ayanamsas = sorted(SwissEphemerisBackend._AYANAMSA_MAP)
    bodies = SwissEphemerisBackend._BODY_MAP
    nodes = [
        {"value": value, "label": f"{label} Node"}
        for value, label in (("mean", "Mean"), ("true", "True"))
        if f"{label} Node" in bodies
    ]
    return {
        "zodiacs": [{"value": z, "label": z.capitalize()} for z in SUPPORTED_ZODIACS],
        "ayanamsas": [{"value": a, "label": a.capitalize()} for a in ayanamsas],
        "nodes": nodes,
        "house_systems": [{"value": defaults.house_system,
                           "label": defaults.house_system.capitalize()}],
        "defaults": {
            "zodiac": defaults.zodiac,
            "ayanamsa": defaults.ayanamsa,
            "node": defaults.node,
            "house_system": defaults.house_system,
        },
        "notes": {
            "house_system": (
                "The current Swiss Ephemeris backend computes Placidus cusps; "
                "no alternative house system is implemented in the core yet."
            ),
            "timezone": "IANA timezone names only (for example Asia/Kolkata).",
        },
    }


@app.post("/api/v1/chart")
def chart(request: ChartRequest) -> dict[str, Any]:
    """Birth details in, real Narayana Jyotish birth chart out."""
    try:
        birth_input = BirthInput(
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            timezone=request.timezone.strip(),
            latitude=request.latitude,
            longitude=request.longitude,
            place_name=(request.place_name or None),
        )
        calculation_config = CalculationConfig(
            zodiac=request.config.zodiac,
            ayanamsa=request.config.ayanamsa,
            node=request.config.node,
            house_system=request.config.house_system,
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        result = calculate_jyotish_birth_chart(birth_input, calculation_config)
    except ZoneInfoNotFoundError as exc:
        raise HTTPException(
            status_code=422, detail=f"Unknown timezone: {request.timezone}"
        ) from exc
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except swe.Error as exc:  # pragma: no cover - ephemeris failure path
        raise HTTPException(status_code=502, detail=f"Ephemeris error: {exc}") from exc

    return _serialise_chart(result)


# --------------------------------------------------------------------------
# Web interface
# --------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


if WEB_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
