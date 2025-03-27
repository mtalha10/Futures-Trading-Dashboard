import streamlit as st

def apply_metal_dark_theme(fig):
    """
    Applies a metal dark theme to a Plotly figure.
    - Chart background: #72797e
    - Font and title color: #ffffff
    - Grid and axis lines: subtle contrasting color (#72797e)
    """
    fig.update_layout(
        paper_bgcolor="#72797e",
        plot_bgcolor="#72797e",
        font=dict(color="#ffffff", size=16),
        title_font=dict(color="#ffffff", size=20),
        xaxis=dict(
            showline=True,
            linecolor="#ffffff",
            tickfont=dict(color="#ffffff", size=14),
            gridcolor="#72797e",
            zerolinecolor="#72797e",
        ),
        yaxis=dict(
            showline=True,
            linecolor="#ffffff",
            tickfont=dict(color="#ffffff", size=14),
            gridcolor="#72797e",
            zerolinecolor="#72797e",
        ),
        legend=dict(
            font=dict(color="#ffffff", size=14),
            bgcolor="#72797e"
        )
    )
    fig.update_xaxes(title_font=dict(color="#ffffff"))
    fig.update_yaxes(title_font=dict(color="#ffffff"))
    return fig

def set_web_background(color="#3c4a50", font_color="#ffffff"):
    """
    Sets the Streamlit app background and styling for a metal dark theme.
    """
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
            color: {font_color};
        }}
        [data-testid="stSidebar"] {{
            background-color: {color} !important;
        }}
        div[data-testid="metric-container"] {{
            background-color: #72797e !important;
            border: 1px solid #5c666e !important;
        }}
        .stSlider .thumb {{
            background-color: #a11212 !important;
        }}
        .stSelectbox div[data-baseweb="select"] {{
            color: {font_color} !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: #4f5b61;
            border-radius: 4px 4px 0px 0px;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: #a11212 !important;
        }}
        .stButton>button {{
            background-color: #a11212 !important;
            color: #ffffff !important;
            border-radius: 5px;
        }}
        .stDataFrame {{
            background-color: #72797e !important;
            color: #ffffff !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
