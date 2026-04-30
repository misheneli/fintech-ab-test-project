

# FinTech A/B Test Analysis: Premium Subscription Model

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/jupyter-notebook-orange)](https://jupyter.org/)
[![SQL](https://img.shields.io/badge/SQL-querying-green)](https://en.wikipedia.org/wiki/SQL)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/your-username/fintech-ab-test-project)

## 📋 Project Overview

This project demonstrates a comprehensive A/B test analysis for a FinTech application, simulating real-world business decision making. The analysis evaluates whether introducing a **30-day free trial** for a premium subscription leads to higher **Lifetime Value (LTV)** compared to the existing immediate paywall model.

## 🔬 Analysis Modules

| Module | Description |
|--------|-------------|
| `src/ab_test_analyzer.py` | Main orchestrator — runs full pipeline via `ABTestAnalyzer` class |
| `src/helpers.py` | Statistical utilities: t-test, Mann-Whitney U, Cohen's d, bootstrap CI |
| `src/visualization.py` | Publication-ready charts with CI, lift annotations, segment heatmaps |
| `docs/SYSTEM_REQUIREMENTS.md` | Functional & non-functional requirements, data model |
| `docs/ARCHITECTURE.md` | System design, data flow, component diagram |

**Key Skills Demonstrated:**
- 🗄️ **SQL**: Complex querying for cohort analysis and LTV calculation
- 📈 **A/B Testing**: Experimental design and statistical analysis
- 🐍 **Python**: Data analysis, visualization, and statistical testing
- 📊 **Data Visualization**: Creating insightful business dashboards
- 💡 **Business Acumen**: Translating data insights into actionable recommendations

## 🎯 Business Problem

"WealthApp," a hypothetical investment platform, struggles with low conversion rates (~2%) to its premium subscription ($10/month). The marketing hypothesis suggests that a free trial would reduce the initial barrier to entry, increase conversion, and ultimately improve long-term revenue (LTV). This project tests that hypothesis through a controlled experiment.

## 🧪 Experiment Design

| Aspect | Details |
|--------|---------|
| **Control Group (A)** | Current model: "Premium for $10/month" |
| **Treatment Group (B)** | New model: "Try Premium free for 30 days, then $10/month" |
| **Primary Metric** | User LTV after 6 months |
| **Sample Size** | 8,000 newly registered users |
| **Duration** | 3-week recruitment + 6-month observation period |
| **Statistical Significance** | α = 0.05 using two-tailed t-test |

## 📁 Project Structure

```
fintech-ab-test-project/
├── data/                    # Synthetic data for analysis
│   ├── users.csv           # User demographics and group assignment
│   ├── subscriptions.csv   # Subscription events and payments
│   ├── trades.csv          # Trading activity and commissions
│   └── README.md           # Data dictionary and description
├── sql/                    # SQL queries for analysis
│   ├── 1_aa_test_check.sql          # Group balance verification
│   ├── 2_ltv_calculation.sql        # Main LTV analysis
│   └── 3_additional_analysis.sql    # Segment analysis
├── notebooks/              # Jupyter notebooks
│   └── Fintech_ABTest_Analysis.ipynb  # Complete analysis
├── src/                    # Python utility functions
│   ├── visualization.py    # Plotting functions
│   └── helpers.py          # Statistical utilities
├── docs/                   # Documentation
│   └── project_summary.md  # Executive summary
├── generate_data.py        # Synthetic data generation
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/fintech-ab-test-project.git
   cd fintech-ab-test-project
   ```

2. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Generate data**
   ```bash
   python generate_data.py
   ```

4. **Run analysis**
   ```bash
   jupyter notebook
   ```
   Then open `notebooks/Fintech_ABTest_Analysis.ipynb`

## 📊 Key Findings

> **The free trial model increased conversion by 45% but did not significantly improve 6-month LTV due to higher post-trial churn. However, users who made deposits during the trial showed 3x higher LTV.**

### Results Summary:
- **Conversion Rate**: 
  - Control (A): 2.0% 
  - Treatment (B): 2.8% (+40%)
- **Average LTV**: 
  - Control (A): $15.20
  - Treatment (B): $15.80 (not statistically significant)
- **Segment Analysis**:
  - Depositors during trial: $42.50 LTV
  - Non-depositors: $14.20 LTV

## 💡 Business Recommendations

1. **❌ Do not roll out** the free trial model broadly to all users
2. **✅ Implement targeted free trials** for users who make an initial deposit
3. **🔄 Improve onboarding** during trial period to demonstrate value
4. **📊 Continue testing** with different trial durations or pricing strategies

## 🛠️ Technical Implementation

### Data Generation
The synthetic data simulates:
- User demographics and registration dates
- Subscription conversions with different patterns for each group
- Trading activity and commission revenue
- Realistic churn patterns

### Analytical Approach
1. **A/A Test Validation**: Confirmed group balance before analysis
2. **LTV Calculation**: 6-month revenue projection for each user
3. **Statistical Testing**: T-tests for significance of results
4. **Segment Analysis**: Identified high-value user characteristics


---
