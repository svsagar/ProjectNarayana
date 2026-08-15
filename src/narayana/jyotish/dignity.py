"""Graha dignity rules for Project Narayana Jyotish."""

from __future__ import annotations

from enum import Enum

from .graha import Graha
from .placement import GrahaPlacement
from .rashi import get_rashi_name


class Dignity(str, Enum):
    """Classical sign-based Graha dignity."""

    EXALTED = "Exalted"
    DEBILITATED = "Debilitated"
    OWN_SIGN = "Own Sign"
    FRIENDLY = "Friendly"
    NEUTRAL = "Neutral"
    INIMICAL = "Inimical"


# Classical exaltation signs.
EXALTATION_RASHIS: dict[Graha, int] = {
    Graha.SURYA: 1,       # Mesha
    Graha.CHANDRA: 2,     # Vrishabha
    Graha.MANGALA: 10,    # Makara
    Graha.BUDHA: 6,       # Kanya
    Graha.GURU: 4,        # Karka
    Graha.SHUKRA: 12,     # Meena
    Graha.SHANI: 7,       # Tula
}


# Classical debilitation signs.
DEBILITATION_RASHIS: dict[Graha, int] = {
    Graha.SURYA: 7,       # Tula
    Graha.CHANDRA: 8,     # Vrishchika
    Graha.MANGALA: 4,     # Karka
    Graha.BUDHA: 12,      # Meena
    Graha.GURU: 10,       # Makara
    Graha.SHUKRA: 6,      # Kanya
    Graha.SHANI: 1,       # Mesha
}


# Classical own signs.
OWN_RASHIS: dict[Graha, tuple[int, ...]] = {
    Graha.SURYA: (5,),
    Graha.CHANDRA: (4,),
    Graha.MANGALA: (1, 8),
    Graha.BUDHA: (3, 6),
    Graha.GURU: (9, 12),
    Graha.SHUKRA: (2, 7),
    Graha.SHANI: (10, 11),
}


# Natural friendship relationships.
NATURAL_FRIENDS: dict[Graha, frozenset[Graha]] = {
    Graha.SURYA: frozenset({
        Graha.CHANDRA,
        Graha.MANGALA,
        Graha.GURU,
    }),
    Graha.CHANDRA: frozenset({
        Graha.SURYA,
        Graha.BUDHA,
    }),
    Graha.MANGALA: frozenset({
        Graha.SURYA,
        Graha.CHANDRA,
        Graha.GURU,
    }),
    Graha.BUDHA: frozenset({
        Graha.SURYA,
        Graha.SHUKRA,
    }),
    Graha.GURU: frozenset({
        Graha.SURYA,
        Graha.CHANDRA,
        Graha.MANGALA,
    }),
    Graha.SHUKRA: frozenset({
        Graha.BUDHA,
        Graha.SHANI,
    }),
    Graha.SHANI: frozenset({
        Graha.BUDHA,
        Graha.SHUKRA,
    }),
}


NATURAL_ENEMIES: dict[Graha, frozenset[Graha]] = {
    Graha.SURYA: frozenset({
        Graha.SHUKRA,
        Graha.SHANI,
    }),
    Graha.CHANDRA: frozenset(),
    Graha.MANGALA: frozenset({
        Graha.BUDHA,
    }),
    Graha.BUDHA: frozenset({
        Graha.CHANDRA,
    }),
    Graha.GURU: frozenset({
        Graha.BUDHA,
        Graha.SHUKRA,
    }),
    Graha.SHUKRA: frozenset({
        Graha.SURYA,
        Graha.CHANDRA,
    }),
    Graha.SHANI: frozenset({
        Graha.SURYA,
        Graha.CHANDRA,
        Graha.MANGALA,
    }),
}


# Traditional sign lords.
RASHI_LORDS: dict[int, Graha] = {
    1: Graha.MANGALA,
    2: Graha.SHUKRA,
    3: Graha.BUDHA,
    4: Graha.CHANDRA,
    5: Graha.SURYA,
    6: Graha.BUDHA,
    7: Graha.SHUKRA,
    8: Graha.MANGALA,
    9: Graha.GURU,
    10: Graha.SHANI,
    11: Graha.SHANI,
    12: Graha.GURU,
}


def get_dignity(
    graha: Graha,
    rashi_number: int,
) -> Dignity:
    """Return the classical sign dignity of a Graha."""

    if not isinstance(graha, Graha):
        raise TypeError("graha must be a Graha")

    if (
        not isinstance(rashi_number, int)
        or isinstance(rashi_number, bool)
        or not 1 <= rashi_number <= 12
    ):
        raise ValueError(
            "rashi_number must be an integer between 1 and 12"
        )

    # Rahu and Ketu do not have a universally accepted classical
    # exaltation/debilitation/own-sign scheme, so use neutral dignity.
    if graha in {Graha.RAHU, Graha.KETU}:
        return Dignity.NEUTRAL

    if EXALTATION_RASHIS.get(graha) == rashi_number:
        return Dignity.EXALTED

    if DEBILITATION_RASHIS.get(graha) == rashi_number:
        return Dignity.DEBILITATED

    if rashi_number in OWN_RASHIS.get(graha, ()):
        return Dignity.OWN_SIGN

    sign_lord = RASHI_LORDS[rashi_number]

    if sign_lord in NATURAL_FRIENDS[graha]:
        return Dignity.FRIENDLY

    if sign_lord in NATURAL_ENEMIES[graha]:
        return Dignity.INIMICAL

    return Dignity.NEUTRAL


def get_graha_dignity(
    placement: GrahaPlacement,
) -> Dignity:
    """Return the dignity of a Graha placement."""

    if not isinstance(placement, GrahaPlacement):
        raise TypeError(
            "placement must be a GrahaPlacement"
        )

    return get_dignity(
        placement.graha,
        placement.rashi_number,
    )


def get_exaltation_rashi(graha: Graha) -> str | None:
    """Return the exaltation Rashi name for a classical Graha."""

    if not isinstance(graha, Graha):
        raise TypeError("graha must be a Graha")

    rashi_number = EXALTATION_RASHIS.get(graha)

    if rashi_number is None:
        return None

    return get_rashi_name(rashi_number)


def get_debilitation_rashi(graha: Graha) -> str | None:
    """Return the debilitation Rashi name for a classical Graha."""

    if not isinstance(graha, Graha):
        raise TypeError("graha must be a Graha")

    rashi_number = DEBILITATION_RASHIS.get(graha)

    if rashi_number is None:
        return None

    return get_rashi_name(rashi_number)


def get_own_rashis(graha: Graha) -> tuple[str, ...]:
    """Return the own-sign names for a Graha."""

    if not isinstance(graha, Graha):
        raise TypeError("graha must be a Graha")

    return tuple(
        get_rashi_name(number)
        for number in OWN_RASHIS.get(graha, ())
    )