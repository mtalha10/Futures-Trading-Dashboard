# data_utils.py
import pandas as pd
import sqlalchemy
import streamlit as st
from datetime import time, datetime, timedelta
from db import engine  # Import engine from db.py


@st.cache_data
def load_categories():
    """
    Fetches unique category values from the category column in public.f_ohlcv.
    Returns a sorted list of categories.
    """
    try:
        query = "SELECT DISTINCT category FROM public.f_ohlcv WHERE category IS NOT NULL"
        df = pd.read_sql(query, engine)
        # Sort categories in ascending order
        return sorted(df["category"].tolist())
    except Exception as e:
        print(f"Error loading categories: {e}")
        return []


@st.cache_data
def load_symbols(category=None):
    """
    Fetches unique symbol values from the symbol column in public.f_ohlcv.
    If a category is provided, filters symbols by that category.
    Returns a sorted list of symbols.
    """
    try:
        query = "SELECT DISTINCT symbol FROM public.f_ohlcv WHERE symbol IS NOT NULL"
        params = {}

        if category:
            query += " AND category = :category"
            params["category"] = category

        df = pd.read_sql(sqlalchemy.text(query), engine, params=params)
        # Sort symbols in ascending order
        return sorted(df["symbol"].tolist())
    except Exception as e:
        print(f"Error loading symbols: {e}")
        return []


@st.cache_data
def get_date_range():
    """
    Fetches the minimum and maximum dates from the ts_event column in public.f_ohlcv.
    Returns a tuple of (min_date, max_date) as datetime.date objects.
    """
    try:
        query = "SELECT MIN(DATE(ts_event)) AS min_date, MAX(DATE(ts_event)) AS max_date FROM public.f_ohlcv"
        with engine.connect() as conn:
            result = pd.read_sql(sqlalchemy.text(query), conn)
        min_date = result["min_date"].iloc[0]
        max_date = result["max_date"].iloc[0]
        # Convert to datetime.date if they are not already
        if isinstance(min_date, str):
            min_date = datetime.strptime(min_date, "%Y-%m-%d").date()
        if isinstance(max_date, str):
            max_date = datetime.strptime(max_date, "%Y-%m-%d").date()
        return min_date, max_date
    except Exception as e:
        print(f"Error fetching date range: {e}")
        # Fallback to a reasonable default if the query fails
        return datetime(2020, 1, 1).date(), datetime(2023, 12, 31).date()


@st.cache_data(ttl=600)
def load_data(category, symbol, start_date=None, end_date=None):
    """
    Loads OHLCV data from the public.f_ohlcv table for the specified category, symbol, and date range.

    Args:
        category (str): The category to filter by (e.g., '6E', 'GC')
        symbol (str): The specific symbol to filter by
        start_date (datetime.date, optional): Start date for filtering
        end_date (datetime.date, optional): End date for filtering

    Returns:
        pd.DataFrame: DataFrame containing the filtered OHLCV data
    """
    try:
        # Base query, updated to filter by category and symbol
        query = """
            SELECT ts_event AS ts_est, open, high, low, close, volume, instrument_id, 
                   hour AS hour_est, minute AS minute_est, category, symbol
            FROM public.f_ohlcv
            WHERE category = :category AND symbol = :symbol
        """
        params = {
            "category": category,
            "symbol": symbol
        }

        # Add date range filter if dates are provided
        if start_date and end_date:
            query += " AND DATE(ts_event) BETWEEN :start_date AND :end_date"
            params["start_date"] = start_date
            params["end_date"] = end_date
        elif start_date:
            query += " AND DATE(ts_event) >= :start_date"
            params["start_date"] = start_date
        elif end_date:
            query += " AND DATE(ts_event) <= :end_date"
            params["end_date"] = end_date

        # Ensure data is sorted by ts_est (ts_event) in ascending order
        query += " ORDER BY ts_event ASC"

        with engine.connect() as conn:
            df = pd.read_sql(sqlalchemy.text(query), conn, params=params, parse_dates=["ts_est"])
        return df
    except Exception as e:
        print(f"Error loading data for category {category}, symbol {symbol}: {e}")
        return pd.DataFrame()


def filter_zones(df, first_minutes_asia, first_minutes_london, first_minutes_ny, zone_opening_hours=None):
    """
    Filters the dataframe rows that fall within the first X minutes of each market zone,
    starting at the specified opening hour for each zone.

    Args:
        df (pd.DataFrame): Input DataFrame with OHLCV data
        first_minutes_asia (int): First X minutes for Asia zone
        first_minutes_london (int): First X minutes for London zone
        first_minutes_ny (int): First X minutes for New York zone
        zone_opening_hours (dict, optional): Dictionary mapping zones to their opening hours in EST
                                            (e.g., {"Asia": 19, "London": 3, "New York": 9})

    Returns:
        pd.DataFrame: Filtered DataFrame with an additional "Zone" column
    """
    if df.empty:
        return pd.DataFrame(columns=df.columns.tolist() + ["Zone"])

    # Default opening hours in EST if not provided
    if zone_opening_hours is None:
        zone_opening_hours = {
            "Asia": 19,  # 9:00 AM JST = 7:00 PM EST previous day
            "London": 3,  # 8:00 AM GMT = 3:00 AM EST
            "New York": 9  # 9:30 AM EST
        }

    # Define minute ranges for each zone
    zone_minutes = {
        "Asia": first_minutes_asia,
        "London": first_minutes_london,
        "New York": first_minutes_ny
    }

    # Adjust for New York's 9:30 AM EST start
    zone_start_minutes = {
        "Asia": 0,
        "London": 0,
        "New York": 30 if zone_opening_hours["New York"] == 9 else 0  # 9:30 AM EST for NY
    }

    filtered_dfs = []
    for zone, opening_hour in zone_opening_hours.items():
        minutes = zone_minutes[zone]
        start_minute = zone_start_minutes.get(zone, 0)

        # Calculate the end time for filtering
        start_time = datetime.strptime(f"{opening_hour:02d}:{start_minute:02d}", "%H:%M").time()
        end_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=minutes)).time()
        end_hour = end_time.hour
        end_minute = end_time.minute

        # Handle cases where the time window crosses midnight
        if end_hour < opening_hour or (end_hour == opening_hour and end_minute <= start_minute):
            # Time window crosses midnight
            zone_df = df[
                (
                    # Before midnight
                    (
                        (df["hour_est"] == opening_hour) &
                        (df["minute_est"] >= start_minute)
                    ) |
                    # After midnight
                    (
                        (df["hour_est"] < end_hour) |
                        ((df["hour_est"] == end_hour) & (df["minute_est"] < end_minute))
                    )
                )
            ]
        else:
            # Time window within the same day
            zone_df = df[
                (
                    (df["hour_est"] == opening_hour) &
                    (df["minute_est"] >= start_minute) &
                    (
                        (df["hour_est"] < end_hour) |
                        ((df["hour_est"] == end_hour) & (df["minute_est"] < end_minute))
                    )
                ) |
                (
                    (df["hour_est"] > opening_hour) &
                    (df["hour_est"] < end_hour)
                ) |
                (
                    (df["hour_est"] == end_hour) &
                    (df["minute_est"] < end_minute)
                )
            ]

        if not zone_df.empty:
            zone_df = zone_df.copy()
            zone_df["Zone"] = zone
            filtered_dfs.append(zone_df)

    if filtered_dfs:
        new_df = pd.concat(filtered_dfs, ignore_index=True)
        # Sort the final DataFrame by ts_est in ascending order
        new_df.sort_values("ts_est", inplace=True)
        return new_df
    else:
        return pd.DataFrame(columns=df.columns.tolist() + ["Zone"])