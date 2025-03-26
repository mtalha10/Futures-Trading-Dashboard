import streamlit as st
from slicers import (
    start_date_filter,
    end_date_filter,
    grouping_filter,
    zone_filter,
    zone_type_filter,
    group_symbols_by_time_zone
)


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

    st.write(f"**Selected Date Range:** {start_date} to {end_date}")
    st.write(f"**Grouping By:** {grouping}")

    # Sidebar: Zone filters (hour and minute inputs) for each zone
    st.sidebar.header("Zone Time Filters")
    zone1_start, zone1_duration = zone_filter("Zone 1 (e.g., 18:00)", 18, 0)
    zone2_start, zone2_duration = zone_filter("Zone 2 (e.g., 03:00)", 3, 0)
    zone3_start, zone3_duration = zone_filter("Zone 3 (e.g., 09:30)", 9, 30)

    st.subheader("Zone Configurations")
    st.write(f"**Zone 1:** Start at {zone1_start}, Duration: {zone1_duration} minutes")
    st.write(f"**Zone 2:** Start at {zone2_start}, Duration: {zone2_duration} minutes")
    st.write(f"**Zone 3:** Start at {zone3_start}, Duration: {zone3_duration} minutes")

    # Sidebar: Zone type (Above / Below / Stacked) filters
    st.sidebar.header("Zone Condition Filters")
    zone1_type = zone_type_filter("Zone 1")
    zone2_type = zone_type_filter("Zone 2")
    zone3_type = zone_type_filter("Zone 3")

    st.write("**Selected Zone Conditions:**")
    st.write(f"Zone 1: {zone1_type}")
    st.write(f"Zone 2: {zone2_type}")
    st.write(f"Zone 3: {zone3_type}")

    # Analyze and display days that match the selected zone conditions
    st.subheader("Symbols Grouped by Day and Zone")
    df_grouped = group_symbols_by_time_zone(
        start_date, end_date, grouping,
        zone1_start, zone2_start, zone3_start,
        zone1_type, zone2_type, zone3_type
    )
    if not df_grouped.empty:
        st.dataframe(df_grouped)
    else:
        st.write("No data available for the selected parameters.")


if __name__ == "__main__":
    main()
