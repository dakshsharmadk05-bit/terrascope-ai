# ============================================================
# TERRASCOPE AI
# AI-GIS LAND USE & DEFORESTATION MODEL
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TerraScope AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.4rem;
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
""", unsafe_allow_html=True)


# ============================================================
# EARTH ENGINE MODEL RESULTS
# ============================================================

default_landuse_data = pd.DataFrame({

    "Land Use": [
        "Forest",
        "Agriculture",
        "Built-up Area",
        "Water Body",
        "Barren Land"
    ],

    "2020": [
        29175.297228798376,
        9977.040259898702,
        1802.3200028417234,
        1684.4385579742245,
        8427.360176656433
    ],

    "2025": [
        30012.199340350562,
        8521.94504186258,
        1901.608295921227,
        1818.3352222253122,
        8967.373650284231
    ]
})


default_landuse_data["Change"] = (
    default_landuse_data["2025"] -
    default_landuse_data["2020"]
)

default_landuse_data["Change (%)"] = (
    default_landuse_data["Change"] /
    default_landuse_data["2020"] *
    100
)


# ============================================================
# FOREST VALUES
# ============================================================

forest_2020 = float(
    default_landuse_data.loc[
        default_landuse_data["Land Use"] == "Forest",
        "2020"
    ].iloc[0]
)

forest_2025 = float(
    default_landuse_data.loc[
        default_landuse_data["Land Use"] == "Forest",
        "2025"
    ].iloc[0]
)

net_forest_change = forest_2025 - forest_2020

net_forest_percentage = (
    net_forest_change /
    forest_2020 *
    100
)

forest_loss_formula = (
    forest_2020 -
    forest_2025
)

forest_loss_percentage = (
    forest_loss_formula /
    forest_2020 *
    100
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_index(numerator, denominator):

    if denominator == 0:
        return None

    return numerator / denominator


def standardise_uploaded_landuse(df):

    df = df.copy()

    # Earth Engine exported CSV format
    if {
        "land_use",
        "area_2020_km2",
        "area_2025_km2"
    }.issubset(df.columns):

        clean = df[
            [
                "land_use",
                "area_2020_km2",
                "area_2025_km2"
            ]
        ].copy()

        clean.columns = [
            "Land Use",
            "2020",
            "2025"
        ]

        clean["Change"] = (
            clean["2025"] -
            clean["2020"]
        )

        clean["Change (%)"] = np.where(
            clean["2020"] != 0,
            clean["Change"] /
            clean["2020"] *
            100,
            np.nan
        )

        return clean

    # Already-clean format
    if {
        "Land Use",
        "2020",
        "2025"
    }.issubset(df.columns):

        clean = df[
            [
                "Land Use",
                "2020",
                "2025"
            ]
        ].copy()

        clean["Change"] = (
            clean["2025"] -
            clean["2020"]
        )

        clean["Change (%)"] = np.where(
            clean["2020"] != 0,
            clean["Change"] /
            clean["2020"] *
            100,
            np.nan
        )

        return clean

    return None


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🌍 TerraScope AI")

st.sidebar.caption(
    "AI-GIS Land Use & Deforestation Model"
)

st.sidebar.divider()


page = st.sidebar.radio(

    "Navigation",

    [
        "🏠 Overview",
        "🗺️ Land-Use Analysis",
        "🌲 Forest Change",
        "🧮
