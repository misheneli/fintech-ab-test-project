# Executive Summary: Free Trial A/B Experiment
**WealthApp Premium Subscription Optimization | Q4 2023**

---

## TL;DR

> The 30-day free trial **significantly increased sign-ups (+40%)** but **did not improve 
> 6-month LTV** (p=0.67). A targeted rollout to depositing users, who show 3× higher LTV, 
> is recommended over a broad launch.

---

## 1. Business Context

WealthApp faces a conversion bottleneck: only **2% of new users** subscribe to the 
$10/month premium plan. The hypothesis under test: a 30-day free trial reduces 
the initial price barrier and leads to higher long-term revenue.

**Experiment period:** Nov 1 – Nov 21, 2023 (recruitment) + 6-month observation  
**Sample size:** 8,000 users (4,000 per group)

---

## 2. Key Results

| Metric | Control (A) | Treatment (B) | Δ | Significant? |
|--------|------------|---------------|---|-------------|
| Conversion Rate | 2.0% | 2.8% | +40% | Yes (p=0.01) |
| Average LTV | $15.20 | $15.80 | +3.9% |  No (p=0.67) |
| Avg Subscription Revenue | $10.40 | $10.90 | +4.8% |  No |
| Churn after Trial | — | 40% | — | — |

---

## 3. The Paradox: More Users, Same Revenue

The free trial attracted **40% more subscribers** but monthly churn after the trial ended 
(40%) nullified the revenue gain. Users who signed up for a free trial showed lower 
long-term commitment than users who paid upfront.

**Root cause:** Free trial self-selects price-sensitive users with lower willingness to pay.

---

## 4. Key Insight: The Depositor Segment

Within Group B, users who made a deposit during the trial period showed dramatically 
different behavior:

| Segment | LTV | vs. Non-Depositors |
|---------|-----|-------------------|
| Depositors during trial | $42.50 | +199% |
| Non-depositors | $14.20 | baseline |

This 3× difference reveals the free trial is a powerful tool — **when targeted correctly**.

---

## 5. Recommendations

### Do Not: Broad Launch
Rolling out the free trial to all users risks diluting brand perception 
(premium = free?) without revenue upside.

###  Targeted Free Trial
Trigger the free trial offer only for users who make an initial deposit 
within the first 7 days. Expected outcome: 3× LTV vs. non-targeted approach.

### Next Experiment
Test a **deposit-gated free trial**: users who deposit ≥$100 receive 30 days free. 
Hypothesis: self-selection of high-intent users improves post-trial retention.

---

## 6. Statistical Confidence

- **LTV test:** Two-sample t-test, α=0.05, Cohen's d=0.04 (negligible effect)
- **Normality check:** Shapiro-Wilk confirms non-normal LTV → Mann-Whitney U 
  used as robustness check, confirming same conclusion
- **Power:** 80% power to detect d≥0.2 with n=4000 per group
