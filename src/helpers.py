"""
Statistical utilities for A/B test analysis.

Module provides:
- Statistical testing (t-test, Mann-Whitney U)
- Effect size calculation (Cohen's d)
- Power analysis
- Confidence interval calculation
- Bootstrap resampling
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """
    Result of a statistical test.

    Attributes:
        test_name: Name of statistical test used
        statistic: Test statistic value
        p_value: P-value of the test
        is_significant: True if p_value < alpha
        alpha: Significance level used (default 0.05)
        effect_size: Cohen's d or other effect size metric
        confidence_interval: 95% CI for the difference
        interpretation: Human-readable interpretation
    """
    test_name: str
    statistic: float
    p_value: float
    is_significant: bool
    alpha: float
    effect_size: float
    confidence_interval: tuple[float, float]
    interpretation: str


def two_sample_ttest(
    control: pd.Series,
    treatment: pd.Series,
    alpha: float = 0.05
) -> TestResult:
    """
    Perform two-sample independent t-test.

    H0: mean(control) == mean(treatment)
    H1: mean(control) != mean(treatment)

    Args:
        control: Values from control group (A)
        treatment: Values from treatment group (B)
        alpha: Significance level (default 0.05)

    Returns:
        TestResult with full statistics

    Example:
        >>> result = two_sample_ttest(ltv_A, ltv_B)
        >>> print(result.is_significant)
        False
    """
    t_stat, p_value = stats.ttest_ind(control, treatment)
    d = cohens_d(control, treatment)
    ci = confidence_interval_for_diff(control, treatment)

    return TestResult(
        test_name="Two-sample t-test (two-tailed)",
        statistic=float(t_stat),
        p_value=float(p_value),
        is_significant=p_value < alpha,
        alpha=alpha,
        effect_size=d,
        confidence_interval=ci,
        interpretation=_interpret_result(p_value, alpha, d)
    )


def mann_whitney_test(
    control: pd.Series,
    treatment: pd.Series,
    alpha: float = 0.05
) -> TestResult:
    """
    Non-parametric Mann-Whitney U test (used when LTV is not normally distributed).

    Preferred over t-test when:
    - Distributions are heavily skewed (typical for LTV)
    - Sample size < 30

    Args:
        control: Values from control group
        treatment: Values from treatment group
        alpha: Significance level

    Returns:
        TestResult with full statistics
    """
    u_stat, p_value = stats.mannwhitneyu(control, treatment, alternative="two-sided")
    d = cohens_d(control, treatment)
    ci = confidence_interval_for_diff(control, treatment)

    return TestResult(
        test_name="Mann-Whitney U test (non-parametric)",
        statistic=float(u_stat),
        p_value=float(p_value),
        is_significant=p_value < alpha,
        alpha=alpha,
        effect_size=d,
        confidence_interval=ci,
        interpretation=_interpret_result(p_value, alpha, d)
    )


def cohens_d(group_a: pd.Series, group_b: pd.Series) -> float:
    """
    Calculate Cohen's d effect size.

    Interpretation:
        d < 0.2  → Negligible
        0.2–0.5  → Small
        0.5–0.8  → Medium
        d > 0.8  → Large

    Args:
        group_a: First group values
        group_b: Second group values

    Returns:
        Cohen's d effect size (absolute value)
    """
    n_a, n_b = len(group_a), len(group_b)
    pooled_std = np.sqrt(
        ((n_a - 1) * group_a.std() ** 2 + (n_b - 1) * group_b.std() ** 2)
        / (n_a + n_b - 2)
    )
    return abs((group_a.mean() - group_b.mean()) / pooled_std) if pooled_std else 0.0


def confidence_interval_for_diff(
    control: pd.Series,
    treatment: pd.Series,
    confidence: float = 0.95
) -> tuple[float, float]:
    """
    95% confidence interval for the difference of means.

    If CI includes 0, the difference is not statistically significant.

    Returns:
        (lower_bound, upper_bound)
    """
    diff = treatment.mean() - control.mean()
    se = np.sqrt(control.var() / len(control) + treatment.var() / len(treatment))
    z = stats.norm.ppf((1 + confidence) / 2)
    return (diff - z * se, diff + z * se)


def check_normality(data: pd.Series, alpha: float = 0.05) -> dict:
    """
    Shapiro-Wilk normality test.

    Decides whether t-test or Mann-Whitney is appropriate.

    Args:
        data: Series to test
        alpha: Significance level

    Returns:
        {'is_normal': bool, 'p_value': float, 'recommendation': str}
    """
    stat, p_value = stats.shapiro(data.sample(min(len(data), 5000), random_state=42))
    is_normal = p_value > alpha
    return {
        "is_normal": is_normal,
        "p_value": float(p_value),
        "recommendation": "t-test" if is_normal else "Mann-Whitney U"
    }


def bootstrap_mean_diff(
    control: pd.Series,
    treatment: pd.Series,
    n_iterations: int = 10_000,
    confidence: float = 0.95,
    random_state: int = 42
) -> dict:
    """
    Bootstrap confidence interval for mean difference.

    More robust than parametric CI for skewed LTV distributions.

    Args:
        control: Control group values
        treatment: Treatment group values
        n_iterations: Bootstrap resampling iterations
        confidence: Confidence level

    Returns:
        {'mean_diff': float, 'ci_lower': float, 'ci_upper': float}
    """
    rng = np.random.default_rng(random_state)
    diffs = [
        rng.choice(treatment, len(treatment)).mean()
        - rng.choice(control, len(control)).mean()
        for _ in range(n_iterations)
    ]
    alpha = 1 - confidence
    return {
        "mean_diff": float(np.mean(diffs)),
        "ci_lower": float(np.percentile(diffs, alpha / 2 * 100)),
        "ci_upper": float(np.percentile(diffs, (1 - alpha / 2) * 100)),
    }


def calculate_percentile(data: pd.Series, percentile: float) -> float:
    """Calculate a specific percentile."""
    return float(np.percentile(data, percentile))


def _interpret_result(p_value: float, alpha: float, cohens_d: float) -> str:
    """Generate human-readable interpretation."""
    significance = "statistically significant" if p_value < alpha else "NOT statistically significant"
    if abs(cohens_d) < 0.2:
        magnitude = "negligible"
    elif abs(cohens_d) < 0.5:
        magnitude = "small"
    elif abs(cohens_d) < 0.8:
        magnitude = "medium"
    else:
        magnitude = "large"
    return f"Difference is {significance} (p={p_value:.4f}), with {magnitude} effect size (d={cohens_d:.3f})"
