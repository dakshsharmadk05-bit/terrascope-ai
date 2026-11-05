import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI-GIS Land Use & Deforestation Model",
    page_icon="🌲",
    layout="wide"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.main-title {
    font-size: 2.4rem;
    font-weight: 700;
    margin-bottom: 0px;
}

.subtitle {
    color: #667085;
    font-size: 1rem;
    margin-bottom: 25px;
}

.metric-card {
    background-color: #f8faf9;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px;
}

.info-box {
    background-color: #f5f9f6;
    border-left: 5px solid #2e7d32;
    padding: 18px;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<p class="main-title">🌲 AI-GIS Land Use & Deforestation Model</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">Machine-learning based land-use classification and deforestation assessment</p>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("AI-GIS Controls")

study_area = st.sidebar.selectbox(
    "Study Area",
    ["Uttarakhand"]
)

year_1 = st.sidebar.selectbox(
    "Baseline Year",
    [2020]
)

year_2 = st.sidebar.selectbox(
    "Comparison Year",
    [2025]
)

model = st.sidebar.selectbox(
    "AI Model",
    ["Random Forest", "Support Vector Machine"]
)

st.sidebar.markdown("---")

st.sidebar.markdown("""
### Land-Use Classes

🌲 Forest  
🌾 Agriculture  
🏙️ Built-up Area  
💧 Water Body  
🟫 Barren Land
""")

# ---------------------------------------------------------
# DEMONSTRATION DATA
# ---------------------------------------------------------
# Replace these values with satellite-derived classification
# results once the final raster analysis is completed.

landuse_data = pd.DataFrame({

    "Land Use": [
        "Forest",
        "Agriculture",
        "Built-up Area",
        "Water Body",
        "Barren Land"
    ],

    "2020": [
        38200,
        7600,
        2100,
        1100,
        4500
    ],

    "2025": [
        36800,
        7900,
        2700,
        1150,
        4950
    ]
})

landuse_data["Change"] = (
    landuse_data["2025"] - landuse_data["2020"]
)

landuse_data["Change (%)"] = (
    landuse_data["Change"] /
    landuse_data["2020"] * 100
).round(2)


# ---------------------------------------------------------
# DEFORESTATION CALCULATION
# ---------------------------------------------------------

forest_2020 = landuse_data.loc[
    landuse_data["Land Use"] == "Forest", "2020"
].iloc[0]

forest_2025 = landuse_data.loc[
    landuse_data["Land Use"] == "Forest", "2025"
].iloc[0]

forest_loss = forest_2020 - forest_2025

forest_loss_percentage = (
    forest_loss / forest_2020
) * 100


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

st.subheader("Land-Use Change Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Forest Area – 2020",
    f"{forest_2020:,.0f} km²"
)

col2.metric(
    "Forest Area – 2025",
    f"{forest_2025:,.0f} km²"
)

col3.metric(
    "Estimated Forest Loss",
    f"{forest_loss:,.0f} km²"
)

col4.metric(
    "Forest Loss",
    f"{forest_loss_percentage:.2f}%"
)

st.caption(
    "Current values are demonstration data and must not be interpreted as official forest statistics."
)

st.divider()


# ---------------------------------------------------------
# LAND-USE CLASSIFICATION MAP
# ---------------------------------------------------------

st.header("1. Land-Use Classification Map")

st.write(
    "The classification map represents the five land-use categories "
    "used by the AI-GIS model."
)

map_year = st.radio(
    "Select classification year",
    [2020, 2025],
    horizontal=True
)

m = folium.Map(
    location=[30.1, 79.2],
    zoom_start=7,
    tiles="CartoDB positron"
)

folium.Marker(
    [30.3165, 78.0322],
    tooltip="Dehradun",
    popup=f"Study Area: Uttarakhand | Classification Year: {map_year}"
).add_to(m)

st_folium(
    m,
    width=None,
    height=500
)

st.info(
    "Satellite-derived classified raster layers will be displayed "
    "on this map after preprocessing and Random Forest/SVM classification."
)


# ---------------------------------------------------------
# DEFORESTATION MAP
# ---------------------------------------------------------

st.header("2. Deforestation Map")

st.write(
    "Deforestation is detected by comparing pixels classified as "
    "forest in the baseline year with pixels converted to another "
    "land-use class in the comparison year."
)

deforestation_map = folium.Map(
    location=[30.1, 79.2],
    zoom_start=7,
    tiles="CartoDB positron"
)

folium.Marker(
    [30.3165, 78.0322],
    tooltip="Deforestation Analysis",
    popup="Forest change: 2020 → 2025"
).add_to(deforestation_map)

st_folium(
    deforestation_map,
    width=None,
    height=500
)


# ---------------------------------------------------------
# AREA-WISE COMPARISON TABLE
# ---------------------------------------------------------

st.header("3. Area-Wise Comparison Table")

display_table = landuse_data.copy()

display_table.columns = [
    "Land-Use Category",
    "Area 2020 (km²)",
    "Area 2025 (km²)",
    "Change (km²)",
    "Change (%)"
]

st.dataframe(
    display_table,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# LAND-USE CHANGE GRAPH
# ---------------------------------------------------------

st.header("4. Land-Use Change Graph")

graph_data = landuse_data.melt(
    id_vars="Land Use",
    value_vars=["2020", "2025"],
    var_name="Year",
    value_name="Area (km²)"
)

fig = px.bar(
    graph_data,
    x="Land Use",
    y="Area (km²)",
    color="Year",
    barmode="group",
    title="Land-Use Area Comparison: 2020 vs 2025"
)

fig.update_layout(
    xaxis_title="Land-Use Category",
    yaxis_title="Area (km²)",
    legend_title="Year"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ---------------------------------------------------------
# DEFORESTATION FORMULA
# ---------------------------------------------------------

st.header("Deforestation Calculation")

st.markdown("""
The estimated forest loss is calculated as:

**Forest Loss = Forest Area in Baseline Year − Forest Area in Comparison Year**
""")

st.latex(
    r"Forest\ Loss\ (\%) = "
    r"\frac{Forest_{baseline}-Forest_{comparison}}"
    r"{Forest_{baseline}}\times100"
)

st.success(
    f"Estimated forest loss = {forest_loss:,.0f} km² "
    f"({forest_loss_percentage:.2f}%)"
)


# ---------------------------------------------------------
# AI MODEL
# ---------------------------------------------------------

st.header("AI Classification Model")

st.markdown(f"""
**Selected model:** {model}

The satellite image is classified into five land-use categories:

1. Forest
2. Agriculture
3. Built-up Area
4. Water Body
5. Barren Land

The model is trained using labelled samples representing these
land-use classes. The trained classifier is then applied to the
satellite image to generate the final land-use classification map.
""")


# ---------------------------------------------------------
# WORKFLOW
# ---------------------------------------------------------

st.header("Methodology")

st.markdown("""
**1. Satellite Image Acquisition**  
Download satellite imagery for two different years from Google Earth Engine or Sentinel Hub.

**2. Image Pre-processing**  
Crop the imagery to the selected study area and prepare the spectral bands.

**3. Land-Use Classes**  
Create labelled samples for forest, agriculture, built-up area, water body and barren land.

**4. AI Model Training**  
Train a Random Forest or Support Vector Machine classifier.

**5. Land-Use Classification**  
Apply the trained model to classify the satellite image.

**6. Change Detection**  
Compare classified images from the two selected years.

**7. Deforestation Assessment**  
Identify areas that changed from forest to non-forest and calculate forest loss.
""")


# ---------------------------------------------------------
# DATA NOTE
# ---------------------------------------------------------

st.divider()

st.warning("""
DATA NOTE

The numerical values currently displayed in this prototype are
demonstration values only. They are included to test the AI-GIS
dashboard and must not be presented as official satellite-derived
results.

The final project will replace these values with results obtained
from processed satellite imagery and GIS analysis.
""")

st.caption(
    "AI-GIS Land Use & Deforestation Model | Uttarakhand Study Area"
)
