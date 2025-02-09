-- BigQuery SQL: Daily & Monthly Retention from Firebase events

WITH 
-- 1. Filter and normalize all events from Firebase.
--    Convert the event_timestamp (in microseconds) to a local DATE.
filtered_events AS (
  SELECT
    user_pseudo_id AS user_id,
    event_name,
    DATE(
      DATETIME_ADD(
        DATETIME(TIMESTAMP_MICROS(event_timestamp), "GMT"),
        INTERVAL device.time_zone_offset_seconds SECOND
      )
    ) AS activity_date
  FROM project.analytics_XXXXXXXXX.events_*
  -- Limit the query to events in the desired date range.
  -- For example, all events in 2024:
  WHERE _TABLE_SUFFIX BETWEEN '20240101' AND '20241231'
),

-- 2. Determine each user’s signup date.
--    Here we assume that the Firebase "first_open" event indicates signup.
signups AS (
  SELECT 
    user_id,
    MIN(activity_date) AS signup_date
  FROM filtered_events
  WHERE event_name = 'first_open'
  GROUP BY user_id
),

-- 3. Count new users (signups) per signup date.
active_user_count AS (
  SELECT 
    signup_date,
    COUNT(DISTINCT user_id) AS users_count
  FROM signups
  GROUP BY signup_date
),

-- 4. Daily retention: For each signup, count subsequent activity in the next 30 days.
daily_retention AS (
  SELECT 
    s.signup_date,
    DATE_DIFF(a.activity_date, s.signup_date, DAY) AS period,
    acu.users_count AS new_users,
    COUNT(DISTINCT a.user_id) AS retained_users,
    SAFE_DIVIDE(COUNT(DISTINCT a.user_id), acu.users_count) AS retention,
    'daily' AS retention_type
  FROM signups s
  LEFT JOIN filtered_events a
    ON s.user_id = a.user_id
    AND a.activity_date > s.signup_date
    AND a.activity_date <= DATE_ADD(s.signup_date, INTERVAL 30 DAY)
  LEFT JOIN active_user_count acu
    ON s.signup_date = acu.signup_date
  GROUP BY s.signup_date, period, acu.users_count
),

-- 5. Monthly retention: For each signup, count subsequent activity in the next 12 months.
monthly_retention AS (
  SELECT 
    s.signup_date,
    DATE_DIFF(a.activity_date, s.signup_date, MONTH) AS period,
    acu.users_count AS new_users,
    COUNT(DISTINCT a.user_id) AS retained_users,
    SAFE_DIVIDE(COUNT(DISTINCT a.user_id), acu.users_count) AS retention,
    'monthly' AS retention_type
  FROM signups s
  LEFT JOIN filtered_events a
    ON s.user_id = a.user_id
    AND a.activity_date > s.signup_date
    AND a.activity_date <= DATE_ADD(s.signup_date, INTERVAL 12 MONTH)
  LEFT JOIN active_user_count acu
    ON s.signup_date = acu.signup_date
  GROUP BY s.signup_date, period, acu.users_count
)

-- 6. Merge the daily and monthly retention results.
SELECT * FROM daily_retention
UNION ALL
SELECT * FROM monthly_retention
ORDER BY signup_date, retention_type, period;