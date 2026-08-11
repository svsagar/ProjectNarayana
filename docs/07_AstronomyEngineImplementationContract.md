# Project Narayana ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Astronomy Engine Implementation Contract

**Version:** 1.0
**Status:** Draft
**Project:** Project Narayana

---

## 1. Purpose

This document translates the Astronomy Engine Specification into an implementation-level contract for the first Python implementation.

It defines the responsibilities, boundaries, inputs, outputs, configuration requirements, and validation obligations of the Astronomy Engine.

The implementation must remain consistent with:

`docs/06_AstronomyEngineSpecification.md`

and the approved architectural decisions:

- D-012 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Configurable Ayanamsa
- D-013 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Lunar Node Calculation
- D-014 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â House Calculation Boundary

---

## 2. Core Responsibility

The Astronomy Engine converts a birth event into reproducible astronomical data.

The core rule is:

> Astronomy calculates. Jyotish interprets.

The engine must remain independent from astrological interpretation.

---

## 3. Implementation Boundary

The implementation shall conceptually follow:

```text
Birth Input
    |
    v
Input Validation
    |
    v
Time / Time-Zone Resolution
    |
    v
UTC / Julian Day
    |
    v
Calculation Configuration
    |
    v
Swiss Ephemeris
    |
    v
Astronomical Results
    |
    v
Canonical Result Model
```

The implementation must preserve the boundary between astronomical calculation and subsequent Jyotish processing.

---

## 4. Input Contract

The initial calculation input shall contain:

- Birth date
- Birth time
- Time zone
- Latitude
- Longitude

The implementation must validate all required input values before astronomical calculation begins.

The input model may retain descriptive location metadata, including:

- Place name
- Coordinate source
- Coordinate precision

Place name is metadata only and must never substitute for geographic coordinates.

The validation case defined by the specification is test data only and must not become an application constant.

---

## 5. Time Handling Contract

The engine shall accept local civil birth time as the primary user-facing time representation.

The implementation shall resolve:

```text
Local Civil Time
    |
    v
Applicable Time-Zone Rules
    |
    v
UTC
    |
    v
Julian Day
    |
    v
Ephemeris Calculation
```

The original local date and time must be retained in the result metadata.

For historical dates, the applicable time-zone rules must be established explicitly for the specified date and geographic location.

The implementation must not silently assume that a current time-zone rule applies to a historical birth date.

The resolved time-zone information must be retained as calculation metadata.

---

## 6. Geographic Location Contract

The Astronomy Engine shall calculate using explicit geographic coordinates:

- Latitude
- Longitude

The implementation must preserve the exact coordinates actually used.

The engine must not silently geocode, substitute, or guess coordinates when required coordinates are unavailable.

Descriptive place names may be retained as metadata but are not calculation inputs unless they have been explicitly resolved into verified coordinates before calculation.

---

## 7. Calculation Configuration Contract

Calculation-relevant configuration shall be explicit and reproducible.

The configuration must be capable of recording, as applicable:

- Ephemeris implementation
- Ephemeris version
- Ayanamsa configuration
- Lunar-node calculation mode
- Time scale
- Coordinate system
- Calculation mode
- Requested celestial bodies
- Other calculation-relevant settings

The implementation must not silently choose a calculation setting that materially changes the result without recording it.

The default ayanamsa remains a separate project decision and must not be permanently hard-coded by the implementation contract.

---

## 8. Ephemeris Boundary Contract

Swiss Ephemeris is the astronomical calculation backend for the first implementation.

The Astronomy Engine shall depend on Swiss Ephemeris through a defined internal boundary rather than allowing Swiss Ephemeris-specific details to spread through the entire application.

The implementation shall:

- Use Swiss Ephemeris for supported astronomical calculations.
- Record the relevant ephemeris implementation and version metadata.
- Avoid unnecessary duplication of astronomical algorithms already provided by the ephemeris backend.
- Keep the astronomical backend replaceable in principle without redesigning the Jyotish layer.

The first implementation must use the project-declared `pyswisseph` dependency.

The Astronomy Engine must not treat Swiss Ephemeris as the source of Jyotish interpretation.

---

## 9. Celestial Body Contract

The Astronomy Engine shall provide a general celestial-body calculation capability.

The initial Jyotish implementation requires support for:

- Sun
- Moon
- Mars
- Mercury
- Jupiter
- Venus
- Saturn
- Lunar Node

The requested body set shall be treated as a request/configuration concern rather than as an architectural limitation.

The implementation should permit additional celestial bodies to be added later without redesigning the core calculation interface.

Each calculated body shall be represented independently in the canonical result.

---

## 10. Sidereal and Ayanamsa Contract

The engine shall support both tropical and sidereal astronomical positions.

Sidereal calculation shall use the configured ayanamsa through the configured ephemeris functionality.

The selected ayanamsa must be:

- Explicit
- Configurable
- Retained in result metadata
- Reproducible

The implementation must not independently reimplement the underlying astronomical sidereal algorithms when equivalent Swiss Ephemeris functionality is available.

No single ayanamsa shall be treated by the core architecture as universally correct for every Jyotish tradition.

The actual default ayanamsa must be established through a separate documented project decision before final implementation.

---

## 11. Lunar Node Contract

The engine shall support:

- Mean Node
- True Node

The selected node calculation mode must be explicit and retained in calculation metadata.

The ascending lunar node represents Rahu.

The descending lunar node represents Ketu.

Rahu and Ketu shall therefore be derived results from the lunar node and shall not be represented internally as independent physical celestial bodies.

The node calculation mode must participate in reproducibility and validation.

---

## 12. Canonical Result Contract

The Astronomy Engine shall expose a canonical astronomical result model.

The result shall contain both:

1. Calculation metadata
2. Astronomical body data

### 12.1 Calculation Metadata

The result must retain, as applicable:

- Input local date/time
- Resolved time zone
- UTC representation
- Geographic coordinates
- Coordinate source
- Julian Day
- Ephemeris implementation
- Ephemeris version
- Ayanamsa configuration
- Node calculation mode
- Time scale
- Calculation mode

### 12.2 Celestial Body Results

Each requested celestial body shall provide the astronomical values required by the subsequent Jyotish layer.

The model shall be capable of representing, as applicable:

- Longitude
- Latitude
- Distance
- Apparent or geometric position
- Motion/speed
- Retrograde status

The exact minimum field set may be finalized during API design, provided that the resulting model remains consistent with the specification.

### 12.3 Canonical Representation

The canonical result must be independent of chart presentation.

International / Western, South Indian, Kerala, North Indian, or other future presentation styles must consume the canonical result rather than modify the underlying astronomical calculation.

No presentation style may require a second astronomical calculation for the same input and configuration.

---

## 13. Validation Contract

Validation shall occur at multiple levels.

### Level 1 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Mathematical Consistency

Internal time conversions, Julian Day conversion, coordinate handling, and calculation transformations shall be verified for consistency.

### Level 2 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Swiss Ephemeris Reference

Results shall be compared against independently generated Swiss Ephemeris results using the same input and calculation configuration.

### Level 3 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Independent Reference

Selected results shall be compared against a trusted independent astronomical or Jyotish calculation source.

### Level 4 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Regression Tests

Once a result has been independently verified, the case shall become a permanent automated regression test.

The implementation must distinguish validation failures from ordinary calculation results.

---

## 14. Error Contract

The engine must explicitly reject or report invalid or unsupported conditions.

The error model shall cover, as applicable:

- Invalid dates
- Invalid times
- Missing time zone
- Invalid latitude
- Invalid longitude
- Unsupported calculation configuration
- Missing ephemeris resources
- Ephemeris/calculation failures

The engine must not silently substitute values when required astronomical input is missing.

Errors should identify the failed stage or input category sufficiently to support diagnosis and audit.

---

## 15. Reproducibility Contract

For identical inputs and identical calculation configuration, the engine must produce the same astronomical result within the defined numerical precision.

A result must retain sufficient metadata to reconstruct the configuration under which it was produced.

At minimum, reproducibility depends on preserving:

- Input local date/time
- Resolved time zone
- UTC
- Coordinates
- Julian Day
- Ephemeris implementation
- Ephemeris version
- Ayanamsa configuration
- Node calculation mode
- Time scale
- Calculation mode

Internal calculations must retain sufficient numerical precision.

Display rounding must never become an input to subsequent calculations.

---

## 16. Implementation Constraints

The first implementation shall remain limited to the Astronomy Engine boundary.

It must not implement:

- Jyotish interpretation
- Dasha calculations
- Horoscope predictions
- Remedies
- AI interpretation
- Chart presentation logic
- Chart-style-specific astronomical calculations
- House interpretation or house-system presentation

House calculation remains outside Astronomy Engine v1.0 in accordance with D-014.

Presentation systems are consumers of the canonical astronomical result and shall be implemented separately.

---

## 17. First Implementation Target

The first implementation milestone shall establish a minimal, testable core capable of:

1. Accepting validated birth input.
2. Resolving the applicable time-zone information.
3. Producing UTC.
4. Producing Julian Day.
5. Applying explicit calculation configuration.
6. Calling Swiss Ephemeris through the internal ephemeris boundary.
7. Calculating the initial supported celestial bodies.
8. Supporting explicit sidereal/ayanamsa configuration.
9. Supporting Mean and True Node modes.
10. Producing the canonical astronomical result.
11. Preserving calculation metadata.
12. Reporting calculation failures explicitly.

The first implementation shall not include chart rendering or astrological interpretation.

---

## 18. Acceptance Tests

The implementation contract is considered satisfied only when the following are demonstrated:

- [ ] Valid birth data is accepted.
- [ ] Invalid birth data is rejected.
- [ ] Local time is correctly converted.
- [ ] Historical time-zone handling is explicit.
- [ ] Julian Day is reproducible.
- [ ] Swiss Ephemeris is invoked through the defined boundary.
- [ ] Planetary positions are reproducible.
- [ ] Sidereal configuration is explicit.
- [ ] Ayanamsa is explicit.
- [ ] Mean Node and True Node modes are supported.
- [ ] Node mode is retained in result metadata.
- [ ] Adequate numerical precision is retained.
- [ ] Calculation metadata is preserved.
- [ ] Results pass independent validation.
- [ ] Verified cases become automated regression tests.
- [ ] No Jyotish interpretation exists inside the Astronomy Engine.
- [ ] No chart presentation style changes the canonical astronomical result.

---

## 19. Contract Status

This implementation contract remains **Draft** until it has been reviewed against:

- `docs/06_AstronomyEngineSpecification.md`
- D-012 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Configurable Ayanamsa
- D-013 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Lunar Node Calculation
- D-014 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â House Calculation Boundary

After technical review, the contract may be marked **Approved** and implementation may begin.
