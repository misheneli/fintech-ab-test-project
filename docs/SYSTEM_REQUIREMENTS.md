
---

## 1. Business Requirements

### BR-1: Experiment Validity
The system must ensure statistical validity of A/B test results before 
any business decision is made. This includes:
- Group balance verification (A/A test)
- Normality checks before selecting statistical test
- Effect size measurement alongside p-values

### BR-2: LTV Accuracy
LTV calculation must capture all revenue sources:
- Subscription payments ($10/month per payment)
- Trading commission revenue
- 6-month observation window

---

## 2. Functional Requirements

### FR-1: Data Generation
**Input:** n_users (int), seed (int), conversion rates (float)  
**Output:** users.csv, subscriptions.csv, trades.csv  
**Acceptance criteria:**
- No duplicates in user_id
- All payment dates > registration date
- 50/50 group split (±5%)

### FR-2: A/A Test Validation
**Input:** users_df  
**Output:** balance report (p-values for age, balance, deposit rate)  
**Acceptance criteria:** All p-values > 0.05 before proceeding

### FR-3: LTV Calculation
LTV = Subscription Revenue + Commission Revenue  
**Acceptance criteria:** No null LTV values (fill with 0 for non-payers)

### FR-4: Statistical Testing
**Required outputs:**
- t-statistic and p-value
- Cohen's d effect size
- 95% confidence interval for difference
- Normality check (Shapiro-Wilk)

### FR-5: Segment Analysis
Segment by: age group, deposit behavior, balance tier  
**Acceptance criteria:** Each segment has n ≥ 30 for valid statistics

---

## 3. Non-Functional Requirements

| ID | Requirement | Metric |
|----|------------|--------|
| NFR-1 | Performance | Full analysis < 60 seconds |
| NFR-2 | Reproducibility | Same results with same seed |
| NFR-3 | Code quality | Test coverage ≥ 80% |
| NFR-4 | Documentation | All public functions documented |

---

## 4. Data Model

### users
| Column | Type | Nullable | Description |
|--------|------|---------|-------------|
| user_id | INT | No | Primary key |
| registration_date | DATE | No | Date of signup |
| group_name | VARCHAR(1) | No | 'A' or 'B' |
| age | INT | No | Age 18-80 |
| initial_balance_usd | FLOAT | No | Starting balance |
| first_deposit_date | DATE | Yes | NULL if no deposit |

### subscriptions
| Column | Type | Nullable | Description |
|--------|------|---------|-------------|
| subscription_id | INT | No | Primary key |
| user_id | INT | No | FK → users |
| payment_date | DATE | No | Payment date |
| payment_status | VARCHAR | No | 'success' |

### trades
| Column | Type | Nullable | Description |
|--------|------|---------|-------------|
| user_id | INT | No | FK → users |
| trade_date | DATE | No | Trade date |
| commission_usd | FLOAT | No | Commission amount |
