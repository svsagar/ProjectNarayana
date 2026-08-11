# Astronomy Engine Specification v1.0

**Status:** Review Draft
**Version:** 1.0
**Project:** Project Narayana

---

## 1. Purpose

The Astronomy Engine provides the astronomical data required by the Jyotish layer from a user's birth date, exact local time, and geographic location.

Its primary responsibility is to convert a birth event into reproducible astronomical positions using a defined astronomical calculation method.

The engine must produce results that can be independently validated and reproduced.

---

## 2. Scope

### 2.1 In Scope

Version 1.0 will handle:

- Birth date
- Birth time
- Geographic location
- Time-zone conversion
- Julian Day
- Planetary positions
- Solar and lunar positions
- Sidereal conversion
- Ayanamsa configuration
- Required astronomical metadata
- Validation and error reporting

### 2.2 Out of Scope

The Astronomy Engine will not perform:

- Nakshatra interpretation
- Pada interpretation
- Rashi interpretation
- Vimshottari Dasha
- Yogas
- Bhava interpretation
- Predictions
- Remedies
- AI-generated interpretations

These belong to subsequent layers.

---

## 3. Architectural Position

The Astronomy Engine sits between the input/time-processing layer and the Jyotish Engine.

Swiss Ephemeris is an implementation dependency of the Astronomy Engine and is not treated as an independent architectural layer.

Conceptually:

User Birth Data
       |
       v
Input / Time Processing
       |
       v
Astronomy Engine
       |
       +---- Swiss Ephemeris
       |
       v
Astronomical Data
       |
       v
Jyotish Engine
       |
       v
Knowledge / Interpretation

### Core Architectural Rule

> Astronomy calculates. Jyotish interprets.

---

## 4. Design Principles

### 4.1 Reproducibility

The same inputs and configuration must produce the same result.

### 4.2 Traceability

Every astronomical result should be traceable to:

```text
Input
  |
  v
Time Conversion
  |
  v
Calculation Configuration
  |
  v
Ephemeris
  |
  v
Result

**After the final `Result` line, add the closing three backticks yourself:**

```text

Then immediately type:

```markdown
### 4.3 Configuration Over Hard-Coding

The engine must not hard-code:

- User birth details
- A particular birthplace
- A particular ayanamsa
- A particular house system

These are input or configuration values.

### 4.4 Separation of Concerns

Astronomical calculations must remain independent from astrological interpretation.

### 4.5 Deterministic Configuration

A calculation result must record the configuration that produced it.

Relevant configuration may include:

- Ephemeris implementation
- Ephemeris version
- Ayanamsa configuration
- Lunar-node calculation mode
- Time scale
- Coordinate system
- Other calculation-relevant settings

The purpose is to ensure that an astronomical result can be reproduced and audited.
---


## 5. Input Model

The initial conceptual input consists of:

- Birth Date
- Birth Time
- Time Zone
- Latitude
- Longitude

The first validation case will use:

Date: 17 August 1978
Time: 10:10 AM
Place: Kottayam, Kerala, India

This is a validation test case and must not become an application constant.

### 5.1 Location Metadata

The location model should distinguish between:

- Place name
- Latitude
- Longitude
- Coordinate source
- Coordinate precision

The place name is descriptive metadata and must not itself be treated as an astronomical coordinate.

The engine must preserve the coordinates actually used for a calculation.

---

## 6. Time Handling

The user supplies local civil time.

The Astronomy Engine must establish the corresponding astronomical time representation before requesting positions from Swiss Ephemeris.

Conceptually:

Local Birth Time → Time Zone → UTC → Julian Day → Ephemeris Calculation

The original local time must also be retained as metadata so that the calculation can be audited.

### 6.1 Historical Time-Zone Handling

For historical birth data, the applicable time-zone rules must be established explicitly for the specified date and geographic location.

The engine must not assume that a modern time-zone rule automatically applies to historical dates.

The resolved time-zone information must be retained as calculation metadata.

---

## 7. Geographic Location

The engine will accept geographic coordinates:

- Latitude
- Longitude

Location must be represented independently from the person's name for calculation purposes.

The exact coordinates used for a calculation must be verified and recorded.

The engine must not silently guess coordinates.

---

## 8. Julian Day

The engine will calculate or obtain the appropriate Julian Day representation required by Swiss Ephemeris.

The implementation must document:

- Input time scale
- Conversion procedure
- Julian Day value
- Relevant precision

Julian Day is a key audit value for every calculation.
---

## 9. Swiss Ephemeris

Swiss Ephemeris will serve as the astronomical calculation library for the first implementation.

Swiss Ephemeris is an implementation dependency of the Astronomy Engine and does not define Jyotish interpretation.

The Astronomy Engine should be designed so that the astronomical backend can theoretically be replaced without requiring a redesign of the entire Jyotish layer.

The calculation metadata should record the relevant Swiss Ephemeris implementation/version information required for reproducibility.

The engine should not duplicate astronomical algorithms unnecessarily when the corresponding functionality is already provided by the configured ephemeris backend.

---

## 10. Sidereal Calculation

The engine must support the distinction between tropical and sidereal longitude.

Conceptually:

Tropical Astronomical Position
       |
       v
Configured Sidereal Calculation
       |
       v
Sidereal Position

The selected ayanamsa must be an explicit configuration value.

The actual sidereal calculation should use the configured Swiss Ephemeris functionality rather than independently reimplementing astronomical algorithms.

The default ayanamsa is not hard-coded by this specification and must be established as a documented project decision before final implementation.

---

## 11. Ayanamsa Policy

Project Narayana will support multiple ayanamsa configurations.

The selected ayanamsa must be explicit and reproducible.

The architecture must not assume that a single ayanamsa is universally correct for every Jyotish tradition.

The initial supported/default configuration will be established separately and documented before implementation.

**Related decision:** D-012.

---

## 12. Lunar Nodes

The engine will support both:

- Mean Node
- True Node

The selected node calculation method must be configurable and reproducible.

The ascending lunar node represents Rahu and the descending lunar node represents Ketu.

Conceptually:

Lunar Node
    |
    +---- Ascending Node → Rahu
    |
    +---- Descending Node → Ketu

Rahu and Ketu must therefore not be treated internally as independent physical celestial bodies.
---

## 13. Celestial Body Support

The Astronomy Engine should provide a general celestial-body calculation capability rather than hard-coding its internal architecture around a fixed list of Jyotish bodies.

The initial Jyotish implementation will require:

- Sun
- Moon
- Mars
- Mercury
- Jupiter
- Venus
- Saturn
- Lunar Node

Rahu and Ketu are derived from the corresponding lunar nodes according to the configured node calculation mode.

The architecture should permit additional celestial bodies to be supported later without requiring a fundamental redesign of the Astronomy Engine API.

The set of celestial bodies requested by the Jyotish layer should therefore be treated as a configuration or request-level concern rather than an architectural limitation.
---

## 14. House Calculation

House calculation is explicitly outside the scope of Astronomy Engine v1.0.

House systems and their astrological application will be handled by the appropriate Jyotish layer.

**Related decision:** D-014.
---

## 15. Precision

The engine must retain sufficient numerical precision internally and avoid unnecessary rounding during calculations.

Calculation precision and display precision are separate concerns.

Rounded display values must never be used as inputs for subsequent calculations.

---

## 16. Output Model

The Astronomy Engine will expose a canonical astronomical result model.

The result must contain both calculation metadata and astronomical body data.

### 16.1 Calculation Metadata

The result should include, as applicable:

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

### 16.2 Celestial Body Results

Each requested celestial body should provide the astronomical values required by the subsequent Jyotish layer.

The initial data contract should be capable of representing values such as:

- Longitude
- Latitude
- Distance
- Apparent or geometric position as applicable
- Motion/speed as applicable
- Retrograde status where applicable

The exact minimum required fields will be finalized during API design and implementation.

### 16.3 Canonical Data

The Astronomy Engine must produce a canonical astronomical representation independent of chart presentation.

Chart styles such as International / Western, South Indian, or Kerala Style must not alter the underlying astronomical result.

This allows the same calculation to be rendered through multiple presentation systems without recalculating the astronomical data.
---

## 17. Error Handling

The engine must explicitly reject or report invalid inputs, including:

- Invalid dates
- Invalid times
- Missing time zone
- Invalid latitude
- Invalid longitude
- Unsupported calculation configuration
- Missing ephemeris resources
- Calculation failures

The engine must not silently substitute a value when a required astronomical input is missing.

---

## 18. Validation Strategy

Validation will occur at multiple levels.

### Level 1 — Mathematical Consistency

Verify internal conversions and calculations.

### Level 2 — Swiss Ephemeris Reference

Compare results against independently generated Swiss Ephemeris results using the same configuration.

### Level 3 — Independent Reference

Compare selected results against a trusted independent astronomical/Jyotish calculation source.

### Level 4 — Regression Tests

Once a result is verified, it becomes a permanent automated test case.

---

## 19. First Validation Case

The first complete validation case will be:

Date: 17 August 1978
Time: 10:10 AM
Place: Kottayam, Kerala, India

Before calculation, the following must be independently established:

- Exact geographic coordinates
- Historical time-zone assumption
- Local-to-UTC conversion
- Ayanamsa configuration
- Ephemeris configuration
- Node calculation mode

No value should be guessed.
---

## 20. Acceptance Criteria

Astronomy Engine v1.0 will not be considered complete until:

- [ ] Valid birth data is accepted
- [ ] Invalid data is rejected
- [ ] Local time is correctly converted
- [ ] Julian Day is reproducible
- [ ] Planetary positions are reproducible
- [ ] Sidereal configuration is explicit
- [ ] Ayanamsa is explicit
- [ ] Node calculation mode is explicit
- [ ] Results retain adequate precision
- [ ] Calculation metadata is preserved
- [ ] Results pass independent validation
- [ ] Automated regression tests exist
- [ ] No Jyotish interpretation exists inside the Astronomy Engine

---

## 21. Explicit Exclusions

The following must not be implemented as part of the Astronomy Engine:

- Jyotish interpretation
- Dasha calculations
- Horoscope predictions
- Remedies
- AI interpretation

These belong to higher-level Jyotish and knowledge/interpretation layers.

---

## 22. Future Extensions

Potential future capabilities include:

- House calculations through the Jyotish layer
- Topocentric calculations
- Additional celestial bodies
- Multiple ephemeris backends
- Additional ayanamsa systems
- Historical calendar handling
- High-precision event calculations
- Astronomical event detection

These are future extensions and are not v1.0 requirements.

---

## 23. Approval Status

The architectural decisions concerning:

- Configurable ayanamsa — D-012
- Mean/True lunar-node support — D-013
- Houses outside Astronomy Engine v1.0 — D-014

have been approved.

The Astronomy Engine Specification remains a Review Draft until the revised specification has been technically reviewed and validated.

Implementation remains subject to the project's validation requirements.