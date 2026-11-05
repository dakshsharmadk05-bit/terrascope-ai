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
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

.main-title {
    font-size: 2.7rem;
    font-weight: 800;
    margin-bottom: 0;
}

.subtitle {
    color: #8b949e;
    font-size: 1.05rem;
    margin-top: 5px;
    margin-bottom: 25px;
}

.formula-card {
    border: 1px solid rgba(128,128,128,0.25);
    border-left: 5px solid #2e7d32;
    padding: 20px;
    border-radius: 10px;
    margin-top: 10px;
    margin-bottom: 15px;
}

.result-card {
    border: 1px solid rgba(128,128,128,0.25);
    padding: 20px;
    border-radius: 10px;
    margin-top: 10px;
}

.footer {
    text-align: center;
    color: #8b949e;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🌍 TerraScope AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-GIS Land Use Classification & Deforestation Assessment'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🌍 TerraScope AI")

st.sidebar.caption(
    "AI-GIS Land Use & Deforestation Model"
)

st.sidebar.divider()


study_area = st.sidebar.selectbox(
    "Study Area",
    ["Uttarakhand"]
)


baseline_year = st.sidebar.selectbox(
    "Baseline Year",
    [2020]
)


comparison_year = st.sidebar.selectbox(
    "Comparison Year",
    [2025]
)


model_choice = st.sidebar.selectbox(
    "AI Classification Model",
    ["Random Forest"]
)


st.sidebar.divider()


st.sidebar.markdown("### Land-Use Classes")

st.sidebar.markdown("""
🌲 **Forest**

🌾 **Agriculture**

🏙️ **Built-up Area**

💧 **Water Body**

🟫 **Barren Land**
""")


st.sidebar.divider()


st.sidebar.markdown("### Data")

st.sidebar.markdown("""
**Satellite:** Sentinel-2

**Reference Labels:** ESA WorldCover 2020

**Processing:** Google Earth Engine

**Years:** 2020 & 2025

**Study Area:** Uttarakhand
""")


# ============================================================
# EARTH ENGINE MODEL RESULTS
# ============================================================
#
# These values were generated from the exported
# Google Earth Engine area-comparison table.
#
# They are MODEL-DERIVED estimates.
# They are not official government forest statistics.
#
# ============================================================

landuse_data = pd.DataFrame({

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


# ============================================================
# CALCULATE CHANGE
# ============================================================

landuse_data["Change"] = (
    landuse_data["2025"] -
    landuse_data["2020"]
)


landuse_data["Change (%)"] = (
    landuse_data["Change"] /
    landuse_data["2020"] *
    100
)


# ============================================================
# FOREST VALUES
# ============================================================

forest_2020 = landuse_data.loc[
    landuse_data["Land Use"] == "Forest",
    "2020"
].iloc[0]


forest_2025 = landuse_data.loc[
    landuse_data["Land Use"] == "Forest",
    "2025"
].iloc[0]


# ============================================================
# REQUIRED FORMULA
# ============================================================
#
# Forest Loss = A2020 - A2025
#
# Here the value is negative because the model estimates
# MORE total forest in 2025 than in 2020.
#
# ============================================================

formula_forest_loss = (
    forest_2020 -
    forest_2025
)


formula_change_percent = (
    formula_forest_loss /
    forest_2020 *
    100
)


# ============================================================
# NET FOREST CHANGE
# ============================================================

net_forest_change = (
    forest_2025 -
    forest_2020
)


net_forest_change_percent = (
    net_forest_change /
    forest_2020 *
    100
)


# ============================================================
# DATA NOTE
# ============================================================

st.info(
    "🛰️ **Earth Engine Results Loaded:** The land-use values displayed "
    "below are model-derived estimates generated from Sentinel-2 imagery "
    "using Random Forest classification in Google Earth Engine."
)


st.warning(
    "These results are AI/remote-sensing estimates and should not be "
    "presented as official Forest Survey of India or government statistics."
)


# ============================================================
# MODEL OVERVIEW
# ============================================================

st.header("Model Overview")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Study Area",
        "Uttarakhand"
    )


with col2:

    st.metric(
        "Baseline",
        "2020"
    )


with col3:

    st.metric(
        "Comparison",
        "2025"
    )


with col4:

    st.metric(
        "AI Model",
        "Random Forest"
    )


st.divider()


# ============================================================
# 1. LAND-USE CLASSIFICATION
# ============================================================

st.header("1. Land-Use Classification")


st.write(
    "Sentinel-2 satellite imagery was classified into five "
    "land-use categories using a Random Forest model."
)


map_year = st.radio(
    "Select classification year",
    [2020, 2025],
    horizontal=True
)


# ============================================================
# BASE MAP
# ============================================================

classification_map = folium.Map(
    location=[30.2, 79.2],
    zoom_start=7,
    tiles="OpenStreetMap"
)


locations = [

    ["Dehradun", 30.3165, 78.0322],

    ["Haridwar", 29.9457, 78.1642],

    ["Nainital", 29.3919, 79.4542],

    ["Almora", 29.5892, 79.6467],

    ["Pithoragarh", 29.5829, 80.2182],

    ["Chamoli", 30.4036, 79.3220],

    ["Uttarkashi", 30.7268, 78.4354],

    ["Rudraprayag", 30.2844, 78.9811],

    ["Bageshwar", 29.8376, 79.7713]

]


for place, latitude, longitude in locations:

    folium.CircleMarker(

        location=[latitude, longitude],

        radius=5,

        tooltip=place,

        popup=(
            f"{place}<br>"
            f"Classification Year: {map_year}"
        ),

        color="#2e7d32",

        fill=True,

        fill_opacity=0.8

    ).add_to(classification_map)


st_folium(
    classification_map,
    width=None,
    height=500,
    returned_objects=[]
)


st.caption(
    "The interactive base map identifies the Uttarakhand study region. "
    "The classified GeoTIFF generated by Google Earth Engine represents "
    "the actual raster classification output."
)


# ============================================================
# CLASSIFICATION LEGEND
# ============================================================

st.subheader("Classification Classes")


class1, class2, class3, class4, class5 = st.columns(5)


with class1:
    st.success("🌲 Forest")


with class2:
    st.warning("🌾 Agriculture")


with class3:
    st.error("🏙️ Built-up")


with class4:
    st.info("💧 Water Body")


with class5:
    st.markdown("🟫 **Barren Land**")


st.divider()


# ============================================================
# 2. FOREST CHANGE ASSESSMENT
# ============================================================

st.header("2. Forest Change Assessment")


st.write(
    "The classified land-use maps for 2020 and 2025 are compared "
    "to quantify changes in total classified forest area."
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Forest Area 2020",
        f"{forest_2020:,.2f} km²"
    )


with col2:

    st.metric(
        "Forest Area 2025",
        f"{forest_2025:,.2f} km²"
    )


with col3:

    st.metric(
        "Net Forest Change",
        f"+{net_forest_change:,.2f} km²"
    )


with col4:

    st.metric(
        "Net Forest Change",
        f"+{net_forest_change_percent:.2f}%"
    )


st.success(
    f"The model estimates a net increase of "
    f"{net_forest_change:,.2f} km² "
    f"({net_forest_change_percent:.2f}%) in total classified "
    f"forest area between 2020 and 2025."
)


st.divider()


# ============================================================
# 3. REQUIRED FOREST-LOSS FORMULA
# ============================================================

st.header("3. Forest-Loss Calculation")


st.write(
    "The required project formula is applied directly to the "
    "forest areas obtained from the classified satellite images."
)


st.markdown(
    """
    <div class="formula-card">

    <b>Forest Loss</b> =
    Forest Area in Baseline Year −
    Forest Area in Comparison Year

    </div>
    """,
    unsafe_allow_html=True
)


st.latex(
    r"Forest\ Loss=A_{2020}-A_{2025}"
)


st.latex(
    r"Forest\ Loss\ (\%)="
    r"\frac{A_{2020}-A_{2025}}{A_{2020}}\times100"
)


# ============================================================
# SHOW ACTUAL CALCULATION
# ============================================================

calc1, calc2 = st.columns(2)


with calc1:

    st.subheader("Area Calculation")

    st.write(
        f"{forest_2020:,.2f} − "
        f"{forest_2025:,.2f}"
    )

    st.metric(
        "Formula Result",
        f"{formula_forest_loss:,.2f} km²"
    )


with calc2:

    st.subheader("Percentage Calculation")

    st.write(
        f"({forest_2020:,.2f} − "
        f"{forest_2025:,.2f}) "
        f"÷ {forest_2020:,.2f} × 100"
    )

    st.metric(
        "Formula Result",
        f"{formula_change_percent:.2f}%"
    )


st.info(
    "The formula produces a negative forest-loss value because "
    "the classified forest area is larger in 2025 than in 2020. "
    "Therefore, the result represents a net forest gain of "
    f"{net_forest_change_percent:.2f}%, not net deforestation."
)


st.divider()


# ============================================================
# 4. DEFORESTATION / FOREST-TO-NON-FOREST MAP
# ============================================================

st.header("4. Deforestation Map")


st.write(
    "Deforestation is assessed spatially by identifying pixels "
    "classified as Forest in 2020 that changed to a non-forest "
    "class in 2025."
)


st.markdown("""
### Change-Detection Logic

**Forest in 2020**

↓

**Compare corresponding 2025 pixel**

↓

**Non-Forest in 2025**

↓

🔴 **Potential Forest-Loss Pixel**
""")


deforestation_map = folium.Map(
    location=[30.2, 79.2],
    zoom_start=7,
    tiles="OpenStreetMap"
)


folium.Marker(
    [30.3165, 78.0322],
    tooltip="Uttarakhand Forest Change Analysis",
    popup="Forest → Non-Forest analysis: 2020–2025"
).add_to(deforestation_map)


st_folium(
    deforestation_map,
    width=None,
    height=500,
    returned_objects=[]
)


st.caption(
    "The actual Forest → Non-Forest raster has been generated separately "
    "in Google Earth Engine as TerraScope_Deforestation_2020_2025."
)


st.info(
    "Net forest-area change and gross Forest → Non-Forest change are "
    "different measurements. Forest loss can occur in some locations "
    "even when the total classified forest area increases overall."
)


st.divider()


# ============================================================
# 5. AREA-WISE COMPARISON TABLE
# ============================================================

st.header("5. Area-Wise Comparison Table")


comparison_table = landuse_data.copy()


comparison_table.columns = [
    "Land-Use Category",
    "Area 2020 (km²)",
    "Area 2025 (km²)",
    "Change (km²)",
    "Change (%)"
]


# Round display values

for column in [
    "Area 2020 (km²)",
    "Area 2025 (km²)",
    "Change (km²)",
    "Change (%)"
]:

    comparison_table[column] = (
        comparison_table[column].round(2)
    )


st.dataframe(
    comparison_table,
    use_container_width=True,
    hide_index=True
)


st.caption(
    "Source: TerraScope AI Google Earth Engine Random Forest "
    "classification results."
)


# ============================================================
# CHANGE INTERPRETATION
# ============================================================

st.subheader("Land-Use Change Interpretation")


interpretation = landuse_data.copy()


interpretation["Trend"] = np.where(
    interpretation["Change"] > 0,
    "↑ Increase",
    np.where(
        interpretation["Change"] < 0,
        "↓ Decrease",
        "No Change"
    )
)


interpretation["Change"] = (
    interpretation["Change"].round(2)
)


interpretation["Change (%)"] = (
    interpretation["Change (%)"].round(2)
)


st.dataframe(

    interpretation[
        [
            "Land Use",
            "Change",
            "Change (%)",
            "Trend"
        ]
    ],

    use_container_width=True,

    hide_index=True

)


st.divider()


# ============================================================
# 6. LAND-USE CHANGE GRAPH
# ============================================================

st.header("6. Land-Use Change Graph")


graph_data = landuse_data.melt(

    id_vars="Land Use",

    value_vars=["2020", "2025"],

    var_name="Year",

    value_name="Area (km²)"

)


comparison_fig = px.bar(

    graph_data,

    x="Land Use",

    y="Area (km²)",

    color="Year",

    barmode="group",

    title="Land-Use Classification: 2020 vs 2025"

)


comparison_fig.update_layout(

    xaxis_title="Land-Use Category",

    yaxis_title="Area (km²)",

    legend_title="Year",

    hovermode="x unified"

)


st.plotly_chart(
    comparison_fig,
    use_container_width=True
)


# ============================================================
# NET CHANGE GRAPH
# ============================================================

st.subheader("Net Land-Use Change")


change_fig = px.bar(

    landuse_data,

    x="Land Use",

    y="Change",

    title="Net Land-Use Change: 2020–2025",

    labels={
        "Change": "Change in Area (km²)"
    }

)


change_fig.add_hline(
    y=0,
    line_width=1
)


st.plotly_chart(
    change_fig,
    use_container_width=True
)


# ============================================================
# FOREST CHANGE GRAPH
# ============================================================

st.subheader("Forest Area Comparison")


forest_graph = pd.DataFrame({

    "Year": [
        "2020",
        "2025"
    ],

    "Forest Area (km²)": [
        forest_2020,
        forest_2025
    ]

})


forest_fig = px.bar(

    forest_graph,

    x="Year",

    y="Forest Area (km²)",

    title="Classified Forest Area: 2020 vs 2025",

    text_auto=".2f"

)


st.plotly_chart(
    forest_fig,
    use_container_width=True
)


st.divider()


# ============================================================
# 7. AI CLASSIFICATION MODEL
# ============================================================

st.header("7. AI Classification Model")


model1, model2 = st.columns(2)


with model1:

    st.subheader("Random Forest")

    st.write(
        "Random Forest is a supervised machine-learning algorithm "
        "that combines multiple decision trees to classify satellite "
        "pixels according to their spectral characteristics."
    )

    st.markdown("""
    **Predictor variables used:**

    - Blue band (B2)
    - Green band (B3)
    - Red band (B4)
    - Near Infrared (B8)
    - SWIR-1 (B11)
    - SWIR-2 (B12)
    - NDVI
    - NDWI
    - NDBI
    - BSI
    """)


with model2:

    st.subheader("Reference Classes")

    st.markdown("""
    ESA WorldCover 2020 reference classes were mapped into:

    **0 — Forest**

    **1 — Agriculture**

    **2 — Built-up Area**

    **3 — Water Body**

    **4 — Barren Land**
    """)


st.divider()


# ============================================================
# 8. WORKING PROCESS
# ============================================================

st.header("8. Working Process")


st.markdown("""
### 1 — Satellite Image Acquisition

Sentinel-2 imagery was obtained through **Google Earth Engine**
for 2020 and 2025.

### 2 — Pre-processing

The imagery was:

- filtered to Uttarakhand,
- filtered for cloud cover,
- cloud masked,
- composited, and
- clipped to the study area.

### 3 — Feature Extraction

Spectral bands were supplemented with:

- **NDVI** — vegetation information
- **NDWI** — water information
- **NDBI** — built-up information
- **BSI** — bare-soil information

### 4 — Training Data

ESA WorldCover 2020 was used to generate reference samples
for the five required land-use classes.

### 5 — Random Forest Training

The labelled samples were divided into training and testing
subsets and used to train the Random Forest classifier.

### 6 — Classification

The trained model was applied to Sentinel-2 imagery to produce
land-use classification maps for **2020 and 2025**.

### 7 — Change Detection

The two classified images were compared to determine land-use
change and identify **Forest → Non-Forest** transitions.

### 8 — Area Calculation

Pixel areas were converted to square kilometres to calculate
the area occupied by each land-use category.
""")


st.divider()


# ============================================================
# 9. OUTPUTS
# ============================================================

st.header("9. Model Outputs")


out1, out2 = st.columns(2)


with out1:

    st.subheader("🗺️ Land-Use Classification Map")

    st.write(
        "Classification of Uttarakhand into five "
        "land-use categories for 2020 and 2025."
    )


    st.subheader("📋 Area-Wise Comparison")

    st.write(
        "Quantitative comparison of land-use area "
        "between the two years."
    )


with out2:

    st.subheader("🌲 Deforestation Map")

    st.write(
        "Spatial identification of Forest → Non-Forest "
        "pixel transitions."
    )


    st.subheader("📊 Land-Use Change Graph")

    st.write(
        "Graphical comparison of changes in all five "
        "land-use categories."
    )


st.divider()


# ============================================================
# 10. DATA SOURCES
# ============================================================

st.header("10. Data Sources & Method")


st.markdown("""
### Sentinel-2

Multispectral satellite imagery used as the primary input for
land-use classification.

**Source:** Copernicus Sentinel-2 / European Union Space Programme

---

### ESA WorldCover 2020

Used as the reference land-cover dataset for automatically
generating labelled training samples.

**Source:** European Space Agency WorldCover

---

### Google Earth Engine

Used for:

- satellite-data access,
- cloud masking,
- spectral-index calculation,
- Random Forest training,
- classification,
- change detection,
- area calculation, and
- GeoTIFF/CSV export.
""")


st.divider()


# ============================================================
# FINAL INTERPRETATION
# ============================================================

st.header("Result Summary")


st.success(
    f"🌲 The Random Forest classification estimates that total "
    f"classified forest area changed from "
    f"{forest_2020:,.2f} km² in 2020 to "
    f"{forest_2025:,.2f} km² in 2025."
)


st.info(
    f"This represents a model-derived net forest-area increase of "
    f"{net_forest_change:,.2f} km² "
    f"({net_forest_change_percent:.2f}%). "
    f"Spatial Forest → Non-Forest transitions are analysed separately "
    f"using the deforestation change raster."
)


st.warning(
    "The results are model-derived estimates produced for this "
    "AI-GIS project. They should not be interpreted as official "
    "government forest-cover statistics."
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")


st.markdown(
    """
    <div class="footer">

    <b>TerraScope AI</b><br>

    AI-GIS Land Use & Deforestation Model<br>

    Uttarakhand, India<br><br>

    Sentinel-2 • ESA WorldCover • Google Earth Engine • Random Forest

    </div>
    """,
    unsafe_allow_html=True
)
