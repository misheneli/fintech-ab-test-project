"""
Visualization module for A/B test analysis.

All plots follow a consistent style with:
- Confidence intervals
- Statistical annotations
- Export-ready quality (300 DPI)
- Business-friendly color palette
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path
from typing import Optional

# ─── Style ──────────────────────────────────────────────────────────────────
PALETTE = {"control": "#2196F3", "treatment": "#4CAF50", "highlight": "#FF5722"}
sns.set_theme(style="whitegrid", palette="muted")


def plot_conversion_rate(
    control_rate: float,
    treatment_rate: float,
    ci_control: tuple[float, float] = (0.0, 0.0),
    ci_treatment: tuple[float, float] = (0.0, 0.0),
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """
    Bar chart comparing conversion rates with confidence intervals.

    Args:
        control_rate: Conversion rate for Group A (0–1)
        treatment_rate: Conversion rate for Group B (0–1)
        ci_control: (lower, upper) 95% CI for control
        ci_treatment: (lower, upper) 95% CI for treatment
        save_path: If provided, saves figure to this path

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    groups = ["Control (A)\nImmediate Paywall", "Treatment (B)\nFree Trial"]
    rates = [control_rate, treatment_rate]
    colors = [PALETTE["control"], PALETTE["treatment"]]
    
    bars = ax.bar(groups, [r * 100 for r in rates], color=colors, width=0.5, zorder=3)
    
    # Error bars from CI
    yerr_lower = [
        (control_rate - ci_control[0]) * 100,
        (treatment_rate - ci_treatment[0]) * 100,
    ]
    yerr_upper = [
        (ci_control[1] - control_rate) * 100,
        (ci_treatment[1] - treatment_rate) * 100,
    ]
    ax.errorbar(
        groups, [r * 100 for r in rates],
        yerr=[yerr_lower, yerr_upper],
        fmt="none", color="black", capsize=6, linewidth=2
    )
    
    # Value labels on bars
    for bar, rate in zip(bars, rates):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{rate:.2%}",
            ha="center", va="bottom", fontsize=12, fontweight="bold"
        )
    
    # Lift annotation
    lift = (treatment_rate - control_rate) / control_rate * 100
    ax.annotate(
        f"Lift: {lift:+.1f}%",
        xy=(1, treatment_rate * 100),
        xytext=(0.5, max(rates) * 100 * 1.15),
        fontsize=11, color=PALETTE["highlight"], fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=PALETTE["highlight"])
    )
    
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_title("Conversion Rate by Group (with 95% CI)", fontsize=14, pad=15)
    ax.set_ylabel("Conversion Rate (%)")
    ax.set_ylim(0, max(rates) * 100 * 1.4)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    
    return fig


def plot_ltv_distribution(
    ltv_df: pd.DataFrame,
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """
    KDE + rug plot of LTV distributions for both groups.

    Shows the full distribution shape, not just averages.

    Args:
        ltv_df: DataFrame with columns ['group_name', 'ltv']
        save_path: Optional export path

    Returns:
        matplotlib Figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for i, (group, label, color) in enumerate([
        ("A", "Control (A)", PALETTE["control"]),
        ("B", "Treatment (B)", PALETTE["treatment"])
    ]):
        data = ltv_df[ltv_df["group_name"] == group]["ltv"]
        sns.histplot(data, kde=True, ax=axes[i], color=color, bins=30, alpha=0.6)
        axes[i].axvline(data.mean(), color="red", linestyle="--", label=f"Mean: ${data.mean():.2f}")
        axes[i].axvline(data.median(), color="orange", linestyle=":", label=f"Median: ${data.median():.2f}")
        axes[i].set_title(f"LTV Distribution — {label}", fontsize=12)
        axes[i].set_xlabel("LTV ($)")
        axes[i].legend()
    
    fig.suptitle("6-Month LTV Distribution by Group", fontsize=14, y=1.02)
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    return fig


def plot_ltv(
    control_ltv: float,
    treatment_ltv: float,
    p_value: float = None,
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """
    Bar chart of average LTV with significance annotation.

    Args:
        control_ltv: Mean LTV for control group
        treatment_ltv: Mean LTV for treatment group
        p_value: Optional p-value to annotate significance
        save_path: Optional export path
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    groups = ["Control (A)", "Treatment (B)"]
    values = [control_ltv, treatment_ltv]
    colors = [PALETTE["control"], PALETTE["treatment"]]
    
    bars = ax.bar(groups, values, color=colors, width=0.5, zorder=3)
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            f"${val:.2f}", ha="center", fontweight="bold", fontsize=12
        )
    
    if p_value is not None:
        sig_label = "✓ Significant (p<0.05)" if p_value < 0.05 else f"✗ Not Significant (p={p_value:.3f})"
        ax.set_title(f"Average 6-Month LTV by Group\n{sig_label}", fontsize=13)
    else:
        ax.set_title("Average 6-Month LTV by Group", fontsize=13)
    
    ax.set_ylabel("Average LTV ($)")
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("$%.0f"))
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    return fig


def plot_segment_heatmap(
    segment_df: pd.DataFrame,
    metric: str = "ltv",
    save_path: Optional[Path] = None,
) -> plt.Figure:
    """
    Heatmap of LTV across segments (age × deposit behavior).

    Args:
        segment_df: DataFrame with segment breakdown
        metric: Column to visualize
        save_path: Optional export path
    """
    pivot = segment_df.pivot_table(values=metric, index="age_group", columns="deposited", aggfunc="mean")
    pivot.columns = ["No Deposit", "Made Deposit"]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlGnBu", ax=ax, cbar_kws={"label": f"Avg {metric.upper()} ($)"})
    ax.set_title(f"Average {metric.upper()} by Age Group and Deposit Behavior", fontsize=13)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    return fig
