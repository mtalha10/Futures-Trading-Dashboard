# ------------------------------------------------
# -------------- Analysis Module -----------------
#   This module calculates various market statistics
#   using SQL queries and returns the results as DataFrames.
# ------------------------------------------------

import streamlit as st
from datetime import datetime, timedelta
from db import create_engine
from sqlalchemy import text
import pandas as pd

# ------------------------------------------------
# -------- Analysis Purpose: Retracement Stats ----
#  Calculate retracement statistics for days meeting zone conditions.
#  Returns a DataFrame with bucket numbers (-1 for no retracement,
#  0-15 for time buckets) and counts.
# ------------------------------------------------
@st.cache_data(show_spinner=False)
def get_retracement_stats(selected_days):
    """
    Calculate retracement statistics for days meeting zone conditions.
    Returns a DataFrame with bucket numbers (-1 for no retracement, 0-15 for time buckets) and counts.
    """
    engine = create_engine()
    query = text("""
    WITH midnight_opens AS (
        SELECT DATE(ts_event) AS day, open AS midnight_open
        FROM f_ohlcv
        WHERE hour = 0 AND minute = 0 AND DATE(ts_event) IN :selected_days
    ),
    first_retracements AS (
        SELECT mo.day, MIN(f.ts_event) AS first_retracement_time
        FROM midnight_opens mo
        LEFT JOIN f_ohlcv f ON DATE(f.ts_event) = mo.day
            AND f.hour >= 8 AND f.hour <= 15
            AND f.low <= mo.midnight_open AND f.high >= mo.midnight_open
        GROUP BY mo.day
    ),
    bucketed AS (
        SELECT
            fr.day,
            CASE
                WHEN fr.first_retracement_time IS NOT NULL THEN
                    (EXTRACT(HOUR FROM fr.first_retracement_time) - 8) * 2 + 
                    FLOOR(EXTRACT(MINUTE FROM fr.first_retracement_time) / 30)
                ELSE -1
            END AS bucket
        FROM first_retracements fr
    )
    SELECT bucket, COUNT(*) AS count
    FROM bucketed
    GROUP BY bucket
    ORDER BY bucket
    """)
    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection, params={"selected_days": tuple(selected_days)})
    return df

# ------------------------------------------------
# -------- Analysis Purpose: Time Bucket Labels ---
#  Generate labels for 30-minute buckets from 08:00 to 16:00.
#  Returns a list of strings, e.g., ['08:00-08:30', ..., '15:30-16:00'].
# ------------------------------------------------
def get_time_bucket_labels():
    """
    Generate labels for 30-minute buckets from 08:00 to 16:00.
    Returns a list of strings, e.g., ['08:00-08:30', ..., '15:30-16:00'].
    """
    labels = []
    for hour in range(8, 16):
        for minute in [0, 30]:
            start_time = f"{hour:02d}:{minute:02d}"
            end_hour = hour if minute == 0 else hour + 1
            end_minute = 30 if minute == 0 else 0
            end_time = f"{end_hour:02d}:{end_minute:02d}"
            labels.append(f"{start_time}-{end_time}")
    return labels

# ------------------------------------------------
# -------- Analysis Purpose: Zone 1 Retracement Stats ---
#  Calculate retracement statistics for days where price retraced
#  to Zone 1 after Zone 3 is fully formed.
#  Returns a DataFrame with bucket numbers (bucket >= 0 for a retracement; -1 for no retracement)
#  and counts.
# ------------------------------------------------
@st.cache_data(show_spinner=False)
def get_zone1_retracement_stats(selected_days):
    """
    Calculate retracement statistics for days where price retraced to Zone 1 (e.g., 18:00-18:05 price)
    after Zone 3 is fully formed (e.g., 09:30-09:35).
    Returns a DataFrame with bucket numbers (bucket >= 0 for a retracement; -1 for no retracement)
    and counts.
    """
    engine = create_engine()
    query = text("""
    WITH zone1_prices AS (
        SELECT DATE(ts_event) AS day,
               MIN(open) AS zone1_price
        FROM f_ohlcv
        WHERE hour = 18 
          AND minute BETWEEN 0 AND 5
          AND DATE(ts_event) IN :selected_days
        GROUP BY DATE(ts_event)
    ),
    zone3_formed AS (
        SELECT DATE(ts_event) AS day,
               MAX(ts_event) AS zone3_end_time
        FROM f_ohlcv
        WHERE hour = 9 
          AND minute BETWEEN 30 AND 35
          AND DATE(ts_event) IN :selected_days
        GROUP BY DATE(ts_event)
    ),
    first_zone1_retracements AS (
        SELECT z3.day, MIN(f.ts_event) AS first_retracement_time
        FROM zone3_formed z3
        JOIN f_ohlcv f ON DATE(f.ts_event) = z3.day
           AND f.ts_event > z3.zone3_end_time
           AND f.ts_event < DATE_TRUNC('day', z3.zone3_end_time) + INTERVAL '16 hours'
        JOIN zone1_prices z1 ON z1.day = z3.day
        WHERE f.low <= z1.zone1_price AND f.high >= z1.zone1_price
        GROUP BY z3.day
    ),
    bucketed AS (
        SELECT
            z3.day,
            CASE
                WHEN fzr.first_retracement_time IS NOT NULL THEN
                    -- Calculate the bucket based on 30-minute intervals from Zone 3 end time
                    FLOOR(EXTRACT(EPOCH FROM (fzr.first_retracement_time - z3.zone3_end_time)) / 1800)
                ELSE -1
            END AS bucket
        FROM zone3_formed z3
        LEFT JOIN first_zone1_retracements fzr ON fzr.day = z3.day
    )
    SELECT bucket, COUNT(*) AS count
    FROM bucketed
    GROUP BY bucket
    ORDER BY bucket
    """)
    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection, params={"selected_days": tuple(selected_days)})
    return df

# ------------------------------------------------
# -------- Analysis Purpose: Zone 1 Time Bucket Labels ---
#  Generate labels for 30-minute buckets starting from Zone 3 end time
#  (assumed 09:35) until the end of day at 16:00.
#  Returns a list of strings, e.g., ['09:35-10:05', '10:05-10:35', ...].
# ------------------------------------------------
def get_zone1_time_bucket_labels():
    """
    Generate labels for 30-minute buckets starting from Zone 3 end time (assumed 09:35)
    until end of day at 16:00.
    Returns a list of strings, e.g., ['09:35-10:05', '10:05-10:35', ...].
    """
    labels = []
    start = datetime.strptime("09:35", "%H:%M")
    end = datetime.strptime("16:00", "%H:%M")
    current = start
    while current < end:
        bucket_start = current.strftime("%H:%M")
        current += timedelta(minutes=30)
        bucket_end = current.strftime("%H:%M")
        labels.append(f"{bucket_start}-{bucket_end}")
    return labels

# ------------------------------------------------
# -------- Analysis Purpose: High in Open Probability ---
#  Calculate the probability of the high of day occurring during market open.
# ------------------------------------------------
@st.cache_data(show_spinner=False)
def get_high_in_open_probability(selected_days):
    query = text("""
    WITH day_highs AS (
        SELECT DATE(ts_event) AS day, MAX(high) AS day_high
        FROM f_ohlcv
        WHERE DATE(ts_event) IN :selected_days
        AND hour >= 9 AND hour <= 15
        GROUP BY DATE(ts_event)
    )
    SELECT COUNT(*) FROM day_highs dh
    WHERE EXISTS (
        SELECT 1
        FROM f_ohlcv f
        WHERE DATE(f.ts_event) = dh.day
        AND f.hour = 9
        AND f.high = dh.day_high
    )
    """)
    with create_engine().connect() as connection:
        result = connection.execute(query, {"selected_days": tuple(selected_days)}).scalar()
    total_days = len(selected_days)
    return result / total_days if total_days > 0 else 0

# ------------------------------------------------
# -------- Analysis Purpose: Low in Open Probability ----
#  Calculate the probability of the low of day occurring during market open.
# ------------------------------------------------
@st.cache_data(show_spinner=False)
def get_low_in_open_probability(selected_days):
    query = text("""
    WITH day_lows AS (
        SELECT DATE(ts_event) AS day, MIN(low) AS day_low
        FROM f_ohlcv
        WHERE DATE(ts_event) IN :selected_days
        AND hour >= 9 AND hour <= 15
        GROUP BY DATE(ts_event)
    )
    SELECT COUNT(*) FROM day_lows dl
    WHERE EXISTS (
        SELECT 1
        FROM f_ohlcv f
        WHERE DATE(f.ts_event) = dl.day
        AND f.hour = 9
        AND f.low = dl.day_low
    )
    """)
    with create_engine().connect() as connection:
        result = connection.execute(query, {"selected_days": tuple(selected_days)}).scalar()
    total_days = len(selected_days)
    return result / total_days if total_days > 0 else 0

# ------------------------------------------------
# -------- Analysis Purpose: High Distribution ----
#  Compute the time distribution of the high of day
#  across 48 time buckets covering the entire day (00:00 to 24:00),
#  with each bucket representing a 30-minute interval.
# ------------------------------------------------
@st.cache_data(show_spinner=False)
def get_high_distribution(selected_days):
    query = text("""
    WITH day_highs AS (
        SELECT DATE(ts_event) AS day, MAX(high) AS day_high
        FROM f_ohlcv
        WHERE DATE(ts_event) IN :selected_days
        GROUP BY DATE(ts_event)
    ),
    first_high_times AS (
        SELECT dh.day, MIN(f.ts_event) AS first_high_time
        FROM day_highs dh
        JOIN f_ohlcv f 
            ON DATE(f.ts_event) = dh.day 
            AND f.high = dh.day_high
        GROUP BY dh.day
    ),
    first_high_details AS (
        SELECT EXTRACT(HOUR FROM first_high_time) AS hour, 
               EXTRACT(MINUTE FROM first_high_time) AS minute
        FROM first_high_times
    )
    SELECT FLOOR((hour * 60 + minute) / 30) AS bucket, COUNT(*) AS count
    FROM first_high_details
    GROUP BY bucket
    ORDER BY bucket
    """)
    with create_engine().connect() as connection:
        df = pd.read_sql_query(query, connection, params={"selected_days": tuple(selected_days)})
    # Ensure all buckets (0-47) are present even if count is 0
    all_buckets = pd.DataFrame({'bucket': range(48)})
    df = all_buckets.merge(df, on='bucket', how='left').fillna({'count': 0})
    return df


# ------------------------------------------------
# -------- Analysis Purpose: Low Distribution -----
#  Compute the time distribution of the low of day
#  across 48 time buckets covering the entire day (00:00 to 24:00),
#  with each bucket representing a 30-minute interval.
# ------------------------------------------------
@st.cache_data(show_spinner=False)
def get_low_distribution(selected_days):
    query = text("""
    WITH day_lows AS (
        SELECT DATE(ts_event) AS day, MIN(low) AS day_low
        FROM f_ohlcv
        WHERE DATE(ts_event) IN :selected_days
        GROUP BY DATE(ts_event)
    ),
    first_low_times AS (
        SELECT dl.day, MIN(f.ts_event) AS first_low_time
        FROM day_lows dl
        JOIN f_ohlcv f ON DATE(f.ts_event) = dl.day AND f.low = dl.day_low
        GROUP BY dl.day
    ),
    first_low_details AS (
        SELECT EXTRACT(HOUR FROM first_low_time) AS hour, 
               EXTRACT(MINUTE FROM first_low_time) AS minute
        FROM first_low_times
    )
    SELECT FLOOR((hour * 60 + minute) / 30) AS bucket, COUNT(*) AS count
    FROM first_low_details
    GROUP BY bucket
    ORDER BY bucket
    """)
    with create_engine().connect() as connection:
        df = pd.read_sql_query(query, connection, params={"selected_days": tuple(selected_days)})
    # Ensure all buckets (0-47) are present even if count is 0
    all_buckets = pd.DataFrame({'bucket': range(48)})
    df = all_buckets.merge(df, on='bucket', how='left').fillna({'count': 0})
    return df


# ------------------------------------------------
# -------- Analysis Purpose: Bullish/Bearish Stats ---
#  Calculate the number of bullish and bearish days from the given set of days.
#  Returns a summary DataFrame with counts and percentages,
#  along with a daily breakdown of bullish/bearish status.
# ------------------------------------------------
@st.cache_data(show_spinner=False)
def get_bullish_bearish_stats(selected_days):
    """
    Calculate the number of bullish and bearish days from the given set of days.

    Returns:
    - DataFrame with bullish/bearish counts and probabilities
    - Dataframe with daily bullish/bearish status
    """
    engine = create_engine()
    query = text("""
    WITH daily_ohlc AS (
        SELECT 
            DATE(ts_event) AS day,
            first_value(open) OVER (PARTITION BY DATE(ts_event) ORDER BY ts_event) AS day_open,
            last_value(close) OVER (PARTITION BY DATE(ts_event) ORDER BY ts_event) AS day_close
        FROM f_ohlcv
        WHERE DATE(ts_event) IN :selected_days
        AND hour = 9 AND minute = 30  -- First market candle
    ),
    day_types AS (
        SELECT 
            day,
            CASE 
                WHEN day_close > day_open THEN 'Bullish'
                WHEN day_close < day_open THEN 'Bearish'
                ELSE 'Neutral'
            END AS day_type
        FROM daily_ohlc
    )
    SELECT 
        day_type, 
        COUNT(*) AS count,
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM day_types) AS percentage
    FROM day_types
    GROUP BY day_type
    ORDER BY count DESC
    """)

    daily_type_query = text("""
    WITH daily_ohlc AS (
        SELECT 
            DATE(ts_event) AS day,
            first_value(open) OVER (PARTITION BY DATE(ts_event) ORDER BY ts_event) AS day_open,
            last_value(close) OVER (PARTITION BY DATE(ts_event) ORDER BY ts_event) AS day_close
        FROM f_ohlcv
        WHERE DATE(ts_event) IN :selected_days
        AND hour = 9 AND minute = 30  -- First market candle
    ),
    day_types AS (
        SELECT 
            day,
            CASE 
                WHEN day_close > day_open THEN 'Bullish'
                WHEN day_close < day_open THEN 'Bearish'
                ELSE 'Neutral'
            END AS day_type
        FROM daily_ohlc
    )
    SELECT 
        day,
        day_type
    FROM day_types
    ORDER BY day
    """)

    with engine.connect() as connection:
        # Get summary statistics
        summary_df = pd.read_sql_query(query, connection, params={"selected_days": tuple(selected_days)})

        # Get daily types
        daily_type_df = pd.read_sql_query(daily_type_query, connection, params={"selected_days": tuple(selected_days)})

    return summary_df, daily_type_df
