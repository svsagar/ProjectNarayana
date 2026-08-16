"""Tests for Graha analysis."""

import pytest

from src.narayana.jyotish.analysis import (
    GrahaAnalysis,
    analyze_graha,
)
from src.narayana.jyotish.graha import Graha
from src.narayana.jyotish.placement import (
    calculate_graha_placement,
)


def test_analyze_sun_exalted():
    placement = calculate_graha_placement(
        Graha.SURYA,
        10.0,
    )

    analysis = analyze_graha(placement)

    assert isinstance(analysis, GrahaAnalysis)
    assert analysis.placement is placement
    assert analysis.dignity_score == 5


def test_analyze_sun_own_sign():
    placement = calculate_graha_placement(
        Graha.SURYA,
        120.0,
    )

    analysis = analyze_graha(placement)

    assert analysis.dignity_score == 4


def test_analyze_sun_debilitated():
    placement = calculate_graha_placement(
        Graha.SURYA,
        190.0,
    )

    analysis = analyze_graha(placement)

    assert analysis.dignity_score == 0


def test_analyze_rejects_invalid_placement():
    with pytest.raises(
        TypeError,
        match="placement must be a GrahaPlacement",
    ):
        analyze_graha(None)