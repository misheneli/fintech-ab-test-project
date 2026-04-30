"""
Main A/B test orchestrator.

Runs the complete analysis pipeline:
1. Load data
2. Validate (A/A test)
3. Calculate LTV
4. Statistical testing
5. Segment analysis
6. Generate report
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from src.helpers import two_sample_ttest, mann_whitney_test, check_normality, bootstrap_mean_diff
from src.visualization import plot_conversion_rate, plot_ltv, plot_ltv_distribution

logger = logging.getLogger(__name__)

SUBSCRIPTION_PRICE = 10.0  # USD per month
ALPHA = 0.05


class ABTestAnalyzer:
    """
    Orchestrates the complete A/B test analysis pipeline.

    Usage:
        analyzer = ABTestAnalyzer.from_csv("data/")
        report = analyzer.run()
        print(report.summary())
    """

    def __init__(
        self,
        users: pd.DataFrame,
        subscriptions: pd.DataFrame,
        trades: pd.DataFrame,
    ):
        self.users = users
        self.subscriptions = subscriptions
        self.trades = trades
        self._ltv: Optional[pd.DataFrame] = None

    @classmethod
    def from_csv(cls, data_dir: str | Path) -> "ABTestAnalyzer":
        """Load datasets from CSV files."""
        path = Path(data_dir)
        return cls(
            users=pd.read_csv(path / "users.csv", parse_dates=["registration_date", "first_deposit_date"]),
            subscriptions=pd.read_csv(path / "subscriptions.csv", parse_dates=["payment_date"]),
            trades=pd.read_csv(path / "trades.csv", parse_dates=["trade_date"]),
        )

    # ── 1. Validation ─────────────────────────────────────────────────────────

    def aa_test(self) -> dict:
        """
        Validate group balance before analysis.

        Returns dict with p-values for age, balance, deposit rate.
        If any p-value < 0.05, groups are imbalanced → experiment is invalid.
        """
        from scipy import stats

        a = self.users[self.users["group_name"] == "A"]
        b = self.users[self.users["group_name"] == "B"]

        _, p_age = stats.ttest_ind(a["age"], b["age"])
        _, p_bal = stats.ttest_ind(a["initial_balance_usd"], b["initial_balance_usd"])

        dep_a = a["first_deposit_date"].notna().sum()
        dep_b = b["first_deposit_date"].notna().sum()
        _, p_dep, _, _ = stats.chi2_contingency([
            [dep_a, len(a) - dep_a],
            [dep_b, len(b) - dep_b]
        ])

        result = {
            "group_a_n": len(a),
            "group_b_n": len(b),
            "age_pvalue": round(p_age, 4),
            "balance_pvalue": round(p_bal, 4),
            "deposit_pvalue": round(p_dep, 4),
            "is_valid": all(p > ALPHA for p in [p_age, p_bal, p_dep])
        }
        logger.info("A/A test: %s", result)
        return result

    # ── 2. LTV ────────────────────────────────────────────────────────────────

    def calculate_ltv(self) -> pd.DataFrame:
        """
        Calculate 6-month LTV per user.

        LTV = Subscription Revenue + Commission Revenue
        """
        sub_rev = (
            self.subscriptions.groupby("user_id").size()
            .mul(SUBSCRIPTION_PRICE).rename("sub_revenue")
        )
        comm_rev = (
            self.trades.groupby("user_id")["commission_usd"]
            .sum().rename("comm_revenue")
        )
        ltv = (
            self.users[["user_id", "group_name", "age", "first_deposit_date"]]
            .merge(sub_rev, on="user_id", how="left")
            .merge(comm_rev, on="user_id", how="left")
            .fillna({"sub_revenue": 0, "comm_revenue": 0})
        )
        ltv["ltv"] = ltv["sub_revenue"] + ltv["comm_revenue"]
        ltv["converted"] = ltv["sub_revenue"] > 0
        self._ltv = ltv
        return ltv

    # ── 3. Statistical test ───────────────────────────────────────────────────

    def test_significance(self) -> dict:
        """
        Test if LTV difference is statistically significant.

        Automatically selects t-test or Mann-Whitney based on normality check.
        Also computes bootstrap CI as robustness check.
        """
        if self._ltv is None:
            self.calculate_ltv()

        ltv_a = self._ltv[self._ltv["group_name"] == "A"]["ltv"]
        ltv_b = self._ltv[self._ltv["group_name"] == "B"]["ltv"]

        # Normality check → pick test
        norm = check_normality(ltv_a)
        if norm["is_normal"]:
            result = two_sample_ttest(ltv_a, ltv_b)
        else:
            result = mann_whitney_test(ltv_a, ltv_b)

        # Bootstrap as additional validation
        bootstrap = bootstrap_mean_diff(ltv_a, ltv_b)

        return {
            "test_used": result.test_name,
            "normality_check": norm,
            "statistic": result.statistic,
            "p_value": result.p_value,
            "is_significant": result.is_significant,
            "cohens_d": result.effect_size,
            "ci_95": result.confidence_interval,
            "bootstrap_ci": (bootstrap["ci_lower"], bootstrap["ci_upper"]),
            "interpretation": result.interpretation,
        }

    # ── 4. Segment analysis ───────────────────────────────────────────────────

    def segment_analysis(self) -> pd.DataFrame:
        """
        Break down LTV by age group and deposit behavior.
        """
        if self._ltv is None:
            self.calculate_ltv()

        df = self._ltv.copy()
        df["age_group"] = pd.cut(
            self.users.set_index("user_id").loc[df["user_id"]]["age"].values,
            bins=[17, 25, 35, 100],
            labels=["18-25", "26-35", "36+"]
        )
        df["deposited"] = df["first_deposit_date"].notna().astype(int)

        return (
            df.groupby(["group_name", "age_group", "deposited"])["ltv"]
            .agg(["mean", "median", "count"])
            .rename(columns={"mean": "avg_ltv", "median": "median_ltv", "count": "users"})
            .reset_index()
        )
