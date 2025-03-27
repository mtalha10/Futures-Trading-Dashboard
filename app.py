import streamlit as st
from slicers import (
    start_date_filter,
    end_date_filter,
    grouping_filter,
    zone_filter,
    zone_type_filter,
    group_symbols_by_time_zone
)
from charts import plot_retracement_bar_chart, \
    plot_zone1_retracement_bar_chart  # Add this import
from analysis import get_retracement_stats, get_zone1_retracement_stats

# Define custom CSS to set the background color
custom_css = """
    <style>
        .stApp {
            background-color: #1A2526;  /* Dark navy blue background */
            color: white;              /* Optional: White text for readability */
        }
    </style>
"""

# Inject the custom CSS into the app
st.markdown(custom_css, unsafe_allow_html=True)

def main():
    st.title("Futures Trading Dashboard")

    # Sidebar: Date and grouping filters
    st.sidebar.header("Filters")
    start_date = start_date_filter()
    end_date = end_date_filter()
    grouping = grouping_filter()

    if not (start_date and end_date):
        st.error("Please select a valid date range.")
        return
    if start_date > end_date:
        st.error("Start date must be before or equal to the end date.")
        return

    # Sidebar: Zone filters
    st.sidebar.header("Zone Time Filters")
    zone1_start, zone1_duration = zone_filter("Zone 1 (e.g., 18:00)", 18, 0)
    zone2_start, zone2_duration = zone_filter("Zone 2 (e.g., 03:00)", 3, 0)
    zone3_start, zone3_duration = zone_filter("Zone 3 (e.g., 09:30)", 9, 30)

    # Sidebar: Zone type filters
    st.sidebar.header("Zone Condition Filters")
    zone1_type = zone_type_filter("Zone 1")
    zone2_type = zone_type_filter("Zone 2")
    zone3_type = zone_type_filter("Zone 3")

    # Compute grouped data based on zone conditions
    df_grouped = group_symbols_by_time_zone(
        start_date, end_date, grouping,
        zone1_start, zone2_start, zone3_start,
        zone1_type, zone2_type, zone3_type
    )

    # Create tabs
    tab1, tab2 = st.tabs(["Zone Analysis", "Retracements"])

    # Zone Analysis Tab
    with tab1:
        st.subheader("Symbols Grouped by Day and Zone")
        if not df_grouped.empty:
            st.write("**Matching Days for Conditions:**")
            st.write(f"- Zone 1: {zone1_type}")
            st.write(f"- Zone 2: {zone2_type}")
            st.write(f"- Zone 3: {zone3_type}")
            st.dataframe(df_grouped)
        else:
            st.write("No data available for the selected parameters.")

    # Retracements Tab
    # In the Retracements Tab (inside app.py)
    with tab2:
        st.subheader("Midnight Open Retracement Analysis")
        if not df_grouped.empty:
            selected_days = df_grouped['day'].tolist()
            retracement_df = get_retracement_stats(selected_days)
            plot_retracement_bar_chart(retracement_df)
        else:
            st.write("No days meet the selected zone conditions.")

        st.subheader("Zone 1 Retracement after Zone 3 Formation")
        if not df_grouped.empty:
            selected_days = df_grouped['day'].tolist()
            zone1_retracement_df = get_zone1_retracement_stats(selected_days)
            plot_zone1_retracement_bar_chart(zone1_retracement_df)
        else:
            st.write("No days meet the selected zone conditions.")


if __name__ == "__main__":
    main()