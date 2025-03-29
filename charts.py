# Import necessary libraries:
import streamlit as st  # Streamlit for building interactive web apps
import pandas as pd  # Pandas for data manipulation and analysis
import plotly.express as px  # Plotly Express for interactive charting
from analysis import get_time_bucket_labels, \
    get_zone1_time_bucket_labels  # Custom functions to retrieve time bucket labels


# ------------------------------------------------
# -------------- Chart Purpose -------------------
# ------------------------------------------------
# Function to plot retracement bar charts
def plot_retracement_bar_chart(retracement_df):
    """
    Plot two bar charts:
    1. A horizontal bar chart summarizing days that retraced vs. did not retrace to midnight open.
    2. A vertical bar chart showing the distribution of first retracement times in 30-minute buckets.
    """
    # Calculate the total retracement count (bucket >= 0) and non-retracement count (bucket == -1)
    retraced_count = retracement_df[retracement_df['bucket'] >= 0]['count'].sum()
    did_not_retrace_count = retracement_df[retracement_df['bucket'] == -1]['count'].sum() if -1 in retracement_df[
        'bucket'].values else 0
    total_days = retraced_count + did_not_retrace_count  # Total number of days

    # Create a summary DataFrame with percentages for retraced and did not retrace statuses
    summary_df = pd.DataFrame({
        'Status': ['Did Not Retrace', 'Retraced'],
        'Percentage': [
            (did_not_retrace_count / total_days * 100) if total_days > 0 else 0,
            (retraced_count / total_days * 100) if total_days > 0 else 0
        ]
    })
    # Add text representation for percentage formatting in the chart
    summary_df['text'] = summary_df['Percentage'].apply(lambda x: f'{x:.2f}%')

    # ------------------------------------------------
    # --------- Chart Purpose: Summary Chart ---------
    #    Midnight Open Probability (Retrace vs Not Retrace)
    # ------------------------------------------------
    st.header("Midnight Open Probability")

    # Create the summary horizontal bar chart using Plotly Express
    fig1 = px.bar(
        summary_df,
        x='Percentage',
        y='Status',
        orientation='h',
        title='Midnight Open Probability',
        text='text',
        color='Status',
        color_discrete_map={'Did Not Retrace': '#FF6666', 'Retraced': '#00C4B4'}
    )
    # Update trace settings for text position and color
    fig1.update_traces(textposition='inside', textfont_color='white')
    # Update layout settings for the chart styling
    fig1.update_layout(
        plot_bgcolor='#1A2526',
        paper_bgcolor='#1A2526',
        font_color='white',
        title_font_color='white',
        xaxis=dict(
            showgrid=False,
            linecolor='lightgray',
            tickcolor='lightgray',
            tickfont_color='white',
            title='Percentage (%)',
            range=[0, 100]
        ),
        yaxis=dict(
            showgrid=False,
            linecolor='lightgray',
            tickcolor='lightgray',
            tickfont_color='white'
        ),
        bargap=0.2,
        title={
            'text': "Midnight Open Probability",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        # Add a decorative horizontal line shape
        shapes=[
            dict(
                type='line',
                x0=0.2, x1=0.8, y0=0.92, y1=0.92,
                xref='paper', yref='paper',
                line=dict(color='yellow', width=2)
            )
        ]
    )
    # Render the summary chart in the Streamlit app
    st.plotly_chart(fig1, use_container_width=True)

    # Prepare data for the distribution chart by filtering retracement entries (bucket >= 0)
    time_buckets_df = retracement_df[retracement_df['bucket'] >= 0].copy()
    # Retrieve custom time bucket labels
    time_bucket_labels = get_time_bucket_labels()
    # Map bucket index to corresponding time bucket label; default to 'Unknown' if index exceeds list length
    time_buckets_df['Time Bucket'] = time_buckets_df['bucket'].apply(
        lambda x: time_bucket_labels[int(x)] if x < len(time_bucket_labels) else 'Unknown'
    )

    # ------------------------------------------------
    # ------ Chart Purpose: Distribution Chart -------
    #     First Retracement Time Distribution (08:00-16:00)
    # ------------------------------------------------
    st.header("First Retracement Time Distribution")

    # Create the vertical bar chart showing the frequency distribution of first retracement times
    fig2 = px.bar(
        time_buckets_df,
        x='Time Bucket',
        y='count',
        title='First Retracement Time Distribution',
        labels={'count': 'FREQUENCY'},
        color_discrete_sequence=['#4682B4']
    )
    # Update layout for the distribution chart
    fig2.update_layout(
        plot_bgcolor='#1A2526',
        paper_bgcolor='#1A2526',
        font_color='white',
        title_font_color='white',
        xaxis=dict(
            tickangle=45,
            linecolor='lightgray',
            tickcolor='lightgray',
            tickfont_color='white'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            linecolor='lightgray',
            tickcolor='lightgray',
            tickfont_color='white',
            title='FREQUENCY'
        ),
        bargap=0.2
    )
    # Render the distribution chart in the Streamlit app
    st.plotly_chart(fig2, use_container_width=True)


# ------------------------------------------------
# -------------- Chart Purpose -------------------
# ------------------------------------------------
# Function to plot Zone 1 retracement bar charts
def plot_zone1_retracement_bar_chart(retracement_df):
    """
    Plot two bar charts for Zone 1 retracement analysis:
    1. A horizontal bar chart showing the probability of retracement to Zone 1.
    2. A vertical bar chart displaying the distribution of first retracement times in 30-minute buckets.
    """
    # Calculate retracement counts similarly as before for Zone 1 analysis
    retraced_count = retracement_df[retracement_df['bucket'] >= 0]['count'].sum()
    did_not_retrace_count = retracement_df[retracement_df['bucket'] == -1]['count'].sum() if -1 in retracement_df[
        'bucket'].values else 0
    total_days = retraced_count + did_not_retrace_count

    # Create summary DataFrame for Zone 1 retracement probability
    summary_df = pd.DataFrame({
        'Status': ['Did Not Retrace', 'Retraced to Zone 1'],
        'Percentage': [
            (did_not_retrace_count / total_days * 100) if total_days > 0 else 0,
            (retraced_count / total_days * 100) if total_days > 0 else 0
        ]
    })
    summary_df['text'] = summary_df['Percentage'].apply(lambda x: f'{x:.2f}%')

    # ------------------------------------------------
    # -------- Chart Purpose: Zone 1 Summary Chart ----
    #  Probability of Retracement after Zone 3 Formation
    # ------------------------------------------------
    st.header("Zone 1 Retracement Probability")

    # Build the summary horizontal bar chart for Zone 1 retracement
    fig1 = px.bar(
        summary_df,
        x='Percentage',
        y='Status',
        orientation='h',
        title='Probability of Zone 1 Retracement after Zone 3 Formation',
        text='text',
        color='Status',
        color_discrete_map={'Did Not Retrace': '#FF6666', 'Retraced to Zone 1': '#00C4B4'}
    )
    fig1.update_traces(textposition='inside', textfont_color='white')
    fig1.update_layout(
        plot_bgcolor='#1A2526',
        paper_bgcolor='#1A2526',
        font_color='white',
        title_font_color='white',
        xaxis=dict(
            showgrid=False,
            linecolor='lightgray',
            tickcolor='lightgray',
            tickfont_color='white',
            title='Percentage (%)',
            range=[0, 100]
        ),
        yaxis=dict(
            showgrid=False,
            linecolor='lightgray',
            tickcolor='lightgray',
            tickfont_color='white'
        ),
        bargap=0.2,
        title={
            'text': "Probability of Zone 1 Retracement after Zone 3 Formation",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        # Add decorative horizontal line for visual enhancement
        shapes=[
            dict(
                type='line',
                x0=0.2, x1=0.8, y0=0.92, y1=0.92,
                xref='paper', yref='paper',
                line=dict(color='yellow', width=2)
            )
        ]
    )
    # Render the Zone 1 summary chart in the Streamlit app
    st.plotly_chart(fig1, use_container_width=True)

    # Prepare data for Zone 1 distribution chart
    time_buckets_df = retracement_df[retracement_df['bucket'] >= 0].copy()
    # Retrieve custom time bucket labels for Zone 1
    time_bucket_labels = get_zone1_time_bucket_labels()
    # Map bucket indices to corresponding time bucket labels
    time_buckets_df['Time Bucket'] = time_buckets_df['bucket'].apply(
        lambda x: time_bucket_labels[int(x)] if x < len(time_bucket_labels) else 'Unknown'
    )

    # ------------------------------------------------
    # ----- Chart Purpose: Zone 1 Distribution Chart ---
    #    First Retracement Time Distribution (After Zone 3)
    # ------------------------------------------------
    st.header("First Zone 1 Retracement Time Distribution")

    # Create the vertical bar chart for Zone 1 retracement distribution
    fig2 = px.bar(
        time_buckets_df,
        x='Time Bucket',
        y='count',
        title='First Zone 1 Retracement Time Distribution (After Zone 3 Formation)',
        labels={'count': 'FREQUENCY'},
        color_discrete_sequence=['#4682B4']
    )
    # Update layout settings for the distribution chart
    fig2.update_layout(
        plot_bgcolor='#1A2526',
        paper_bgcolor='#1A2526',
        font_color='white',
        title_font_color='white',
        xaxis=dict(
            tickangle=45,
            linecolor='lightgray',
            tickcolor='lightgray',
            tickfont_color='white'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            linecolor='lightgray',
            tickcolor='lightgray',
            tickfont_color='white',
            title='FREQUENCY'
        ),
        bargap=0.2
    )
    # Render the Zone 1 distribution chart in the Streamlit app
    st.plotly_chart(fig2, use_container_width=True)


# ------------------------------------------------
# -------- Analysis Purpose: Time Bucket Labels ----
#  Generate labels for 30-minute buckets covering the entire day (00:00 to 24:00).
#  Returns a list of strings, e.g., ['00:00-00:30', '00:30-01:00', ..., '23:30-24:00'].
# ------------------------------------------------
def get_bucket_labels(num_buckets=48):
    labels = []
    bucket_duration = 30  # Each bucket spans 30 minutes
    for i in range(num_buckets):
        start_total_minutes = i * bucket_duration
        end_total_minutes = start_total_minutes + bucket_duration
        start_hour = start_total_minutes // 60
        start_minute = start_total_minutes % 60
        end_hour = end_total_minutes // 60
        end_minute = end_total_minutes % 60
        # Special case: end_hour 24 should be represented as "24:00"
        start_time_str = f"{start_hour:02d}:{start_minute:02d}"
        end_time_str = f"{end_hour:02d}:{end_minute:02d}" if end_hour < 24 else "24:00"
        labels.append(f"{start_time_str}-{end_time_str}")
    return labels



# ------------------------------------------------
# -------------- Chart Purpose -------------------
# ------------------------------------------------
# Function to plot the probability that the high of day occurs during Zone 3 open (0900-1000 EST)
def plot_high_in_open_probability(probability):
    # Create a DataFrame with the probabilities for True/False outcomes
    df = pd.DataFrame({
        'Status': ['False', 'True'],
        'Percentage': [(1 - probability) * 100, probability * 100]
    })
    df['text'] = df['Percentage'].apply(lambda x: f'{x:.2f}%')

    # ------------------------------------------------
    # ---- Chart Purpose: High of Day Probability ----
    #        during Zone 3 Open (0900-1000 EST)
    # ------------------------------------------------
    st.header("High of Day Probability (Zone 3 Open)")

    # Create a horizontal bar chart with the probability data
    fig = px.bar(
        df, x='Percentage', y='Status', orientation='h',
        title='Market Open (Zone 3) (0900-1000est) High of Day Probability',
        text='text', color='Status',
        color_discrete_map={'False': '#FF6666', 'True': '#00C4B4'}
    )
    fig.update_traces(textposition='inside', textfont_color='white')
    # Update layout styling for the chart
    fig.update_layout(
        plot_bgcolor='#1A2526', paper_bgcolor='#1A2526',
        font_color='white', title_font_color='white',
        xaxis=dict(showgrid=False, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white', title='Percentage (%)', range=[0, 100]),
        yaxis=dict(showgrid=False, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white'),
        bargap=0.2
    )
    # Render the high probability chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------
# -------------- Chart Purpose -------------------
# ------------------------------------------------
# Function to plot the probability that the low of day occurs during Zone 3 open (0900-1000 EST)
def plot_low_in_open_probability(probability):
    # Create a DataFrame with the probabilities for True/False outcomes
    df = pd.DataFrame({
        'Status': ['False', 'True'],
        'Percentage': [(1 - probability) * 100, probability * 100]
    })
    df['text'] = df['Percentage'].apply(lambda x: f'{x:.2f}%')

    # ------------------------------------------------
    # ---- Chart Purpose: Low of Day Probability -----
    #        during Zone 3 Open (0900-1000 EST)
    # ------------------------------------------------
    st.header("Low of Day Probability (Zone 3 Open)")

    # Create a horizontal bar chart with the probability data
    fig = px.bar(
        df, x='Percentage', y='Status', orientation='h',
        title='Market Open (Zone 3) (0900-1000est) Low of Day Probability',
        text='text', color='Status',
        color_discrete_map={'False': '#FF6666', 'True': '#00C4B4'}
    )
    fig.update_traces(textposition='inside', textfont_color='white')
    # Update layout styling for the chart
    fig.update_layout(
        plot_bgcolor='#1A2526', paper_bgcolor='#1A2526',
        font_color='white', title_font_color='white',
        xaxis=dict(showgrid=False, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white', title='Percentage (%)', range=[0, 100]),
        yaxis=dict(showgrid=False, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white'),
        bargap=0.2
    )
    # Render the low probability chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------
# -------------- Chart Purpose -------------------
# ------------------------------------------------
# Function to plot distribution for high of day events over time buckets
def plot_high_distribution(df):
    if df.empty:
        st.write("No high distribution data available.")
        return
    # Generate labels for 20 time buckets
    bucket_labels = get_bucket_labels()
    # Map each bucket to its corresponding label; fallback to 'Unknown'
    df['Time Bucket'] = df['bucket'].apply(
        lambda x: bucket_labels[int(x)] if int(x) < len(bucket_labels) else 'Unknown')

    # ------------------------------------------------
    # ---- Chart Purpose: High of Day Distribution ----
    #         Across 20 Time Buckets
    # ------------------------------------------------
    st.header("High of Day Time Distribution")

    # Create a bar chart for the high distribution data
    fig = px.bar(
        df, x='Time Bucket', y='count',
        title='High of Day Time Distribution',
        labels={'count': 'Frequency'}, color_discrete_sequence=['#00C4B4']
    )
    # Update layout settings for the chart styling
    fig.update_layout(
        plot_bgcolor='#1A2526', paper_bgcolor='#1A2526',
        font_color='white', title_font_color='white',
        xaxis=dict(tickangle=45, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', linecolor='lightgray',
                   tickcolor='lightgray', tickfont_color='white')
    )
    # Render the high distribution chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------
# -------------- Chart Purpose -------------------
# ------------------------------------------------
# Function to plot distribution for low of day events over time buckets
def plot_low_distribution(df):
    if df.empty:
        st.write("No low distribution data available.")
        return
    # Generate labels for 20 time buckets
    bucket_labels = get_bucket_labels()
    # Map each bucket to its corresponding label; fallback to 'Unknown'
    df['Time Bucket'] = df['bucket'].apply(
        lambda x: bucket_labels[int(x)] if int(x) < len(bucket_labels) else 'Unknown')

    # ------------------------------------------------
    # ----- Chart Purpose: Low of Day Distribution ----
    #         Across 20 Time Buckets
    # ------------------------------------------------
    st.header("Low of Day Time Distribution")

    # Create a bar chart for the low distribution data
    fig = px.bar(
        df, x='Time Bucket', y='count',
        title='Low of Day Time Distribution (20 buckets)',
        labels={'count': 'Frequency'}, color_discrete_sequence=['#FF6666']
    )
    # Update layout settings for the chart styling
    fig.update_layout(
        plot_bgcolor='#1A2526', paper_bgcolor='#1A2526',
        font_color='white', title_font_color='white',
        xaxis=dict(tickangle=45, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', linecolor='lightgray',
                   tickcolor='lightgray', tickfont_color='white')
    )
    # Render the low distribution chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------
# -------------- Chart Purpose -------------------
# ------------------------------------------------
# Function to plot bullish/bearish day probabilities and a daily breakdown of day types
def plot_bullish_bearish_probability(summary_df, daily_type_df):
    """
    Plot two charts:
    1. Horizontal bar chart showing bullish, bearish, and neutral day probabilities.
    2. Daily breakdown of bullish/bearish days (implementation not shown here).
    """
    # ------------------------------------------------
    # -------- Chart Purpose: Day Type Probability ----
    #  Bullish/Bearish/Neutral Day Probabilities
    # ------------------------------------------------
    st.header("Day Type Probability")

    # Create a horizontal bar chart using the summary DataFrame
    fig1 = px.bar(
        summary_df,
        x='percentage',
        y='day_type',
        orientation='h',
        title='Day Type Probability',
        text=[f'{p:.2f}%' for p in summary_df['percentage']],
        color='day_type',
        color_discrete_map={
            'Bullish': '#00C4B4',  # Green color for bullish days
            'Bearish': '#FF6666',  # Red color for bearish days
            'Neutral': '#888888'  # Gray color for neutral days
        }
    )
    # Update trace settings for text
    fig1.update_traces(textposition='inside', textfont_color='white')
    # Update layout styling for the probability chart
    fig1.update_layout(
        plot_bgcolor='#1A2526',
        paper_bgcolor='#1A2526',
        font_color='white',
        title_font_color='white',
        xaxis=dict(
            showgrid=False,
            linecolor='lightgray',
            tickcolor='lightgray',
            tickfont_color='white',
            title='Percentage (%)',
            range=[0, 100]
        ),
        yaxis=dict(
            showgrid=False,
            linecolor='lightgray',
            tickcolor='lightgray',
            tickfont_color='white'
        ),
        bargap=0.2
    )
    # Render the bullish/bearish probability chart in Streamlit
    st.plotly_chart(fig1, use_container_width=True)
