"""Public Jyotish birth-chart calculation API."""

from __future__ import annotations

from src.narayana.astronomy.calculator import calculate as calculate_astronomy
from src.narayana.astronomy.models import (
    AstronomyResult,
    BirthInput,
    CalculationConfig,
)

from .birth_chart import (
    JyotishBirthChart,
    calculate_birth_chart,
)


def calculate_jyotish_birth_chart(
    birth_input: BirthInput,
    calculation_config: CalculationConfig | None = None,
) -> JyotishBirthChart:
    """Calculate a complete Jyotish birth chart from birth details.

    The astronomy layer remains the single source of truth for
    astronomical calculations. This function only orchestrates the
    conversion into the Jyotish representation.
    """

    if not isinstance(birth_input, BirthInput):
        raise TypeError("birth_input must be a BirthInput")

    if calculation_config is None:
        calculation_config = CalculationConfig()

    if not isinstance(calculation_config, CalculationConfig):
        raise TypeError(
            "calculation_config must be a CalculationConfig"
        )

    astronomy_result: AstronomyResult = calculate_astronomy(
        birth_input,
        calculation_config,
    )

    return calculate_birth_chart(astronomy_result)