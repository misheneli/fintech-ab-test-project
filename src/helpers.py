"""
Statistical utilities for A/B test analysis.

Provides:
- Two-sample t-test and Mann-Whitney U test
- Cohen's d effect size
- Bootstrap confidence intervals
- Normality check (Shapiro-Wilk)
- Confidence interval for difference of means
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """
    Container for statistical test output.

    Attributes:
        test_name: Name of the test used
        statistic: Test statistic (t or U)
        p_value: Two-tailed p-value
        is_significant: True if p_value < alpha
        alpha: Significance level used
        effect_size: Cohen's d
        confidence_interval: 95% CI for the difference of means
        interpretation: Human-readable conclusion
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
    alpha: float = 0.05,
) -> TestResult:
    """
    Independent two-sample t-test (two-tailed).

    H0: mean(control) == mean(treatment)
    H1: mean(control) != mean(treatment)

    Use when both groups are normally distributed (verified by check_normality).

    Args:
        control: LTV values for Group A
        treatment: LTV values for Group B
        alpha: Significance level (default 0.05)

    Returns:
        TestResult dataclass with all statistics

    Example:
        >>> result = two_sample_ttest(ltv_a, ltv_b)
        >>> print(result.is_significant)  # False
        >>> print(result.interpretation)
        'Difference is NOT statistically significant (p=0.6700), with negligible effect size (d=0.040)'
    """
    t_stat, p_value = stats.ttest_ind(control, treatment)
    d = cohens_d(control, treatment)
    ci = confidence_interval_for_diff(control, treatment)

    return TestResult(
        test_name="Two-sample t-test (two-tailed)",
        statistic=float(t_stat),
        p_value=float(p_value),
        is_significant=bool(p_value < alpha),
        alpha=alpha,
        effect_size=d,
        confidence_interval=ci,
        interpretation=_interpret(p_value, alpha, d),
    )


def mann_whitney_test(
    control: pd.Series,
    treatment: pd.Series,
    alpha: float = 0.05,
) -> TestResult:
    """
    Non-parametric Mann-Whitney U test (two-tailed).

    Preferred over t-test when LTV distributions are skewed (typical in fintech).
    Does not assume normality.

    Args:
        control: LTV values for Group A
        treatment: LTV values for Group B
        alpha: Significance level (default 0.05)

    Returns:
        TestResult dataclass with all statistics
    """
    u_stat, p_value = stats.mannwhitneyu(control, treatment, alternative="two-sided")
    d = cohens_d(control, treatment)
    ci = confidence_interval_for_diff(control, treatment)

    return TestResult(
        test_name="Mann-Whitney U test (non-parametric)",
        statistic=float(u_stat),
        p_value=float(p_value),
        is_significant=bool(p_value < alpha),
        alpha=alpha,
        effect_size=d,
        confidence_interval=ci,
        interpretation=_interpret(p_value, alpha, d),
    )


def cohens_d(group_a: pd.Series, group_b: pd.Series) -> float:
    """
    Calculate Cohen's d effect size between two groups.

    Interpretation guide:
        |d| < 0.2  → Negligible
        0.2–0.5    → Small
        0.5–0.8    → Medium
        |d| > 0.8  → Large

    Args:
        group_a: First group values
        group_b: Second group values

    Returns:
        Absolute value of Cohen's d
    """
    n_a, n_b = len(group_a), len(group_b)
    pooled_var = (
        (n_a - 1) * group_a.std() ** 2 + (n_b - 1) * group_b.std() ** 2
    ) / (n_a + n_b - 2)
    pooled_std = np.sqrt(pooled_var)

    if pooled_std == 0:
        return 0.0
    return float(abs(group_a.mean() - group_b.mean()) / pooled_std)


def confidence_interval_for_diff(
    control: pd.Series,
    treatment: pd.Series,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """
    Parametric confidence interval for the difference of means (treatment - control).

    If the interval contains 0, the difference is not statistically significant.

    Args:
        control: Control group values
        treatment: Treatment group values
        confidence: Confidence level (default 0.95 → 95% CI)

    Returns:
        (lower_bound, upper_bound) of the CI
    """
    diff = treatment.mean() - control.mean()
    se = np.sqrt(
        control.var() / len(control) + treatment.var() / len(treatment)
    )
    z = stats.norm.ppf((1 + confidence) / 2)
    return (float(diff - z * se), float(diff + z * se))


def check_normality(data: pd.Series, alpha: float = 0.05) -> dict:
    """
    Shapiro-Wilk normality test to decide which statistical test to use.

    Samples up to 5000 points (Shapiro-Wilk requires n ≤ 5000).

    Args:
        data: Series to test for normality
        alpha: Significance level for the normality test

    Returns:
        {
            'is_normal': bool,
            'p_value': float,
            'recommendation': 't-test' | 'Mann-Whitney U'
        }
    """
    sample = data.sample(min(len(data), 5000), random_state=42)
    _, p_value = stats.shapiro(sample)
    is_normal = bool(p_value > alpha)

    return {
        "is_normal": is_normal,
        "p_value": float(p_value),
        "recommendation": "t-test" if is_normal else "Mann-Whitney U",
    }


def bootstrap_mean_diff(
    control: pd.Series,
    treatment: pd.Series,
    n_iterations: int = 10_000,
    confidence: float = 0.95,
    random_state: int = 42,
) -> dict:
    """
    Bootstrap confidence interval for the difference of means.

    More robust than parametric CI for skewed LTV distributions.
    Used as a robustness check alongside the primary statistical test.

    Args:
        control: Control group values
        treatment: Treatment group values
        n_iterations: Number of bootstrap resamples (default 10,000)
        confidence: Confidence level (default 0.95)
        random_state: Random seed for reproducibility

    Returns:
        {
            'mean_diff': float,        # treatment.mean - control.mean
            'ci_lower': float,
            'ci_upper': float
        }
    """
    rng = np.random.default_rng(random_state)
    diffs = np.array([
        rng.choice(treatment.values, len(treatment)).mean()
        - rng.choice(control.values, len(control)).mean()
        for _ in range(n_iterations)
    ])
    alpha = 1 - confidence
    return {
        "mean_diff": float(diffs.mean()),
        "ci_lower": float(np.percentile(diffs, alpha / 2 * 100)),
        "ci_upper": float(np.percentile(diffs, (1 - alpha / 2) * 100)),
    }


def calculate_percentile(data: pd.Series, percentile: float) -> float:
    """
    Calculate a specific percentile from a series.

    Args:
        data: Input data
        percentile: Percentile to compute (0–100)

    Returns:
        Percentile value
    """
    return float(np.percentile(data, percentile))


# ── Private helpers ──────────────────────────────────────────────────────────

def _interpret(p_value: float, alpha: float, d: float) -> str:
    """Generate a plain-English interpretation of test results."""
    sig = (
        "statistically significant"
        if p_value < alpha
        else "NOT statistically significant"
    )
    if abs(d) < 0.2:
        magnitude = "negligible"
    elif abs(d) < 0.5:
        magnitude = "small"
    elif abs(d) < 0.8:
        magnitude = "medium"
    else:
        magnitude = "large"
    return (
        f"Difference is {sig} (p={p_value:.4f}), "
        f"with {magnitude} effect size (d={d:.3f})"
    )
