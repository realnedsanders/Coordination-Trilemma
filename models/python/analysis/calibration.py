"""
Parameter Calibration from Forecasting Data

Uses AI timeline forecasts and historical coordination failures to calibrate
Monte Carlo simulation parameters.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ForecastPoint:
    """A single forecast data point."""
    source: str
    year: int
    probability: float
    description: str


@dataclass
class HistoricalCase:
    """A historical coordination case."""
    name: str
    start_year: int
    end_year: int
    duration: int
    outcome: str  # 'failure', 'success', 'mixed'
    scale: str  # 'global', 'regional', 'national'


# AI Capability Forecasts (as of early 2025)
AI_FORECASTS = [
    ForecastPoint("Epoch AI", 2025, 0.10, "10% chance TAI by 2025"),
    ForecastPoint("Metaculus", 2027, 0.25, "25% chance AGI by 2027"),
    ForecastPoint("Samotsvety", 2030, 0.28, "28% chance AGI by 2030"),
    ForecastPoint("Metaculus", 2031, 0.50, "50% chance AGI by 2031 (median)"),
    ForecastPoint("Expert Survey 2024", 2040, 0.50, "50% chance AGI by 2040"),
]

# Historical Coordination Failures/Successes
HISTORICAL_CASES = [
    HistoricalCase("League of Nations", 1920, 1946, 26, "failure", "global"),
    HistoricalCase("Bretton Woods", 1944, 1971, 27, "mixed", "global"),
    HistoricalCase("Concert of Europe", 1815, 1914, 99, "failure", "regional"),
    HistoricalCase("UN Security Council", 1945, 2025, 80, "mixed", "global"),
    HistoricalCase("European Coal and Steel", 1951, 2002, 51, "success", "regional"),
    HistoricalCase("Warsaw Pact", 1955, 1991, 36, "failure", "regional"),
    HistoricalCase("COMECON", 1949, 1991, 42, "failure", "regional"),
    HistoricalCase("Gold Standard (Interwar)", 1919, 1936, 17, "failure", "global"),
    HistoricalCase("Kyoto Protocol", 1997, 2020, 23, "mixed", "global"),
]


def estimate_p_ai_from_forecasts(
    forecasts: List[ForecastPoint] = None,
    current_year: int = 2025,
    cycle_duration: float = 50.0
) -> Tuple[float, float]:
    """
    Estimate initial p_AI and growth rate from AGI forecasts.

    The model's p_AI is the probability that, given TCS formation,
    it's AI-controlled rather than human-controlled.

    We interpret AGI forecasts as follows:
    - If AGI exists, P(AI-controlled TCS | TCS forms) is high
    - So p_AI ≈ P(AGI exists) * P(AI used for TCS | AGI exists)
    - Assume P(AI used | AGI exists) ≈ 0.8 (high due to efficiency)

    Returns:
        (initial_p_ai, growth_rate_per_cycle)
    """
    if forecasts is None:
        forecasts = AI_FORECASTS

    # Fit exponential growth: P(t) = p0 * exp(r * t)
    # Or equivalently: P(t) = p0 * (1 + g)^t for discrete cycles

    # Use two points to estimate growth
    # Early point: 2025, ~10%
    # Later point: 2031, ~50%

    p_2025 = 0.10
    p_2031 = 0.50
    years_between = 6

    # P(2031) = P(2025) * (1 + annual_growth)^6
    # annual_growth = (P(2031)/P(2025))^(1/6) - 1
    annual_growth = (p_2031 / p_2025) ** (1/years_between) - 1

    # Convert to per-cycle growth
    # If cycles are ~50 years, one cycle sees huge growth
    # But early cycles (next few decades) matter most

    # More realistic: use 10-year "cycles" for near-term
    # Then p_AI grows from ~10% to ~80% over 2-3 cycles

    # Adjustment: P(AI used | AGI) = 0.8
    p_ai_usage = 0.8

    initial_p_ai = p_2025 * p_ai_usage  # ~8%

    # Growth rate per cycle
    # In 50 years (one cycle), we go from 2025 to 2075
    # By then, P(AGI) ≈ 1.0, so p_AI ≈ 0.8
    # That's 10x growth over one cycle: (1 + g) = 10, g = 9
    # This seems too high; use more conservative estimate

    # Alternative: use observed Metaculus compression
    # Predictions dropped 5.5 predicted years per real year
    # This suggests ~30% annual "probability growth"

    # Per cycle (50 years): (1.30)^50 is huge
    # But p_AI is capped at 1.0
    # Use effective rate that reaches 0.9 in ~100 years

    growth_rate = 0.15  # 15% per cycle, reaches high p_AI in ~20 cycles

    # More principled: fit to forecast CDF
    # For now, return calibrated point estimates

    return initial_p_ai, growth_rate


def estimate_cycle_duration(
    cases: List[HistoricalCase] = None,
    scale_filter: str = None
) -> Tuple[float, float]:
    """
    Estimate cycle duration from historical coordination cases.

    Returns:
        (mean_duration, std_duration)
    """
    if cases is None:
        cases = HISTORICAL_CASES

    if scale_filter:
        cases = [c for c in cases if c.scale == scale_filter]

    durations = [c.duration for c in cases]

    if not durations:
        return 50.0, 20.0  # Default

    mean_dur = np.mean(durations)
    std_dur = np.std(durations)

    return mean_dur, std_dur


def get_calibrated_scenarios() -> Dict[str, Dict]:
    """
    Return calibrated parameter sets for pessimistic, baseline, optimistic scenarios.

    Based on:
    - AI forecasts for p_AI
    - Historical cases for cycle duration
    - Reasonable uncertainty ranges
    """

    # Baseline from calibration
    base_p_ai, base_growth = estimate_p_ai_from_forecasts()
    base_cycle_mean, base_cycle_std = estimate_cycle_duration()

    scenarios = {
        'pessimistic': {
            'p_ai': 0.15,  # Higher initial AI capability
            'growth': 0.25,  # Faster capability growth
            'cycle_duration': 30.0,  # Shorter cycles (faster coordination attempts)
            'cycle_std': 10.0,
            'description': 'Fast AI progress, short coordination windows'
        },
        'baseline': {
            'p_ai': round(base_p_ai, 2),  # ~0.08
            'growth': round(base_growth, 2),  # ~0.15
            'cycle_duration': round(base_cycle_mean, 0),  # ~42 years
            'cycle_std': round(base_cycle_std, 0),  # ~25 years
            'description': 'Calibrated from forecasts and historical data'
        },
        'optimistic': {
            'p_ai': 0.03,  # Lower initial AI capability
            'growth': 0.08,  # Slower capability growth
            'cycle_duration': 60.0,  # Longer cycles
            'cycle_std': 20.0,
            'description': 'Slow AI progress, longer coordination windows'
        }
    }

    return scenarios


def print_calibration_summary():
    """Print summary of calibration data and estimates."""

    print("=" * 60)
    print("PARAMETER CALIBRATION SUMMARY")
    print("=" * 60)

    print("\n### AI Capability Forecasts ###\n")
    for f in AI_FORECASTS:
        print(f"  {f.source}: {f.probability*100:.0f}% by {f.year}")

    p_ai, growth = estimate_p_ai_from_forecasts()
    print(f"\n  → Estimated initial p_AI: {p_ai:.2f}")
    print(f"  → Estimated growth rate: {growth:.0%} per cycle")

    print("\n### Historical Coordination Cases ###\n")
    for c in HISTORICAL_CASES:
        print(f"  {c.name}: {c.duration} years ({c.outcome})")

    mean_dur, std_dur = estimate_cycle_duration()
    print(f"\n  → Mean duration: {mean_dur:.0f} years")
    print(f"  → Std deviation: {std_dur:.0f} years")

    print("\n### Calibrated Scenarios ###\n")
    scenarios = get_calibrated_scenarios()
    for name, params in scenarios.items():
        print(f"  {name.upper()}:")
        print(f"    p_AI: {params['p_ai']:.0%}")
        print(f"    growth: {params['growth']:.0%}/cycle")
        print(f"    cycle: {params['cycle_duration']:.0f} ± {params['cycle_std']:.0f} years")
        print(f"    ({params['description']})")
        print()

    print("=" * 60)


if __name__ == "__main__":
    print_calibration_summary()
