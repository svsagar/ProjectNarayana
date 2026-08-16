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

| Method | Path                     | Responsibility                                        |
|--------|--------------------------|-------------------------------------------------------|
| GET    | `/api/v1/health`         | Core version and Swiss Ephemeris version               |
| GET    | `/api/v1/config/options` | Supported configuration vocabularies and defaults      |
| POST   | `/api/v1/chart`          | Birth details → serialised `JyotishBirthChart`         |
| GET    | `/`                      | Web interface                                          |

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

## 5. Error Contract

| Condition                                   | Status | Source                          |
|---------------------------------------------|--------|---------------------------------|
| Malformed or out-of-range request field      | 422    | Pydantic / `validate_birth_input` |
| Unknown IANA timezone                        | 422    | `ZoneInfoNotFoundError`         |
| Unsupported ayanamsa, zodiac, or node mode   | 422    | `ValueError` from the core      |
| Swiss Ephemeris failure                      | 502    | `swisseph.Error`                |

Domain validation is never reimplemented in the interface layer; core
exceptions are translated into HTTP status codes.

---

## 6. Serialisation Notes

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

## 7. Out of Scope

Dashas, yogas, predictions, compatibility, reports, transits, chart graphics,
geocoding, and persistence remain out of scope for this layer.

---

## 8. Running

```bash
pip install -r requirements.txt
uvicorn src.narayana.interface.http:app --host 0.0.0.0 --port 8000
```
