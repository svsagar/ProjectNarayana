"""Canonical Graha definitions for Project Narayana Jyotish."""

from __future__ import annotations

from enum import Enum


class Graha(str, Enum):
    """The nine traditional Jyotish Grahas."""

    SURYA = "Surya"
    CHANDRA = "Chandra"
    MANGALA = "Mangala"
    BUDHA = "Budha"
    GURU = "Guru"
    SHUKRA = "Shukra"
    SHANI = "Shani"
    RAHU = "Rahu"
    KETU = "Ketu"


GRAHAS: tuple[Graha, ...] = (
    Graha.SURYA,
    Graha.CHANDRA,
    Graha.MANGALA,
    Graha.BUDHA,
    Graha.GURU,
    Graha.SHUKRA,
    Graha.SHANI,
    Graha.RAHU,
    Graha.KETU,
)


PLANETARY_GRAHAS: tuple[Graha, ...] = (
    Graha.SURYA,
    Graha.CHANDRA,
    Graha.MANGALA,
    Graha.BUDHA,
    Graha.GURU,
    Graha.SHUKRA,
    Graha.SHANI,
)


NODE_GRAHAS: tuple[Graha, ...] = (
    Graha.RAHU,
    Graha.KETU,
)


_ENGLISH_NAMES: dict[Graha, str] = {
    Graha.SURYA: "Sun",
    Graha.CHANDRA: "Moon",
    Graha.MANGALA: "Mars",
    Graha.BUDHA: "Mercury",
    Graha.GURU: "Jupiter",
    Graha.SHUKRA: "Venus",
    Graha.SHANI: "Saturn",
    Graha.RAHU: "Rahu",
    Graha.KETU: "Ketu",
}


def get_grahas() -> tuple[Graha, ...]:
    """Return the nine Grahas in canonical order."""
    return GRAHAS


def get_graha_name(graha: Graha) -> str:
    """Return the English astronomical name for a Graha."""
    if not isinstance(graha, Graha):
        raise TypeError("graha must be a Graha")

    return _ENGLISH_NAMES[graha]


def is_planetary_graha(graha: Graha) -> bool:
    """Return True when the Graha is one of the seven classical planets."""
    if not isinstance(graha, Graha):
        raise TypeError("graha must be a Graha")

    return graha in PLANETARY_GRAHAS


def is_node_graha(graha: Graha) -> bool:
    """Return True when the Graha is Rahu or Ketu."""
    if not isinstance(graha, Graha):
        raise TypeError("graha must be a Graha")

    return graha in NODE_GRAHAS