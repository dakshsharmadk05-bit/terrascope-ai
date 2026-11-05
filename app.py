
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TerraScope AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #8b949e;
        margin-top: 4px;
        margin-bottom: 22px;
    }

    .section-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8b949e;
        font-weight: 700;
    }

    .formula-box {
        border: 1px solid rgba(128,128,128,0.25);
        border-left: 5px solid #2e7d32;
        padding: 18px;
        border-radius: 10px;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .footer {
        text-align: center;
        color: #8b949e;
        padding: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DEFAULT EARTH ENGINE RESULTS
# ============================================================

default_landuse_data = pd.DataFrame(
    {
        "Land Use": [
            "Forest",
            "Agriculture",
            "Built-up Area",
            "Water Body", ]
    }
