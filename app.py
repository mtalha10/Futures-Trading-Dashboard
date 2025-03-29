# ------------------------------------------------
# -------------- IMPORTS & CUSTOM CSS ------------
# ------------------------------------------------
import streamlit as st
from slicers import (
    start_date_filter,
    end_date_filter,
    grouping_filter,
    zone_filter,
    zone_type_filter,
    group_symbols_by_time_zone, symbol_filter, category_filter
)
from charts import (
    plot_retracement_bar_chart,
    plot_zone1_retracement_bar_chart,
    plot_high_in_open_probability,
    plot_high_distribution,
    plot_low_in_open_probability,
    plot_low_distribution,
    plot_bullish_bearish_probability
)
from analysis import (
    get_retracement_stats,
    get_zone1_retracement_stats,
    get_high_in_open_probability,
    get_high_distribution,
    get_low_in_open_probability,
    get_low_distribution,
    get_bullish_bearish_stats
)
from cards import (
    create_days_analyzed_card,
    create_date_range_card,
    create_symbols_card,
    create_zones_card,
    create_stats_summary_card
)

# ------------------------------------------------
# --------- CUSTOM CSS FOR APP STYLING ----------
# ------------------------------------------------
custom_css = """
    <style>
        .stApp {
            background-color: #1A2526;  /* Dark navy blue background */
            color: white;              /* White text for readability */
        }
        .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        /* Add Font Awesome for icons */
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
    </style>
"""
# Inject the custom CSS into the app
st.markdown(custom_css, unsafe_allow_html=True)


# ------------------------------------------------
# --------------------- MAIN ---------------------
#  The main function defines the layout and behavior
#  of the Futures Trading Dashboard.
# ------------------------------------------------
def main():
    st.title("Futures Trading Dashboard")

    # ------------------------------------------------
    # -------- Sidebar: Date, Symbol & Grouping Filters --------
    # ------------------------------------------------
    st.sidebar.header("Filters")
    start_date = start_date_filter()
    end_date = end_date_filter()
    category_filter_value = category_filter()
    symbol_filter_value = symbol_filter()
    grouping = grouping_filter()

    # Validate date range
    if not (start_date and end_date):
        st.error("Please select a valid date range.")
        return
    if start_date > end_date:
        st.error("Start date must be before or equal to the end date.")
        return

    # ------------------------------------------------
    # -------- Sidebar: Zone Time Filters ------------
    # ------------------------------------------------
    st.sidebar.header("Zone Time Filters")
    zone1_start, zone1_duration = zone_filter("Zone 1 (e.g., 18:00)", 18, 0)
    zone2_start, zone2_duration = zone_filter("Zone 2 (e.g., 03:00)", 3, 0)
    zone3_start, zone3_duration = zone_filter("Zone 3 (e.g., 09:30)", 9, 30, minute_min=30)

    # ------------------------------------------------
    # ------- Sidebar: Zone Condition Filters --------
    # ------------------------------------------------
    st.sidebar.header("Zone Condition Filters")
    zone1_type = zone_type_filter("Zone 1")
    zone2_type = zone_type_filter("Zone 2")
    zone3_type = zone_type_filter("Zone 3")

    # ------------------------------------------------
    # --- Compute Grouped Data Based on Zone Conditions ---
    # ------------------------------------------------
    try:
        df_grouped = group_symbols_by_time_zone(
            start_date, end_date, grouping,
            zone1_start, zone2_start, zone3_start,
            zone1_type, zone2_type, zone3_type,
            symbol_filter_value, category_filter_value
        )
    except Exception as e:
        st.error(f"Error in group_symbols_by_time_zone: {str(e)}")
        return

    # Initialize DataFrames and variables for later use
    retracement_df = None
    zone1_retracement_df = None
    high_prob = None
    high_dist_df = None
    low_prob = None
    low_dist_df = None
    bullish_bearish_summary = None
    bullish_bearish_daily = None

    # ------------------------------------------------
    # ---------- Dashboard Summary Cards -------------
    # ------------------------------------------------
    st.subheader("Dashboard Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_days_analyzed_card(df_grouped)
    with col2:
        create_symbols_card(symbol_filter_value, category_filter_value)
    with col3:
        create_date_range_card(start_date, end_date)
    with col4:
        create_zones_card(
            zone1_start, zone1_duration,
            zone2_start, zone2_duration,
            zone3_start, zone3_duration,
            zone1_type, zone2_type, zone3_type
        )

    # ------------------------------------------------
    # ---------- Retracement Analysis Section --------
    # ------------------------------------------------
    st.subheader("Retracement Analysis")
    col1, col2 = st.columns(2)

    # ----- Column 1: Midnight Open Retracement Analysis -----
    with col1:
        st.write("Midnight Open Retracement")
        if not df_grouped.empty:
            selected_days = df_grouped['day'].tolist()
            try:
                retracement_df = get_retracement_stats(selected_days)
                plot_retracement_bar_chart(retracement_df)
            except Exception as e:
                st.error(f"Error in Midnight Open Retracement: {str(e)}")
        else:
            st.write("No days meet the selected zone conditions.")

    # ----- Column 2: Zone 1 Retracement Analysis -----
    with col2:
        st.write("Zone 1 Retracement")
        if not df_grouped.empty:
            selected_days = df_grouped['day'].tolist()
            try:
                zone1_retracement_df = get_zone1_retracement_stats(selected_days)
                plot_zone1_retracement_bar_chart(zone1_retracement_df)
            except Exception as e:
                st.error(f"Error in Zone 1 Retracement: {str(e)}")
        else:
            st.write("No days meet the selected zone conditions.")

    # ------------------------------------------------
    # ------------ Daily Stats Section ----------------
    # ------------------------------------------------
    st.subheader("Daily Stats")
    col_high, col_low = st.columns(2)

    # ----- Column 1: High of Day Analysis -----
    with col_high:
        st.write("High of Day Analysis")
        if 'df_grouped' in locals() and not df_grouped.empty:
            selected_days = df_grouped['day'].tolist()
            try:
                high_prob = get_high_in_open_probability(selected_days)
                plot_high_in_open_probability(high_prob)
                high_dist_df = get_high_distribution(selected_days)
                plot_high_distribution(high_dist_df)
            except Exception as e:
                st.error(f"Error in High of Day Analysis: {str(e)}")
        else:
            st.write("No data available.")

    # ----- Column 2: Low of Day Analysis -----
    with col_low:
        st.write("Low of Day Analysis")
        if 'df_grouped' in locals() and not df_grouped.empty:
            selected_days = df_grouped['day'].tolist()
            try:
                low_prob = get_low_in_open_probability(selected_days)
                plot_low_in_open_probability(low_prob)
                low_dist_df = get_low_distribution(selected_days)
                plot_low_distribution(low_dist_df)
            except Exception as e:
                st.error(f"Error in Low of Day Analysis: {str(e)}")
        else:
            st.write("No data available.")

    # ------------------------------------------------
    # -------- Bullish/Bearish Day Analysis -----------
    # ------------------------------------------------
    st.subheader("Bullish/Bearish Day Analysis")
    if not df_grouped.empty:
        selected_days = df_grouped['day'].tolist()
        try:
            bullish_bearish_summary, bullish_bearish_daily = get_bullish_bearish_stats(selected_days)
            plot_bullish_bearish_probability(bullish_bearish_summary, bullish_bearish_daily)

            # Add statistics summary card after analysis is complete
            st.subheader("Analysis Summary")
            create_stats_summary_card(retracement_df, high_prob, low_prob, bullish_bearish_summary)

        except Exception as e:
            st.error(f"Error in Bullish/Bearish Day Analysis: {str(e)}")
    else:
        st.write("No data available.")

    # ------------------------------------------------
    # ------- Expandable Section: View DataFrames -------
    # ------------------------------------------------
    with st.expander("View DataFrames"):
        st.subheader("Data Used in Charts")

        # --- Symbols Grouped by Day and Zone ---
        st.write("**Symbols Grouped by Day and Zone**")
        if not df_grouped.empty:
            st.write("Matching Days for Conditions:")
            st.write(f"- Zone 1: {zone1_type}")
            st.write(f"- Zone 2: {zone2_type}")
            st.write(f"- Zone 3: {zone3_type}")
            st.dataframe(df_grouped, use_container_width=True)
        else:
            st.write("No data available for the selected parameters.")

        # --- Midnight Open Retracement DataFrame ---
        st.write("**Midnight Open Retracement Data**")
        if retracement_df is not None and not retracement_df.empty:
            st.dataframe(retracement_df, use_container_width=True)
        else:
            st.write("No retracement data available.")

        # --- Zone 1 Retracement DataFrame ---
        st.write("**Zone 1 Retracement Data**")
        if zone1_retracement_df is not None and not zone1_retracement_df.empty:
            st.dataframe(zone1_retracement_df, use_container_width=True)
        else:
            st.write("No Zone 1 retracement data available.")

        # --- High of Day Data ---
        st.write("**High of Day Data**")
        if high_prob is not None:
            st.write(f"High in Open Probability: {high_prob:.2%}")
        if high_dist_df is not None and not high_dist_df.empty:
            st.dataframe(high_dist_df, use_container_width=True)
        else:
            st.write("No high distribution data available.")

        # --- Low of Day Data ---
        st.write("**Low of Day Data**")
        if low_prob is not None:
            st.write(f"Low in Open Probability: {low_prob:.2%}")
        if low_dist_df is not None and not low_dist_df.empty:
            st.dataframe(low_dist_df, use_container_width=True)
        else:
            st.write("No low distribution data available.")

        # --- Bullish/Bearish Day Data ---
        st.write("**Bullish/Bearish Day Data**")
        if bullish_bearish_summary is not None and not bullish_bearish_summary.empty:
            st.write("Day Type Summary:")
            st.dataframe(bullish_bearish_summary, use_container_width=True)
            st.write("Daily Day Types:")
            st.dataframe(bullish_bearish_daily, use_container_width=True)
        else:
            st.write("No bullish/bearish day data available.")


# ------------------------------------------------
# -------------------- EXECUTION -----------------
#  Run the main function when the script is executed.
# ------------------------------------------------
if __name__ == "__main__":
    main()