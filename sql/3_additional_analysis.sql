-- ============================================================
-- 3. Segment Analysis
-- Objective: Identify high-value user segments within Group B
-- ============================================================

-- SEGMENT 1: Depositors vs. Non-Depositors during trial (Group B)
WITH user_revenues AS (
    SELECT
        u.user_id,
        u.group_name,
        u.first_deposit_date,
        u.registration_date,
        COALESCE(SUM(CASE WHEN s.payment_status = 'success' THEN 10 ELSE 0 END), 0)
            AS subscription_revenue,
        COALESCE(SUM(t.commission_usd), 0)
            AS commission_revenue,
        COALESCE(SUM(CASE WHEN s.payment_status = 'success' THEN 10 ELSE 0 END), 0)
            + COALESCE(SUM(t.commission_usd), 0) AS total_ltv,
        MAX(CASE WHEN s.subscription_id IS NOT NULL THEN 1 ELSE 0 END)
            AS converted
    FROM users u
    LEFT JOIN subscriptions s
        ON u.user_id = s.user_id
        AND s.payment_date <= DATE_ADD(u.registration_date, INTERVAL 6 MONTH)
    LEFT JOIN trades t
        ON u.user_id = t.user_id
        AND t.trade_date <= DATE_ADD(u.registration_date, INTERVAL 6 MONTH)
    WHERE u.registration_date BETWEEN '2023-11-01' AND '2023-11-21'
    GROUP BY u.user_id, u.group_name, u.first_deposit_date, u.registration_date
),
deposit_during_trial AS (
    SELECT
        ur.user_id,
        ur.group_name,
        ur.total_ltv,
        ur.converted,
        CASE
            WHEN ur.first_deposit_date IS NOT NULL
             AND ur.first_deposit_date <= DATE_ADD(ur.registration_date, INTERVAL 30 DAY)
            THEN 1 ELSE 0
        END AS deposited_during_trial
    FROM user_revenues ur
    WHERE ur.group_name = 'B'
)
SELECT
    CASE deposited_during_trial WHEN 1 THEN 'Deposited during trial' ELSE 'No deposit' END
        AS segment,
    COUNT(*)                          AS users,
    AVG(converted)                    AS conversion_rate,
    AVG(total_ltv)                    AS avg_ltv,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_ltv) AS median_ltv
FROM deposit_during_trial
GROUP BY deposited_during_trial
ORDER BY deposited_during_trial DESC;

-- SEGMENT 2: Age groups × Group comparison
WITH age_segments AS (
    SELECT
        u.user_id,
        u.group_name,
        CASE
            WHEN u.age BETWEEN 18 AND 25 THEN '18-25'
            WHEN u.age BETWEEN 26 AND 35 THEN '26-35'
            ELSE '36+'
        END AS age_group,
        COALESCE(SUM(CASE WHEN s.payment_status = 'success' THEN 10 ELSE 0 END), 0)
            + COALESCE(SUM(t.commission_usd), 0) AS total_ltv,
        MAX(CASE WHEN s.subscription_id IS NOT NULL THEN 1 ELSE 0 END) AS converted
    FROM users u
    LEFT JOIN subscriptions s
        ON u.user_id = s.user_id
        AND s.payment_date <= DATE_ADD(u.registration_date, INTERVAL 6 MONTH)
    LEFT JOIN trades t
        ON u.user_id = t.user_id
        AND t.trade_date <= DATE_ADD(u.registration_date, INTERVAL 6 MONTH)
    WHERE u.registration_date BETWEEN '2023-11-01' AND '2023-11-21'
    GROUP BY u.user_id, u.group_name, u.age
)
SELECT
    age_group,
    group_name,
    COUNT(*)           AS users,
    AVG(converted)     AS conversion_rate,
    AVG(total_ltv)     AS avg_ltv
FROM age_segments
GROUP BY age_group, group_name
ORDER BY age_group, group_name;
