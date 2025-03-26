import streamlit as st
from datetime import datetime, timedelta
from db import create_engine
from sqlalchemy import text
import pandas as pd


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


def grouping_filter():
    """
    Creates a selectbox in the sidebar to choose the time grouping unit.
    Options include: year, month, week, day, hour, minute.
    """
    grouping_options = ['year', 'month', 'week', 'day', 'hour', 'minute']
    grouping_choice = st.sidebar.selectbox(
        "Group by Time Unit",
        options=grouping_options,
        index=3  # default to 'day'
    )
    return grouping_choice


def zone_filter(zone_label, default_hour, default_minute):
    """
    Creates a filter for a trading zone in the sidebar using a number input for hour and a slider for minute.
    The user enters the start hour (0-23) and selects the start minute (0-59); the duration is fixed at 60 minutes.
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
        f"{zone_label} Start Minute (0-59)",
        min_value=0,
        max_value=59,
        value=default_minute,
        step=1
    )
    zone_start_time = datetime.strptime(f"{zone_hour:02d}:{zone_minute:02d}", "%H:%M").time()
    zone_duration = 60  # Fixed duration in minutes
    return zone_start_time, zone_duration


def zone_type_filter(zone_label):
    """
    Creates a dropdown (selectbox) for selecting the zone type condition (Above, Below, or Stacked).
    """
    return st.sidebar.selectbox(f"{zone_label} Type", ["Above", "Below", "Stacked"], index=0)


@st.cache_data(show_spinner=False)
def group_symbols_by_time_zone(start_date, end_date, grouping,
                               zone1_start, zone2_start, zone3_start,
                               zone1_type, zone2_type, zone3_type):
    """
    Groups symbols by day (or other time grouping) and assigns a zone condition for each zone.
    This query simulates computing a zone condition by simply returning the parameter values for rows
    where the ts_event time falls within the zone's window (zone window = start time to start time + 60 minutes).
    Then it filters (via HAVING) only days that match the user-selected conditions for all three zones.

    Args:
        start_date, end_date: Date filters.
        grouping: Time grouping unit (e.g., 'day').
        zoneX_start: Start time for Zone X.
        zoneX_type: Selected condition for Zone X (Above/Below/Stacked).

    Returns:
        A DataFrame with columns: day, zone1_condition, zone2_condition, zone3_condition, symbols.
    """
    # Compute zone end times by adding 60 minutes.
    zone1_end = (datetime.combine(datetime.today(), zone1_start) + timedelta(minutes=60)).time()
    zone2_end = (datetime.combine(datetime.today(), zone2_start) + timedelta(minutes=60)).time()
    zone3_end = (datetime.combine(datetime.today(), zone3_start) + timedelta(minutes=60)).time()

    engine = create_engine()
    query = f"""
        SELECT 
            DATE(ts_event) as day,
            MAX(CASE WHEN CAST(ts_event AS time) BETWEEN :zone1_start AND :zone1_end 
                     THEN :zone1_type ELSE NULL END) as zone1_condition,
            MAX(CASE WHEN CAST(ts_event AS time) BETWEEN :zone2_start AND :zone2_end 
                     THEN :zone2_type ELSE NULL END) as zone2_condition,
            MAX(CASE WHEN CAST(ts_event AS time) BETWEEN :zone3_start AND :zone3_end 
                     THEN :zone3_type ELSE NULL END) as zone3_condition,
            string_agg(DISTINCT symbol, ', ') as symbols
        FROM f_ohlcv
        WHERE ts_event BETWEEN :start_date AND :end_date
        GROUP BY day
        HAVING 
            MAX(CASE WHEN CAST(ts_event AS time) BETWEEN :zone1_start AND :zone1_end 
                     THEN :zone1_type ELSE NULL END) = :zone1_type
            AND MAX(CASE WHEN CAST(ts_event AS time) BETWEEN :zone2_start AND :zone2_end 
                     THEN :zone2_type ELSE NULL END) = :zone2_type
            AND MAX(CASE WHEN CAST(ts_event AS time) BETWEEN :zone3_start AND :zone3_end 
                     THEN :zone3_type ELSE NULL END) = :zone3_type
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
    }
    df = pd.read_sql_query(text(query), engine, params=params)
    return df
