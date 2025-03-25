import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from data_utils import load_categories, load_symbols, load_data, filter_zones, get_date_range
from datetime import datetime, timedelta
from style import configure_page  # Import the new style configuration


def set_custom_styles():
    """
    Set custom CSS styles for the Streamlit application with a modern and clean design
    """
    custom_css = """
    <style>
    /* Global Background and Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    .stApp {
        background-color: #f4f6f9;
        color: #2c3e50;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Styling */
    .css-1aumxhk {
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
        padding: 20px;
    }

    .sidebar .sidebar-content {
        background-color: #ffffff;
    }

    /* Header Styles */
    h1, h2, h3 {
        color: #1a5f7a;
        font-weight: 700;
        margin-bottom: 15px;
    }

    h1 {
        font-size: 2.2rem;
        border-bottom: 3px solid #4a90e2;
        padding-bottom: 10px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #4a4a4a;
        font-weight: 500;
        padding: 10px 15px;
        transition: all 0.3s ease;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e6f2ff;
    }

    .stTabs [data-baseweb="tab"][data-selected="true"] {
        background-color: #4a90e2;
        color: white;
    }

    /* Dataframe and Table Styling */
    .dataframe {
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .dataframe th {
        background-color: #4a90e2;
        color: white;
        font-weight: 600;
        text-transform: uppercase;
        padding: 12px;
    }

    .dataframe td {
        padding: 10px;
        border: 1px solid #e9ecef;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #4a90e2;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        padding: 10px 20px;
    }

    .stButton>button:hover {
        background-color: #357abd;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Metric and Chart Styling */
    .stPlotlyChart {
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
        padding: 10px;
        background-color: white;
    }

    .metric-container {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
        padding: 15px;
    }

    /* Selectbox and Input Styling */
    .stSelectbox, .stNumberInput, .stDateInput {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def configure_page():
    """
    Configure Streamlit page settings with an enhanced aesthetic
    """
    st.set_page_config(
        page_title="Market Zones Analysis Dashboard",
        page_icon=":chart_with_upwards_trend:",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    set_custom_styles()

def calculate_zone_metrics(zone_df):
    metrics = {
        'Open Price': zone_df['open'].iloc[0],
        'Close Price': zone_df['close'].iloc[-1],
        'High': zone_df['high'].max(),
        'Low': zone_df['low'].min(),
        'Total Volume': zone_df['volume'].sum(),
        'Price Range': zone_df['high'].max() - zone_df['low'].min(),
        'Price Change %': ((zone_df['close'].iloc[-1] - zone_df['open'].iloc[0]) / zone_df['open'].iloc[0]) * 100,
        'Volatility': zone_df['high'].max() - zone_df['low'].min()
    }
    return metrics

def calculate_zone_correlations(filtered_df):
    pivot_df = filtered_df.pivot_table(
        index='ts_est',
        columns='Zone',
        values=['open', 'close', 'high', 'low']
    )
    pivot_df.columns = [f'{col[1]}_{col[0]}' for col in pivot_df.columns]
    correlation_matrix = pivot_df.corr()
    return correlation_matrix

def compute_zone_relationship(zoneA, zoneB):
    A_low, A_high = zoneA['Low'], zoneA['High']
    B_low, B_high = zoneB['Low'], zoneB['High']

    # Determine if zoneA is entirely above or below zoneB
    if A_high < B_low:
        return "Zone A is below Zone B"
    elif A_low > B_high:
        return "Zone A is above Zone B"
    else:
        # Calculate overlap
        overlap = min(A_high, B_high) - max(A_low, B_low)
        range_A = A_high - A_low
        if range_A > 0 and (overlap / range_A) >= 0.75:
            return "Zone A is stacked on top of Zone B"
        else:
            return "Zone A partially overlaps with Zone B"


def create_enhanced_dashboard():
    configure_page()  # Apply custom page configuration
    st.title("Market Zones Relationship Dashboard")

    # Sidebar for filters
    st.sidebar.header("Market Analysis Filters")
    categories = load_categories()
    selected_category = st.sidebar.selectbox("Select Asset Category", categories)
    symbols = load_symbols(selected_category)
    selected_symbol = st.sidebar.selectbox("Select Specific Symbol", symbols)
    min_date, max_date = get_date_range()
    start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

    # Zone Time Configuration
    st.sidebar.subheader("Market Zone Time Configuration")
    zone_configs = {
        "Asia": {
            "opening_hour": st.sidebar.number_input("Asia Opening Hour (EST)", value=19, min_value=0, max_value=23),
            "first_minutes": st.sidebar.number_input("First Minutes (Asia)", value=10, min_value=1, max_value=60)
        },
        "London": {
            "opening_hour": st.sidebar.number_input("London Opening Hour (EST)", value=3, min_value=0, max_value=23),
            "first_minutes": st.sidebar.number_input("First Minutes (London)", value=10, min_value=1, max_value=60)
        },
        "New York": {
            "opening_hour": st.sidebar.number_input("New York Opening Hour (EST)", value=9, min_value=0, max_value=23),
            "first_minutes": st.sidebar.number_input("First Minutes (New York)", value=10, min_value=1, max_value=60)
        }
    }

    # Load and Filter Data
    df = load_data(selected_category, selected_symbol, start_date, end_date)
    zone_opening_hours = {zone: config['opening_hour'] for zone, config in zone_configs.items()}
    filtered_df = filter_zones(
        df,
        zone_configs['Asia']['first_minutes'],
        zone_configs['London']['first_minutes'],
        zone_configs['New York']['first_minutes'],
        zone_opening_hours=zone_opening_hours
    )

    if filtered_df.empty:
        st.warning("No data found. Please adjust your filters.")
        return

    st.header(f"Market Zone Analysis for {selected_symbol} ({selected_category})")

    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs([
        "Charts",
        "Zone Metrics & Performance",
        "Zone Relationship Analysis"
    ])

    # Prepare zone metrics for later use
    zone_metrics = {}
    for zone in filtered_df['Zone'].unique():
        zone_df = filtered_df[filtered_df['Zone'] == zone]
        zone_metrics[zone] = calculate_zone_metrics(zone_df)
    metrics_df = pd.DataFrame.from_dict(zone_metrics, orient='index')

    with tab1:
        # Box Plot for Price Distribution
        st.subheader("Price Distribution by Zone")
        fig_box = go.Figure()
        for zone in filtered_df['Zone'].unique():
            zone_data = filtered_df[filtered_df['Zone'] == zone]
            fig_box.add_trace(go.Box(
                y=zone_data['close'],
                name=zone,
                boxpoints='all',  # Include all points
                jitter=0.3,  # Add some spread to points
                pointpos=-1.8  # Offset points from the box
            ))
        fig_box.update_layout(
            title='Close Price Distribution Across Zones',
            yaxis_title='Price',
            xaxis_title='Zones'
        )
        st.plotly_chart(fig_box, use_container_width=True)

        # Violin Plot for Price Distribution
        st.subheader("Price Distribution Density")
        fig_violin = go.Figure()
        for zone in filtered_df['Zone'].unique():
            zone_data = filtered_df[filtered_df['Zone'] == zone]
            fig_violin.add_trace(go.Violin(
                x=zone_data['Zone'],
                y=zone_data['close'],
                name=zone,
                box_visible=True,  # Show inner box plot
                meanline_visible=True  # Show mean line
            ))
        fig_violin.update_layout(
            title='Price Distribution Density by Zone',
            yaxis_title='Price',
            xaxis_title='Zones'
        )
        st.plotly_chart(fig_violin, use_container_width=True)

        # Line Chart: Volume Trend by Zone
        st.subheader("Trading Volume Trend by Zone")
        volume_by_zone = filtered_df.groupby(['Zone', 'ts_est'])['volume'].sum().reset_index()
        fig_volume = px.line(
            volume_by_zone,
            x='ts_est',
            y='volume',
            color='Zone',
            title='Trading Volume Trend'
        )
        st.plotly_chart(fig_volume, use_container_width=True)

    # Tab 2: Zone Metrics & Performance
    with tab2:
        # Zone Metrics
        st.subheader("Market Zone Metrics")
        st.dataframe(metrics_df.style.format("{:.2f}"))

        # Market Zone Correlations
        st.subheader("Market Zone Correlations")
        correlation_matrix = calculate_zone_correlations(filtered_df)
        fig_corr = px.imshow(
            correlation_matrix,
            labels=dict(x="Features", y="Features", color="Correlation"),
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            color_continuous_scale='RdBu_r'
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        st.dataframe(correlation_matrix)

        # Zone Performance Comparison
        st.subheader("Zone Performance Comparison")
        metrics_to_plot = ['Price Change %', 'Volatility', 'Total Volume']
        fig_perf = go.Figure()
        for metric in metrics_to_plot:
            fig_perf.add_trace(go.Bar(
                x=metrics_df.index,
                y=metrics_df[metric],
                name=metric
            ))
        fig_perf.update_layout(barmode='group')
        st.plotly_chart(fig_perf, use_container_width=True)

    # Tab 3: Zone Relationship Analysis
    with tab3:
        st.subheader("Detailed Zone Relationship Analysis")
        # Ensure we have exactly three zones for this analysis
        zones = list(zone_metrics.keys())
        if len(zones) < 3:
            st.warning("Zone Relationship Analysis requires at least three zones.")
        else:
            # For demonstration, assume:
            # Zone 1 = first zone, Zone 2 = second zone, Zone 3 = third zone
            zone1, zone2, zone3 = zones[0], zones[1], zones[2]
            st.markdown(f"**Comparing Zones:** Zone 1 = {zone1}, Zone 2 = {zone2}, Zone 3 = {zone3}")

            # Zone 1 vs Zone 2 analysis
            rel_1_2 = compute_zone_relationship(zone_metrics[zone1], zone_metrics[zone2])
            st.write(f"**{zone1} vs. {zone2}:** {rel_1_2}")

            # Zone 3 vs Zone 1 and Zone 2 analysis
            rel_3_1 = compute_zone_relationship(zone_metrics[zone3], zone_metrics[zone1])
            rel_3_2 = compute_zone_relationship(zone_metrics[zone3], zone_metrics[zone2])
            st.write(f"**{zone3} vs. {zone1}:** {rel_3_1}")
            st.write(f"**{zone3} vs. {zone2}:** {rel_3_2}")

            # Detailed metrics for context
            st.subheader("Zone Metrics Details")
            for zone in [zone1, zone2, zone3]:
                st.markdown(f"**{zone} Metrics:**")
                for metric, value in zone_metrics[zone].items():
                    st.write(f"{metric}: {value:.2f}")
                st.markdown("---")


if __name__ == "__main__":
    create_enhanced_dashboard()