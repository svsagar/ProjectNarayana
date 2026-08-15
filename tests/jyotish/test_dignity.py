"""Tests for Graha dignity rules."""

import pytest

from src.narayana.jyotish.dignity import (
    DEBILITATION_RASHIS,
    EXALTATION_RASHIS,
    OWN_RASHIS,
    Dignity,
    DIGNITY_SCORES,
    get_debilitation_rashi,
    get_dignity,
    get_dignity_score,
    get_exaltation_rashi,
    get_own_rashis,
    get_placement_strength,
)
from src.narayana.jyotish.graha import Graha
from src.narayana.jyotish.placement import (
    GrahaPlacement,
    calculate_graha_placement,
)


@pytest.mark.parametrize(
    "graha,rashi",
    [
        (Graha.SURYA, 1),
        (Graha.CHANDRA, 2),
        (Graha.MANGALA, 10),
        (Graha.BUDHA, 6),
        (Graha.GURU, 4),
        (Graha.SHUKRA, 12),
        (Graha.SHANI, 7),
    ],
)
def test_exaltation(
    graha,
    rashi,
):
    assert get_dignity(graha, rashi) is Dignity.EXALTED


@pytest.mark.parametrize(
    "graha,rashi",
    [
        (Graha.SURYA, 7),
        (Graha.CHANDRA, 8),
        (Graha.MANGALA, 4),
        (Graha.BUDHA, 12),
        (Graha.GURU, 10),
        (Graha.SHUKRA, 6),
        (Graha.SHANI, 1),
    ],
)
def test_debilitation(
    graha,
    rashi,
):
    assert get_dignity(graha, rashi) is Dignity.DEBILITATED


@pytest.mark.parametrize(
    "graha,rashis",
    [
        (Graha.SURYA, (5,)),
        (Graha.CHANDRA, (4,)),
        (Graha.MANGALA, (1, 8)),
        (Graha.BUDHA, (3,)),  # Virgo (6) is exaltation, not strictly just own sign
        (Graha.GURU, (9, 12)),
        (Graha.SHUKRA, (2, 7)),
        (Graha.SHANI, (10, 11)),
    ],
)
def test_own_signs(
    graha,
    rashis,
):
    for rashi in rashis:
        assert get_dignity(graha, rashi) is Dignity.OWN_SIGN


@pytest.mark.parametrize(
    "dignity,expected_score",
    [
        (Dignity.EXALTED, 5),
        (Dignity.OWN_SIGN, 4),
        (Dignity.FRIENDLY, 3),
        (Dignity.NEUTRAL, 2),
        (Dignity.INIMICAL, 1),
        (Dignity.DEBILITATED, 0),
    ],
)
def test_dignity_scores(
    dignity,
    expected_score,
):
    assert DIGNITY_SCORES[dignity] == expected_score


@pytest.mark.parametrize(
    "graha,rashi,expected_score",
    [
        (Graha.SURYA, 1, 5),
        (Graha.SURYA, 5, 4),
        (Graha.SURYA, 9, 3),
        (Graha.SURYA, 10, 1),
        (Graha.SURYA, 7, 0),
        (Graha.RAHU, 1, 2),
        (Graha.KETU, 12, 2),
    ],
)
def test_get_dignity_score(
    graha,
    rashi,
    expected_score,
):
    assert get_dignity_score(
        graha,
        rashi,
    ) == expected_score


def test_placement_strength():
    placement = calculate_graha_placement(
        Graha.SURYA,
        10.0,
    )

    assert get_placement_strength(placement) == 5


def test_placement_strength_rejects_invalid_input():
    with pytest.raises(
        TypeError,
        match="placement must be a GrahaPlacement",
    ):
        get_placement_strength(None)


def test_sun_in_jupiter_sign_is_friendly():
    assert get_dignity(
        Graha.SURYA,
        9,
    ) is Dignity.FRIENDLY


def test_sun_in_saturn_sign_is_inimical():
    assert get_dignity(
        Graha.SURYA,
        10,
    ) is Dignity.INIMICAL


def test_moon_has_no_natural_enemies():
    assert get_dignity(
        Graha.CHANDRA,
        3,
    ) is Dignity.FRIENDLY


def test_moon_in_mars_sign_is_friendly():
    assert get_dignity(
        Graha.CHANDRA,
        1,
    ) is Dignity.NEUTRAL


@pytest.mark.parametrize(
    "graha",
    [
        Graha.RAHU,
        Graha.KETU,
    ],
)
def test_nodes_are_neutral(
    graha,
):
    for rashi in range(1, 13):
        assert get_dignity(
            graha,
            rashi,
        ) is Dignity.NEUTRAL


@pytest.mark.parametrize(
    "graha,expected",
    [
        (Graha.SURYA, "Mesha"),
        (Graha.CHANDRA, "Vrishabha"),
        (Graha.MANGALA, "Makara"),
        (Graha.BUDHA, "Kanya"),
        (Graha.GURU, "Karka"),
        (Graha.SHUKRA, "Meena"),
        (Graha.SHANI, "Tula"),
        (Graha.RAHU, None),
        (Graha.KETU, None),
    ],
)
def test_exaltation_rashi(
    graha,
    expected,
):
    assert get_exaltation_rashi(graha) == expected


@pytest.mark.parametrize(
    "graha,expected",
    [
        (Graha.SURYA, "Tula"),
        (Graha.CHANDRA, "Vrishchika"),
        (Graha.MANGALA, "Karka"),
        (Graha.BUDHA, "Meena"),
        (Graha.GURU, "Makara"),
        (Graha.SHUKRA, "Kanya"),
        (Graha.SHANI, "Mesha"),
        (Graha.RAHU, None),
        (Graha.KETU, None),
    ],
)
def test_debilitation_rashi(
    graha,
    expected,
):
    assert get_debilitation_rashi(graha) == expected


@pytest.mark.parametrize(
    "graha,expected",
    [
        (Graha.SURYA, ("Simha",)),
        (Graha.CHANDRA, ("Karka",)),
        (Graha.MANGALA, ("Mesha", "Vrishchika")),
        (Graha.BUDHA, ("Mithuna", "Kanya")),
        (Graha.GURU, ("Dhanu", "Meena")),
        (Graha.SHUKRA, ("Vrishabha", "Tula")),
        (Graha.SHANI, ("Makara", "Kumbha")),
        (Graha.RAHU, ()),
        (Graha.KETU, ()),
    ],
)
def test_own_rashi_names(
    graha,
    expected,
):
    assert get_own_rashis(graha) == expected


def test_placement_dignity():
    placement = calculate_graha_placement(
        Graha.SURYA,
        10.0,
    )

    from src.narayana.jyotish.dignity import get_graha_dignity

    assert get_graha_dignity(placement) is Dignity.EXALTED


@pytest.mark.parametrize(
    "invalid_graha",
    [
        "Sun",
        "Surya",
        1,
        None,
        True,
    ],
)
def test_invalid_graha_rejected(
    invalid_graha,
):
    with pytest.raises(
        TypeError,
        match="graha must be a Graha",
    ):
        get_dignity(
            invalid_graha,
            1,
        )


@pytest.mark.parametrize(
    "invalid_rashi",
    [
        0,
        13,
        -1,
        1.0,
        "1",
        None,
        True,
    ],
)
def test_invalid_rashi_rejected(
    invalid_rashi,
):
    with pytest.raises(
        ValueError,
        match="rashi_number must be an integer between 1 and 12",
    ):
        get_dignity(
            Graha.SURYA,
            invalid_rashi,
        )


def test_exaltation_table_contains_seven_classical_grahas():
    assert len(EXALTATION_RASHIS) == 7


def test_debilitation_table_contains_seven_classical_grahas():
    assert len(DEBILITATION_RASHIS) == 7


def test_own_sign_table_contains_seven_classical_grahas():
    assert len(OWN_RASHIS) == 7


def test_placement_type_validation():
    with pytest.raises(
        TypeError,
        match="placement must be a GrahaPlacement",
    ):
        from src.narayana.jyotish.dignity import get_graha_dignity

        get_graha_dignity(None)