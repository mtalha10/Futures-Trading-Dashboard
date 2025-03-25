# style.py:
import streamlit as st

def set_custom_styles():
    """
    Set custom CSS styles for the Streamlit application
    """
    custom_css = """
    <style>
    /* Main background and text color */
    .stApp {
        background-color: #f0f2f6;
        color: #262730;
    }

    /* Sidebar styling */
    .css-1aumxhk {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Header styles */
    h1, h2, h3 {
        color: #1a3b5c;
        font-weight: 600;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        color: #4a4a4a;
        padding: 10px 15px;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e6f2ff;
    }

    /* Dataframe styling */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 1rem;
    }

    .dataframe th {
        background-color: #4a90e2;
        color: white;
        font-weight: bold;
    }

    .dataframe td, .dataframe th {
        padding: 0.75rem;
        border: 1px solid #dee2e6;
    }

    /* Button styling */
    .stButton>button {
        background-color: #4a90e2;
        color: white;
        border-radius: 5px;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #357abd;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def configure_page():
    """
    Configure Streamlit page settings
    """
    st.set_page_config(
        page_title="Market Zones Analysis Dashboard",
        page_icon=":chart_with_upwards_trend:",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    set_custom_styles()