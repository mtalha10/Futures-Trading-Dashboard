import streamlit as st
import pandas as pd
from datetime import datetime, time


def create_days_analyzed_card(df_grouped):
    """
    Creates a card showing the number of days being analyzed based on the applied filters.

    Args:
        df_grouped (pd.DataFrame): DataFrame containing grouped data after filters are applied
    """
    days_count = 0 if df_grouped.empty else len(df_grouped)

    st.markdown("""
    <div style="background-color:#2D3A3E; padding:15px; border-radius:10px; margin-bottom:15px">
        <h3 style="margin-top:0; color:#4ECDC4">Days Being Analyzed</h3>
        <div style="display:flex; justify-content:space-between; align-items:center">
            <div>
                <span style="font-size:28px; font-weight:bold; color:white">{}</span>
                <span style="color:#A9A9A9; margin-left:5px">days match your criteria</span>
            </div>
            <div style="font-size:24px; color:#4ECDC4">
                <i class="fas fa-calendar-alt"></i>
            </div>
        </div>
    </div>
    """.format(days_count), unsafe_allow_html=True)


def create_date_range_card(start_date, end_date):
    """
    Creates a card showing the selected date range.

    Args:
        start_date (datetime): The start date of the analysis
        end_date (datetime): The end date of the analysis
    """
    date_format = "%b %d, %Y"
    formatted_start = start_date.strftime(date_format)
    formatted_end = end_date.strftime(date_format)
    total_days = (end_date - start_date).days + 1

    st.markdown(f"""
    <div style="background-color:#2D3A3E; padding:15px; border-radius:10px; margin-bottom:15px">
        <h3 style="margin-top:0; color:#4ECDC4">Date Range</h3>
        <div style="display:flex; justify-content:space-between; align-items:center">
            <div>
                <span style="font-size:16px; color:white">{formatted_start} - {formatted_end}</span>
                <div style="color:#A9A9A9; margin-top:5px">Total period: {total_days} days</div>
            </div>
            <div style="font-size:24px; color:#4ECDC4">
                <i class="fas fa-calendar-range"></i>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_symbols_card(symbol_filter_value, category_filter_value):
    """
    Creates a card showing the selected symbols and categories.

    Args:
        symbol_filter_value (list): List of selected symbols
        category_filter_value (list): List of selected categories
    """
    symbols_text = "All" if not symbol_filter_value else ", ".join(symbol_filter_value)
    categories_text = "All" if not category_filter_value else ", ".join(category_filter_value)

    st.markdown(f"""
    <div style="background-color:#2D3A3E; padding:15px; border-radius:10px; margin-bottom:15px">
        <h3 style="margin-top:0; color:#4ECDC4">Symbols & Categories</h3>
        <div>
            <div style="margin-bottom:8px">
                <span style="color:#A9A9A9">Symbols:</span>
                <span style="color:white; margin-left:5px">{symbols_text}</span>
            </div>
            <div>
                <span style="color:#A9A9A9">Categories:</span>
                <span style="color:white; margin-left:5px">{categories_text}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_zones_card(zone1_start, zone1_duration, zone2_start, zone2_duration,
                      zone3_start, zone3_duration, zone1_type, zone2_type, zone3_type):
    """
    Creates a card showing the configured zones and their conditions.

    Args:
        zone1_start, zone2_start, zone3_start: Starting times for each zone
        zone1_duration, zone2_duration, zone3_duration: Duration of each zone
        zone1_type, zone2_type, zone3_type: Conditions applied to each zone
    """

    # Format zone times - handling time objects correctly
    def format_zone_time(hour_or_time, minute_val, duration):
        # Check if hour_or_time is a time object or an integer
        if isinstance(hour_or_time, time):
            start_hour = hour_or_time.hour
            start_minute = hour_or_time.minute
        else:
            start_hour = hour_or_time
            start_minute = minute_val

        start_time = f"{start_hour:02d}:{start_minute:02d}"
        end_hour = (start_hour + duration) % 24
        end_time = f"{end_hour:02d}:{start_minute:02d}"
        return f"{start_time} - {end_time}"

    # Get appropriate zone times
    zone1_time = format_zone_time(zone1_start, 0, zone1_duration)
    zone2_time = format_zone_time(zone2_start, 0, zone2_duration)
    zone3_time = format_zone_time(zone3_start, 30, zone3_duration)

    st.markdown(f"""
    <div style="background-color:#2D3A3E; padding:15px; border-radius:10px; margin-bottom:15px">
        <h3 style="margin-top:0; color:#4ECDC4">Trading Zones</h3>
        <table style="width:100%; color:white;">
            <tr>
                <th style="text-align:left; padding:3px; color:#A9A9A9">Zone</th>
                <th style="text-align:left; padding:3px; color:#A9A9A9">Time (UTC)</th>
                <th style="text-align:left; padding:3px; color:#A9A9A9">Condition</th>
            </tr>
            <tr>
                <td style="padding:3px">Zone 1</td>
                <td style="padding:3px">{zone1_time}</td>
                <td style="padding:3px">{zone1_type}</td>
            </tr>
            <tr>
                <td style="padding:3px">Zone 2</td>
                <td style="padding:3px">{zone2_time}</td>
                <td style="padding:3px">{zone2_type}</td>
            </tr>
            <tr>
                <td style="padding:3px">Zone 3</td>
                <td style="padding:3px">{zone3_time}</td>
                <td style="padding:3px">{zone3_type}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)


def create_stats_summary_card(retracement_df, high_prob, low_prob, bullish_bearish_summary):
    """
    Creates a card showing key statistics from the analysis.

    Args:
        retracement_df: DataFrame with retracement statistics
        high_prob: Probability of high occurring in the open
        low_prob: Probability of low occurring in the open
        bullish_bearish_summary: Summary of bullish/bearish days
    """
    # Calculate key metrics (handle None or empty dataframes)
    avg_retracement = "-"
    if retracement_df is not None and not retracement_df.empty and 'retracement_pct' in retracement_df.columns:
        avg_retracement = f"{retracement_df['retracement_pct'].mean():.2f}%"

    high_in_open = "-"
    if high_prob is not None:
        high_in_open = f"{high_prob:.2%}"

    low_in_open = "-"
    if low_prob is not None:
        low_in_open = f"{low_prob:.2%}"

    bullish_pct = "-"
    if bullish_bearish_summary is not None and not bullish_bearish_summary.empty:
        if 'day_type' in bullish_bearish_summary.columns and 'percentage' in bullish_bearish_summary.columns:
            if 'Bullish' in bullish_bearish_summary['day_type'].values:
                bullish_row = bullish_bearish_summary[bullish_bearish_summary['day_type'] == 'Bullish']
                if not bullish_row.empty:
                    bullish_pct = f"{bullish_row['percentage'].values[0]:.2%}"

    st.markdown(f"""
    <div style="background-color:#2D3A3E; padding:15px; border-radius:10px; margin-bottom:15px">
        <h3 style="margin-top:0; color:#4ECDC4">Key Statistics</h3>
        <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:10px">
            <div>
                <div style="color:#A9A9A9">High in Open</div>
                <div style="font-size:18px; font-weight:bold; color:white">{high_in_open}</div>
            </div>
            <div>
                <div style="color:#A9A9A9">Low in Open</div>
                <div style="font-size:18px; font-weight:bold; color:white">{low_in_open}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)