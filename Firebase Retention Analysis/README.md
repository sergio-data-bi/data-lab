# Firebase Retention Analysis

## Overview
This repository contains a **BigQuery SQL script** to analyze **daily and monthly user retention** using Firebase Analytics event data. The query helps measure **user engagement and retention trends** for mobile applications.

Leveraging **BigQuery’s powerful querying capabilities**, this script processes **raw Firebase event data**, normalizes timestamps, and calculates **cohort-based retention metrics**.

## Features
- **Daily Retention**: Tracks user activity for **30 days** post-signup.
- **Monthly Retention**: Tracks user activity for **12 months** post-signup.
- **First Open Event Detection**: Identifies new users based on their first interaction.
- **Time Zone Adjustment**: Converts `event_timestamp` to **local time** using `device.time_zone_offset_seconds`.
- **Firebase A/B Testing Compatibility**: Works with **BigQuery-integrated Firebase experiments**.

## Prerequisites
- **Google Cloud Platform (GCP)** with **BigQuery** access.
- **Firebase Analytics raw events** exported to BigQuery (`events_*` tables).
- Ensure the dataset includes:
  - `event_timestamp`
  - `event_name`
  - `user_pseudo_id`
  - `device.time_zone_offset_seconds`

## Files
This repository contains the following files:

| File Name                         | Description |
|------------------------------------|-------------|
| **[`retention_analysis.sql`](retention_analysis.sql)** | SQL query to compute **daily and monthly retention**. |

## Usage
1. **Update dataset reference**: Replace `project.analytics_XXXXXXXXX.events_*` with your actual BigQuery dataset.
2. **Modify `_TABLE_SUFFIX`**: Adjust the query to filter events for the desired date range.
3. **Run the query**: Execute the SQL script in **Google BigQuery**.

## Sample Output
| signup_date | period | new_users | retained_users | retention | retention_type |
|-------------|--------|-----------|----------------|-----------|----------------|
| 2023-01-16  | 1     | 100       | 34             | 0.340000  | daily          |
| 2023-01-16  | 7     | 100       | 20             | 0.200000  | daily          |
| 2023-01-16  | 6     | 28        | 12             | 0.428571  | monthly        |
| 2023-01-16  | 10    | 28        | 9              | 0.321429  | monthly        |

- **Working with Raw Firebase Data**:
  - **Events are stored across multiple tables** (`events_YYYYMMDD`).
  - Use `_TABLE_SUFFIX` for **efficient date filtering**.
  - Convert `event_timestamp` using `TIMESTAMP_MICROS()` and `DATETIME_ADD()` for local time.