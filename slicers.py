# ------------------------------------------------
# -------------- IMPORTS -------------------------
#  Import necessary libraries and modules.
# ------------------------------------------------
import streamlit as st
from datetime import datetime, timedelta
from db import create_engine
from sqlalchemy import text
import pandas as pd

# ------------------------------------------------
# ------- Analysis Purpose: Date Range -----------
#  Connect to the database and fetch the minimum
#  and maximum dates from the ts_event column.
# ------------------------------------------------
@st.cache_data(show_spinner=False)
def get_date_range():
    """
    Connects to the database and fetches the minimum and maximum dates from the ts_event column.
    Update the table name 'f_ohlcv' if necessary.
    """
    engine = create_engine()
    query = text("SELECT MIN(ts_event) as min_date, MAX(ts_event) as max_date FROM f_ohlcv;")
    with engine.connect() as connection:
        result = connection.execute(query).mappings()
        row = result.fetchone()
    min_date = row["min_date"].date() if row["min_date"] else None
    max_date = row["max_date"].date() if row["max_date"] else None
    return min_date, max_date

# ------------------------------------------------
# -------- Analysis Purpose: Start Date Filter ----
#  Create a start date filter widget in the sidebar.
# ------------------------------------------------
def start_date_filter():
    """
    Creates a start date filter widget in the sidebar.
    """
    min_date, max_date = get_date_range()
    if not min_date or not max_date:
        st.sidebar.error("No date range found in the database.")
        return None
    start_date = st.sidebar.date_input(
        "Select Start Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
    return start_date

# ------------------------------------------------
# -------- Analysis Purpose: End Date Filter ------
#  Create an end date filter widget in the sidebar.
# ------------------------------------------------
def end_date_filter():
    """
    Creates an end date filter widget in the sidebar.
    """
    min_date, max_date = get_date_range()
    if not min_date or not max_date:
        st.sidebar.error("No date range found in the database.")
        return None
    end_date = st.sidebar.date_input(
        "Select End Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )
    return end_date

# ------------------------------------------------
# ------- Analysis Purpose: Grouping Filter --------
#  Create a selectbox for choosing the time grouping unit.
#  Options include: year, month, week, day, hour, minute.
# ------------------------------------------------
def grouping_filter():
    """
    Creates a selectbox in the sidebar to choose the time grouping unit.
    Options include: year, month, week, day, hour, minute.
    """
    grouping_options = ['year', 'month', 'week', 'day', 'hour', 'minute']
    grouping_choice = st.sidebar.selectbox(
        "Time Category According To Symbols",
        options=grouping_options,
        index=3  # default to 'day'
    )
    return grouping_choice

# ------------------------------------------------
# -------- Analysis Purpose: Symbol Filter --------
#  Create a text input widget for filtering by symbol.
#  Multiple symbols can be entered, separated by commas.
# ------------------------------------------------
def symbol_filter():
    """
    Creates a text input widget in the sidebar for filtering by symbol.
    Enter multiple symbols separated by commas (e.g., "6EQ4, 6EF1").
    """
    return st.sidebar.text_input("Symbol Filter (contains, comma separated)", value="")

# ------------------------------------------------
# ------- Analysis Purpose: Category Filter -------
#  Create a text input widget for filtering by category.
#  Multiple comma-separated category prefixes are supported.
# ------------------------------------------------
def category_filter():
    """
    Creates a text input widget in the sidebar for filtering by category.
    Enter multiple comma-separated category prefixes (e.g., "6E, 6F").
    The filter matches rows whose category starts with any of the given prefixes.
    """
    return st.sidebar.text_input("Category Filter 6E, ES, NQ, RT(starts with, comma separated)", value="")

# ------------------------------------------------
# -------- Analysis Purpose: Zone Filter -----------
#  Create filters for a trading zone with inputs for hour and minute.
#  The duration is fixed at 60 minutes.
# ------------------------------------------------
def zone_filter(zone_label, default_hour, default_minute, minute_min=0, minute_max=59):
    """
    Creates a filter for a trading zone in the sidebar using a number input for hour and a slider for minute.
    The user enters the start hour (0-23) and selects the start minute (from minute_min to minute_max);
    the duration is fixed at 60 minutes.
    """
    st.sidebar.subheader(zone_label)
    zone_hour = st.sidebar.number_input(
        f"{zone_label} Start Hour (0-23)",
        min_value=0,
        max_value=23,
        value=default_hour,
        step=1
    )
    zone_minute = st.sidebar.slider(
        f"{zone_label} Start Minute ({minute_min}-{minute_max})",
        min_value=minute_min,
        max_value=minute_max,
        value=default_minute,
        step=1
    )
    zone_start_time = datetime.strptime(f"{zone_hour:02d}:{zone_minute:02d}", "%H:%M").time()
    zone_duration = 60  # Fixed duration in minutes
    return zone_start_time, zone_duration

# ------------------------------------------------
# -------- Analysis Purpose: Zone Type Filter ----
#  Create a dropdown with condition options for each zone.
# ------------------------------------------------
def zone_type_filter(zone_label):
    """
    Creates a dropdown with zone condition options.
    For Zone 1 and Zone 2, the condition is based on the other zone.
    For Zone 3, the condition is based on both Zone 1 and Zone 2.
    """
    zone_condition_options = {
        "Zone 1": [
            "Above Zone 2",
            "Below Zone 2",
            "Stacked with Zone 2"
        ],
        "Zone 2": [
            "Above Zone 1",
            "Below Zone 1",
            "Stacked with Zone 1"
        ],
        "Zone 3": [
            "Above Zone 1 & Zone 2",
            "Below Zone 1 & Zone 2",
            "Stacked with Zone 1 & Zone 2"
        ]
    }
    return st.sidebar.selectbox(
        f"{zone_label} Condition",
        zone_condition_options[zone_label],
        index=0
    )

# ------------------------------------------------
# ------ Analysis Purpose: Group Symbols by Time Zone -----
#  Groups symbols by day and checks zone conditions.
#  Also filters rows by symbol and category if provided.
# ------------------------------------------------
@st.cache_data(show_spinner=False)
def group_symbols_by_time_zone(start_date, end_date, grouping,
                               zone1_start, zone2_start, zone3_start,
                               zone1_type, zone2_type, zone3_type,
                               symbol_filter_value, category_filter_value):
    """
    Groups symbols by day and checks zone conditions.
      - Zone 1: Compares with Zone 2.
      - Zone 2: Compares with Zone 1.
      - Zone 3: Compares with both Zone 1 and Zone 2.

    Also filters rows by symbol and category if provided.

    Checks three conditions for each zone:
      - "Above": the zone's max is greater than the compared zone(s).
      - "Below": the zone's max is less than the compared zone(s).
      - "Stacked": the zone's max is approximately equal (within a tolerance) to the compared zone(s).
    """
    # Compute zone end times (each zone lasts 60 minutes)
    zone1_end = (datetime.combine(datetime.today(), zone1_start) + timedelta(minutes=60)).time()
    zone2_end = (datetime.combine(datetime.today(), zone2_start) + timedelta(minutes=60)).time()
    zone3_end = (datetime.combine(datetime.today(), zone3_start) + timedelta(minutes=60)).time()

    engine = create_engine()

    # Process comma-separated filter values, converting to uppercase.
    symbol_list = [s.strip().upper() for s in symbol_filter_value.split(',') if s.strip()] \
        if symbol_filter_value.strip() != "" else []
    category_list = [s.strip().upper() for s in category_filter_value.split(',') if s.strip()] \
        if category_filter_value.strip() != "" else []

    query = f"""
    WITH zone_data AS (
        SELECT 
            DATE(ts_event) as day,
            MAX(CASE WHEN CAST(ts_event AS time) BETWEEN :zone1_start AND :zone1_end 
                     THEN high ELSE NULL END) as zone1_max,
            MAX(CASE WHEN CAST(ts_event AS time) BETWEEN :zone2_start AND :zone2_end 
                     THEN high ELSE NULL END) as zone2_max,
            MAX(CASE WHEN CAST(ts_event AS time) BETWEEN :zone3_start AND :zone3_end 
                     THEN high ELSE NULL END) as zone3_max,
            string_agg(DISTINCT symbol, ', ') as symbols
        FROM f_ohlcv
        WHERE ts_event BETWEEN :start_date AND :end_date
          AND (:symbol_filter = '' OR UPPER(symbol) = ANY(:symbol_list))
          AND (:category_filter = '' OR UPPER(category) = ANY(:category_list))
        GROUP BY day
    ),
    zone_conditions AS (
        SELECT 
            day, 
            symbols,
            zone1_max,
            zone2_max,
            zone3_max,
            CASE 
                -- Zone 1 conditions (compared with Zone 2)
                WHEN :zone1_type = 'Above Zone 2'
                     AND zone1_max > COALESCE(zone2_max, 0)
                     THEN 'Zone 1 above Zone 2'
                WHEN :zone1_type = 'Below Zone 2'
                     AND zone1_max < COALESCE(zone2_max, 999999)
                     THEN 'Zone 1 below Zone 2'
                WHEN :zone1_type = 'Stacked with Zone 2'
                     AND zone1_max IS NOT NULL AND zone2_max IS NOT NULL
                     AND ABS(zone1_max - zone2_max) < 0.1
                     THEN 'Zone 1 stacked with Zone 2'

                -- Zone 2 conditions (compared with Zone 1)
                WHEN :zone2_type = 'Above Zone 1'
                     AND zone2_max > COALESCE(zone1_max, 0)
                     THEN 'Zone 2 above Zone 1'
                WHEN :zone2_type = 'Below Zone 1'
                     AND zone2_max < COALESCE(zone1_max, 999999)
                     THEN 'Zone 2 below Zone 1'
                WHEN :zone2_type = 'Stacked with Zone 1'
                     AND zone1_max IS NOT NULL AND zone2_max IS NOT NULL
                     AND ABS(zone2_max - zone1_max) < 0.1
                     THEN 'Zone 2 stacked with Zone 1'

                -- Zone 3 conditions (compared with both Zone 1 and Zone 2)
                WHEN :zone3_type = 'Above Zone 1 & Zone 2'
                     AND zone3_max > COALESCE(zone1_max, 0)
                     AND zone3_max > COALESCE(zone2_max, 0)
                     THEN 'Zone 3 above Zone 1 & Zone 2'
                WHEN :zone3_type = 'Below Zone 1 & Zone 2'
                     AND zone3_max < COALESCE(zone1_max, 999999)
                     AND zone3_max < COALESCE(zone2_max, 999999)
                     THEN 'Zone 3 below Zone 1 & Zone 2'
                WHEN :zone3_type = 'Stacked with Zone 1 & Zone 2'
                     AND zone3_max IS NOT NULL 
                     AND zone1_max IS NOT NULL 
                     AND zone2_max IS NOT NULL
                     AND ABS(zone3_max - zone1_max) < 0.1
                     AND ABS(zone3_max - zone2_max) < 0.1
                     THEN 'Zone 3 stacked with Zone 1 & Zone 2'
                ELSE NULL
            END as zone_relationship
        FROM zone_data
    )
    SELECT 
        day, 
        symbols,
        zone1_max,
        zone2_max,
        zone3_max,
        zone_relationship
    FROM zone_conditions
    WHERE zone_relationship IS NOT NULL
    ORDER BY day;
    """

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "zone1_start": zone1_start.strftime("%H:%M:%S"),
        "zone1_end": zone1_end.strftime("%H:%M:%S"),
        "zone2_start": zone2_start.strftime("%H:%M:%S"),
        "zone2_end": zone2_end.strftime("%H:%M:%S"),
        "zone3_start": zone3_start.strftime("%H:%M:%S"),
        "zone3_end": zone3_end.strftime("%H:%M:%S"),
        "zone1_type": zone1_type,
        "zone2_type": zone2_type,
        "zone3_type": zone3_type,
        "symbol_filter": symbol_filter_value.strip(),
        "category_filter": category_filter_value.strip(),
        "symbol_list": symbol_list,
        "category_list": category_list
    }

    df = pd.read_sql_query(text(query), engine, params=params)
    return df
