# Project Narayana â€” Astronomy Engine Implementation Contract



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



- D-012 â€” Configurable Ayanamsa

- D-013 â€” Lunar Node Calculation

- D-014 â€” House Calculation Boundary



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

&#x20;   |

&#x20;   v

Input Validation

&#x20;   |

&#x20;   v

Time / Time-Zone Resolution

&#x20;   |

&#x20;   v

UTC / Julian Day

&#x20;   |

&#x20;   v

Calculation Configuration

&#x20;   |

&#x20;   v

Swiss Ephemeris

&#x20;   |

&#x20;   v

Astronomical Results

&#x20;   |

&#x20;   v

Canonical Result Model
