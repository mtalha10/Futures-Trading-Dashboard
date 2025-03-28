import streamlit as st
import pandas as pd
import plotly.express as px
from analysis import get_time_bucket_labels, get_zone1_time_bucket_labels

def plot_retracement_bar_chart(retracement_df):
    """
    Plot two bar charts:
    1. Summary of days that retraced vs. did not retrace to midnight open (horizontal bar chart with percentages).
    2. Distribution of first retracement times in 30-minute buckets (vertical bar chart).
    """
    # Summary chart: Retraced vs Did Not Retrace (with percentages)
    retraced_count = retracement_df[retracement_df['bucket'] >= 0]['count'].sum()
    did_not_retrace_count = retracement_df[retracement_df['bucket'] == -1]['count'].sum() if -1 in retracement_df['bucket'].values else 0
    total_days = retraced_count + did_not_retrace_count
    summary_df = pd.DataFrame({
        'Status': ['Did Not Retrace', 'Retraced'],
        'Percentage': [
            (did_not_retrace_count / total_days * 100) if total_days > 0 else 0,
            (retraced_count / total_days * 100) if total_days > 0 else 0
        ]
    })
    summary_df['text'] = summary_df['Percentage'].apply(lambda x: f'{x:.2f}%')

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
            'text': "Midnight Open Probability",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        shapes=[
            dict(
                type='line',
                x0=0.2, x1=0.8, y0=0.92, y1=0.92,
                xref='paper', yref='paper',
                line=dict(color='yellow', width=2)
            )
        ]
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Distribution chart: Time buckets for retracements
    time_buckets_df = retracement_df[retracement_df['bucket'] >= 0].copy()
    time_bucket_labels = get_time_bucket_labels()
    time_buckets_df['Time Bucket'] = time_buckets_df['bucket'].apply(
        lambda x: time_bucket_labels[int(x)] if x < len(time_bucket_labels) else 'Unknown'
    )
    fig2 = px.bar(
        time_buckets_df,
        x='Time Bucket',
        y='count',
        title='First Retracement Time Distribution (08:00-16:00)',
        labels={'count': 'FREQUENCY'},
        color_discrete_sequence=['#4682B4']
    )
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
    st.plotly_chart(fig2, use_container_width=True)

def plot_zone1_retracement_bar_chart(retracement_df):
    """
    Plot two bar charts for Zone 1 retracement analysis:
    1. Summary of days that retraced vs. did not retrace to Zone 1 (horizontal bar chart with percentages).
    2. Distribution of first retracement times in 30-minute buckets (vertical bar chart).
    """
    # Summary chart: Retraced vs Did Not Retrace (with percentages)
    retraced_count = retracement_df[retracement_df['bucket'] >= 0]['count'].sum()
    did_not_retrace_count = retracement_df[retracement_df['bucket'] == -1]['count'].sum() if -1 in retracement_df['bucket'].values else 0
    total_days = retraced_count + did_not_retrace_count
    summary_df = pd.DataFrame({
        'Status': ['Did Not Retrace', 'Retraced to Zone 1'],
        'Percentage': [
            (did_not_retrace_count / total_days * 100) if total_days > 0 else 0,
            (retraced_count / total_days * 100) if total_days > 0 else 0
        ]
    })
    summary_df['text'] = summary_df['Percentage'].apply(lambda x: f'{x:.2f}%')

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
        shapes=[
            dict(
                type='line',
                x0=0.2, x1=0.8, y0=0.92, y1=0.92,
                xref='paper', yref='paper',
                line=dict(color='yellow', width=2)
            )
        ]
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Distribution chart: Time buckets for retracements
    time_buckets_df = retracement_df[retracement_df['bucket'] >= 0].copy()
    time_bucket_labels = get_zone1_time_bucket_labels()
    time_buckets_df['Time Bucket'] = time_buckets_df['bucket'].apply(
        lambda x: time_bucket_labels[int(x)] if x < len(time_bucket_labels) else 'Unknown'
    )
    fig2 = px.bar(
        time_buckets_df,
        x='Time Bucket',
        y='count',
        title='First Zone 1 Retracement Time Distribution (After Zone 3 Formation)',
        labels={'count': 'FREQUENCY'},
        color_discrete_sequence=['#4682B4']
    )
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
    st.plotly_chart(fig2, use_container_width=True)


# Generate time bucket labels (e.g., "09:00-09:20")
def get_bucket_labels(num_buckets=20):
    labels = []
    bucket_duration = 21  # minutes
    for i in range(num_buckets):
        start_min = i * bucket_duration
        end_min = start_min + bucket_duration - 1
        start_hour = 9 + start_min // 60
        start_minute = start_min % 60
        end_hour = 9 + end_min // 60
        end_minute = end_min % 60
        start_time_str = f"{start_hour:02d}:{start_minute:02d}"
        end_time_str = f"{end_hour:02d}:{end_minute:02d}"
        labels.append(f"{start_time_str}-{end_time_str}")
    return labels

# Probability bar chart for high
def plot_high_in_open_probability(probability):
    df = pd.DataFrame({
        'Status': ['False', 'True'],
        'Percentage': [(1 - probability) * 100, probability * 100]
    })
    df['text'] = df['Percentage'].apply(lambda x: f'{x:.2f}%')
    fig = px.bar(
        df, x='Percentage', y='Status', orientation='h',
        title='Market Open (Zone 3) (0900-1000est) High of Day Probability',
        text='text', color='Status',
        color_discrete_map={'False': '#FF6666', 'True': '#00C4B4'}
    )
    fig.update_traces(textposition='inside', textfont_color='white')
    fig.update_layout(
        plot_bgcolor='#1A2526', paper_bgcolor='#1A2526',
        font_color='white', title_font_color='white',
        xaxis=dict(showgrid=False, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white', title='Percentage (%)', range=[0, 100]),
        yaxis=dict(showgrid=False, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white'),
        bargap=0.2
    )
    st.plotly_chart(fig, use_container_width=True)

# Probability bar chart for low
def plot_low_in_open_probability(probability):
    df = pd.DataFrame({
        'Status': ['False', 'True'],
        'Percentage': [(1 - probability) * 100, probability * 100]
    })
    df['text'] = df['Percentage'].apply(lambda x: f'{x:.2f}%')
    fig = px.bar(
        df, x='Percentage', y='Status', orientation='h',
        title='Market Open (Zone 3) (0900-1000est) Low of Day Probability',
        text='text', color='Status',
        color_discrete_map={'False': '#FF6666', 'True': '#00C4B4'}
    )
    fig.update_traces(textposition='inside', textfont_color='white')
    fig.update_layout(
        plot_bgcolor='#1A2526', paper_bgcolor='#1A2526',
        font_color='white', title_font_color='white',
        xaxis=dict(showgrid=False, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white', title='Percentage (%)', range=[0, 100]),
        yaxis=dict(showgrid=False, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white'),
        bargap=0.2
    )
    st.plotly_chart(fig, use_container_width=True)

# In charts.py, modify plot_high_distribution and plot_low_distribution
def plot_high_distribution(df):
    if df.empty:
        st.write("No high distribution data available.")
        return
    bucket_labels = get_bucket_labels()
    df['Time Bucket'] = df['bucket'].apply(lambda x: bucket_labels[int(x)] if int(x) < len(bucket_labels) else 'Unknown')
    fig = px.bar(
        df, x='Time Bucket', y='count',
        title='High of Day Time Distribution (20 buckets)',
        labels={'count': 'Frequency'}, color_discrete_sequence=['#00C4B4']
    )
    fig.update_layout(
        plot_bgcolor='#1A2526', paper_bgcolor='#1A2526',
        font_color='white', title_font_color='white',
        xaxis=dict(tickangle=45, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', linecolor='lightgray',
                   tickcolor='lightgray', tickfont_color='white')
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_low_distribution(df):
    if df.empty:
        st.write("No low distribution data available.")
        return
    bucket_labels = get_bucket_labels()
    df['Time Bucket'] = df['bucket'].apply(lambda x: bucket_labels[int(x)] if int(x) < len(bucket_labels) else 'Unknown')
    fig = px.bar(
        df, x='Time Bucket', y='count',
        title='Low of Day Time Distribution (20 buckets)',
        labels={'count': 'Frequency'}, color_discrete_sequence=['#FF6666']
    )
    fig.update_layout(
        plot_bgcolor='#1A2526', paper_bgcolor='#1A2526',
        font_color='white', title_font_color='white',
        xaxis=dict(tickangle=45, linecolor='lightgray', tickcolor='lightgray',
                   tickfont_color='white'),
        yaxis=dict(showgrid=True, gridcolor='lightgray', linecolor='lightgray',
                   tickcolor='lightgray', tickfont_color='white')
    )
    st.plotly_chart(fig, use_container_width=True)