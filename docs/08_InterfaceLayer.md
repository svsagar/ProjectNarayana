# Project Narayana — Interface Layer Contract

**Version:** 1.0
**Status:** Draft
**Project:** Project Narayana

---

## 1. Purpose

This document defines the HTTP interface layer that exposes the existing
Narayana calculation core to a user interface.

It adds a presentation boundary above the application API. It does not extend,
alter, or duplicate the Astronomy Engine or the Jyotish layer.

---

## 2. Core Rule

> Astronomy calculates. Jyotish interprets. The interface only presents.

The interface layer performs no astronomical or Jyotish calculation. It calls:

`src.narayana.jyotish.api.calculate_jyotish_birth_chart()`

and serialises the returned `JyotishBirthChart` and its embedded
`AstronomyResult`.

---

## 3. Layering

```
Browser (src/narayana/interface/web)
    ↓ HTTP / JSON
Interface layer (src/narayana/interface/http.py)
    ↓ calculate_jyotish_birth_chart()
Narayana Jyotish (src/narayana/jyotish)
    ↓ calculate()
Narayana Astronomy (src/narayana/astronomy)
    ↓
Swiss Ephemeris
```

No layer may be bypassed. The browser never imports, replicates, or
approximates domain logic.

---

## 4. Endpoints

| Method | Path                       | Responsibility                                      |
|--------|----------------------------|-----------------------------------------------------|
| GET    | `/api/v1/health`           | Core version and Swiss Ephemeris version             |
| GET    | `/api/v1/config/options`   | Supported configuration vocabularies and defaults    |
| GET    | `/api/v1/location/search`  | Resolve a place name into coordinates and timezone   |
| POST   | `/api/v1/chart`            | Birth details → serialised `JyotishBirthChart`       |
| GET    | `/`                        | Web interface                                        |

### 4.1 Configuration options

`/api/v1/config/options` derives its vocabularies from the core rather than
restating them:

- Ayanamsas are read from `SwissEphemerisBackend._AYANAMSA_MAP`.
- Node modes are read from `SwissEphemerisBackend._BODY_MAP`.
- Defaults are read from `CalculationConfig()`.

This guarantees the interface can never offer a setting the engine does not
implement. When the core gains an ayanamsa, the UI gains it automatically.

### 4.2 House system

`CalculationConfig.house_system` defaults to `placidus`, and the current
Swiss Ephemeris backend computes Placidus cusps unconditionally
(`swe.houses_ex(..., b"P", ...)`). The interface therefore presents a single
house-system option and states this limitation to the user. It must not offer
alternatives until the Astronomy Engine implements them (see D-014).

---

## 5. Location Resolution

`GET /api/v1/location/search?q=<place>&count=<1..10>` resolves free-text place
input into coordinates and an IANA timezone, so the user is not required to
type latitude and longitude by hand.

The provider is the Open-Meteo Geocoding API
(`https://geocoding-api.open-meteo.com/v1/search`). It is called **server
side**; the browser never contacts it directly.

### 5.1 Boundary

Location resolution produces *inputs* for `BirthInput`. It participates in no
astronomical or Jyotish calculation, and `POST /api/v1/chart` never invokes it.
The calculation always uses the values present in the submitted request.

### 5.2 Normalisation

Each provider entry is reduced to `name`, `latitude`, `longitude`, `timezone`,
`country`, `country_code`, `admin1`, `admin2` and a composed `label`.

An entry is discarded unless it carries a non-empty name, a numeric latitude in
[-90, 90], a numeric longitude in [-180, 180], and a non-empty timezone.
Coordinates are never inferred, defaulted, or rounded.

### 5.3 Ambiguity

A single usable candidate may populate the form directly. Two or more
candidates must be presented for explicit user selection; the interface must
not choose on the user's behalf. Candidates are shown with their coordinates
and timezone so that visually identical place names remain distinguishable.

### 5.4 Auditability and override

The resolved location is displayed, not merely written into fields. Latitude,
longitude and timezone remain editable; a deliberate manual edit after
resolution is retained and never silently overwritten. Only an explicit
re-resolution replaces the values.

### 5.5 Error contract

| Condition                                     | Status | Behaviour                                   |
|-----------------------------------------------|--------|---------------------------------------------|
| Blank query                                    | 422    | Rejected before any provider call            |
| No match                                       | 200    | `{"results": []}` — an empty result, not an error |
| Network failure, timeout, non-200 upstream     | 503    | Advises manual entry of coordinates          |
| Invalid JSON or unusable payload structure     | 503    | Advises manual entry of coordinates          |

When the provider reports matches but none survive validation, the response is
a 503 rather than a misleading "no results".

Tests mock the provider with `httpx.MockTransport` and never depend on live
Open-Meteo availability.

---

## 6. Error Contract

| Condition                                   | Status | Source                          |
|---------------------------------------------|--------|---------------------------------|
| Malformed or out-of-range request field      | 422    | Pydantic / `validate_birth_input` |
| Unknown IANA timezone                        | 422    | `ZoneInfoNotFoundError`         |
| Unsupported ayanamsa, zodiac, or node mode   | 422    | `ValueError` from the core      |
| Swiss Ephemeris failure                      | 502    | `swisseph.Error`                |

Domain validation is never reimplemented in the interface layer; core
exceptions are translated into HTTP status codes.

---

## 7. Serialisation Notes

The interface adds presentation-only fields alongside core values:

- `*_dms` — degree/minute/second rendering of a longitude.
- `degrees_in_rashi` — the longitude modulo 30, for display.
- `retrograde` — the sign of `CelestialPosition.speed_longitude`.
- `vara.weekday` — a calendar label for the core's `vara` integer.

Every domain value (`longitude`, `rashi_number`, `rashi_name`,
`nakshatra_number`, `nakshatra_name`, `nakshatra_pada`, `bhava_number`,
`dignity`, `dignity_score`, panchanga limbs, cusps, ascendant) is passed
through unchanged. This is enforced by `tests/interface/test_http.py`, which
compares the HTTP response against a direct call to the application API.

---

## 8. Out of Scope

Dashas, yogas, predictions, compatibility, reports, transits, chart graphics,
and persistence remain out of scope for this layer.

---

## 9. Running

```bash
pip install -r requirements.txt
uvicorn src.narayana.interface.http:app --host 0.0.0.0 --port 8000
```
