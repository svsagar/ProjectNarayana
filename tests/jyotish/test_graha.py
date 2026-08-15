"""Tests for the canonical Jyotish Graha definitions."""

import pytest

from src.narayana.jyotish.graha import (
    Graha,
    GRAHAS,
    NODE_GRAHAS,
    PLANETARY_GRAHAS,
    get_graha_name,
    get_grahas,
    is_node_graha,
    is_planetary_graha,
)


def test_all_nine_grahas_are_defined():
    assert len(GRAHAS) == 9
    assert len(set(GRAHAS)) == 9


def test_grahas_are_in_canonical_order():
    assert get_grahas() == (
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


@pytest.mark.parametrize(
    "graha,expected",
    [
        (Graha.SURYA, "Sun"),
        (Graha.CHANDRA, "Moon"),
        (Graha.MANGALA, "Mars"),
        (Graha.BUDHA, "Mercury"),
        (Graha.GURU, "Jupiter"),
        (Graha.SHUKRA, "Venus"),
        (Graha.SHANI, "Saturn"),
        (Graha.RAHU, "Rahu"),
        (Graha.KETU, "Ketu"),
    ],
)
def test_graha_english_name(graha, expected):
    assert get_graha_name(graha) == expected


def test_seven_planetary_grahas():
    assert PLANETARY_GRAHAS == (
        Graha.SURYA,
        Graha.CHANDRA,
        Graha.MANGALA,
        Graha.BUDHA,
        Graha.GURU,
        Graha.SHUKRA,
        Graha.SHANI,
    )


def test_two_node_grahas():
    assert NODE_GRAHAS == (
        Graha.RAHU,
        Graha.KETU,
    )


@pytest.mark.parametrize(
    "graha",
    [
        Graha.SURYA,
        Graha.CHANDRA,
        Graha.MANGALA,
        Graha.BUDHA,
        Graha.GURU,
        Graha.SHUKRA,
        Graha.SHANI,
    ],
)
def test_planetary_graha_classification(graha):
    assert is_planetary_graha(graha) is True
    assert is_node_graha(graha) is False


@pytest.mark.parametrize(
    "graha",
    [
        Graha.RAHU,
        Graha.KETU,
    ],
)
def test_node_graha_classification(graha):
    assert is_node_graha(graha) is True
    assert is_planetary_graha(graha) is False


@pytest.mark.parametrize(
    "invalid",
    [
        "Sun",
        "Rahu",
        1,
        None,
        True,
    ],
)
def test_graha_name_rejects_invalid_value(invalid):
    with pytest.raises(TypeError):
        get_graha_name(invalid)


@pytest.mark.parametrize(
    "invalid",
    [
        "Sun",
        1,
        None,
        True,
    ],
)
def test_planetary_classification_rejects_invalid_value(invalid):
    with pytest.raises(TypeError):
        is_planetary_graha(invalid)


@pytest.mark.parametrize(
    "invalid",
    [
        "Rahu",
        1,
        None,
        True,
    ],
)
def test_node_classification_rejects_invalid_value(invalid):
    with pytest.raises(TypeError):
        is_node_graha(invalid)