# Project Narayana — Decision Log

**Version:** 1.0
**Status:** Active
**Project:** Project Narayana

---

## Purpose

This document records significant architectural and technical decisions made during the development of Project Narayana.

Each decision should be documented with sufficient context to explain:

- What was decided
- Why it was decided
- What alternatives were considered
- What consequences the decision creates
- Which project components are affected

The Decision Log is intended to provide a permanent architectural audit trail.

---

## Decision Status

The following statuses may be used:

- **Proposed** — under discussion
- **Approved** — accepted for implementation
- **Superseded** — replaced by a later decision
- **Rejected** — considered and explicitly rejected

---

# Astronomy Engine Decisions

## D-012 — Configurable Ayanamsa

**Status:** Approved

### Decision

The Astronomy Engine shall support a configurable ayanamsa rather than permanently hard-coding a single ayanamsa system.

The selected ayanamsa must be explicitly recorded as part of the calculation configuration.

### Reasoning

Different Jyotish traditions and calculation systems may use different ayanamsa definitions.

Hard-coding one system would unnecessarily restrict the architecture and make later comparison or configuration difficult.

A configurable approach allows the astronomical calculation layer to remain reusable while allowing the Jyotish layer or application configuration to select the required system.

### Consequence

The Astronomy Engine must expose ayanamsa configuration through its calculation interface.

The default ayanamsa, if one is eventually selected, must be documented as a separate project decision rather than being silently embedded in the implementation.

### Related Specification

`docs/06_AstronomyEngineSpecification.md`
## D-013 — Lunar Node Calculation

**Status:** Approved

### Decision

The Astronomy Engine shall support both Mean Node and True Node calculation modes.

The selected node calculation mode must be explicitly configurable and recorded as part of the calculation configuration.

The ascending lunar node represents Rahu, while the descending lunar node represents Ketu.

Rahu and Ketu shall therefore be represented as derived lunar-node results rather than as independent physical celestial bodies.

### Reasoning

Different Jyotish calculation practices may use Mean or True lunar nodes.

Making the node calculation mode explicit allows Narayana to support both approaches without changing the underlying architecture.

Treating Rahu and Ketu as derived from the lunar node also maintains a clearer astronomical data model.

### Consequence

The Astronomy Engine must expose the lunar-node calculation mode through its calculation interface.

The selected mode must be retained in the calculation metadata so that results remain reproducible.

### Related Specification

`docs/06_AstronomyEngineSpecification.md`
## D-014 — House Calculation Boundary

**Status:** Approved

### Decision

House calculation is outside the scope of Astronomy Engine v1.0.

The Astronomy Engine will provide the astronomical data required by the Jyotish layer, including the time and geographic information necessary for subsequent house calculation.

House-system selection and house calculation will be handled by the appropriate Jyotish layer rather than being implemented as part of the Astronomy Engine v1.0.

### Reasoning

House calculation is part of the horoscope/Jyotish calculation layer rather than the fundamental astronomical position layer.

Keeping this responsibility outside Astronomy Engine maintains a clear separation between:

- Astronomical calculation
- Jyotish calculation
- Interpretation

This also allows future support for different house systems without coupling those choices to the core astronomical engine.

### Consequence

The Astronomy Engine must expose sufficiently precise time and geographic data for the Jyotish layer to perform house calculations.

The Astronomy Engine itself will not determine or interpret houses in v1.0.

### Related Specification

`docs/06_AstronomyEngineSpecification.md`

---