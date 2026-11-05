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

st.sidebar.markdown("### Data Sources")

st.sidebar.markdown("""
**Satellite:** Sentinel-2

**Reference Labels:** ESA WorldCover 2020

**Processing:** Google Earth Engine

**Baseline:** 2020

**Comparison:** 2025
""")


# ============================================================
# EARTH ENGINE RESULTS
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
# CALCULATE LAND-USE CHANGE
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


net_forest_change = (
    forest_2025 -
    forest_2020
)

net_forest_change_percentage = (
    net_forest_change /
    forest_2020 *
    100
)


# Required formula

formula_result = (
    forest_2020 -
    forest_2025
)

formula_percentage = (
    formula_result /
    forest_2020 *
    100
)


# ============================================================
# DATA STATUS
# ============================================================

st.info(
    "🛰️ **Earth Engine Results Loaded:** Land-use areas are based "
    "on the TerraScope AI Random Forest classification of Sentinel-2 imagery."
)

st.warning(
    "The values are model-derived remote-sensing estimates and "
    "should not be interpreted as official government forest statistics."
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

st.header("1. Land-Use Classification Map")

st.write(
    "Sentinel-2 imagery is classified into five land-use "
    "categories using the Random Forest machine-learning model."
)

map_year = st.radio(
    "Select classification year",
    [2020, 2025],
    horizontal=True
)


# ============================================================
# MAP
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
    "The Google Earth Engine GeoTIFF classification outputs "
    "represent the full raster land-use maps."
)


# ============================================================
# CLASSIFICATION LEGEND
# ============================================================

st.subheader("Land-Use Classes")

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
    "The classified 2020 and 2025 satellite images are compared "
    "to determine changes in total classified forest area."
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
        "Net Change",
        f"+{net_forest_change_percentage:.2f}%"
    )


st.success(
    f"The model estimates a net increase of "
    f"{net_forest_change:,.2f} km² "
    f"({net_forest_change_percentage:.2f}%) "
    f"in classified forest area between 2020 and 2025."
)


st.divider()


# ============================================================
# 3. FOREST-LOSS FORMULA
# ============================================================

st.header("3. Forest-Loss Calculation")

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
    r"Forest\ Loss=A_{baseline}-A_{comparison}"
)

st.latex(
    r"Deforestation\ (\%)="
    r"\frac{A_{baseline}-A_{comparison}}"
    r"{A_{baseline}}\times100"
)


calc1, calc2 = st.columns(2)


with calc1:

    st.write("### Area Calculation")

    st.write(
        f"{forest_2020:,.2f} − "
        f"{forest_2025:,.2f}"
    )

    st.metric(
        "Formula Result",
        f"{formula_result:,.2f} km²"
    )


with calc2:

    st.write("### Percentage Calculation")

    st.write(
        f"({forest_2020:,.2f} − "
        f"{forest_2025:,.2f}) "
        f"÷ {forest_2020:,.2f} × 100"
    )

    st.metric(
        "Formula Result",
        f"{formula_percentage:.2f}%"
    )


st.info(
    "The negative forest-loss result indicates that the model "
    "estimated a net increase in total classified forest area."
)


st.divider()


# ============================================================
# 4. INTERACTIVE DEFORESTATION CALCULATOR
# ============================================================

st.header("4. 🌲 Interactive Deforestation Calculator")

st.write(
    "Enter forest-area values for any baseline and comparison "
    "period to calculate forest loss, forest gain and percentage change."
)


st.latex(
    r"Forest\ Loss=A_{baseline}-A_{comparison}"
)


st.latex(
    r"Deforestation\ (\%)="
    r"\frac{A_{baseline}-A_{comparison}}"
    r"{A_{baseline}}\times100"
)


calculator_col1, calculator_col2 = st.columns(2)


with calculator_col1:

    calculator_baseline = st.number_input(
        "Baseline Forest Area (km²)",
        min_value=0.01,
        value=float(round(forest_2020, 2)),
        step=1.0
    )


with calculator_col2:

    calculator_comparison = st.number_input(
        "Comparison Forest Area (km²)",
        min_value=0.0,
        value=float(round(forest_2025, 2)),
        step=1.0
    )


# ============================================================
# CALCULATOR LOGIC
# ============================================================

calculator_result = (
    calculator_baseline -
    calculator_comparison
)


calculator_percentage = (
    calculator_result /
    calculator_baseline *
    100
)


st.subheader("Calculator Result")


result1, result2, result3 = st.columns(3)


with result1:

    st.metric(
        "Baseline Area",
        f"{calculator_baseline:,.2f} km²"
    )


with result2:

    st.metric(
        "Comparison Area",
        f"{calculator_comparison:,.2f} km²"
    )


with result3:

    if calculator_result > 0:

        st.metric(
            "Forest Loss",
            f"{calculator_result:,.2f} km²"
        )

    elif calculator_result < 0:

        st.metric(
            "Forest Gain",
            f"{abs(calculator_result):,.2f} km²"
        )

    else:

        st.metric(
            "Forest Change",
            "0.00 km²"
        )


# ============================================================
# SHOW CALCULATION
# ============================================================

st.subheader("Calculation")

st.write(
    f"Forest Loss = "
    f"{calculator_baseline:,.2f} − "
    f"{calculator_comparison:,.2f}"
)


st.write(
    f"**Forest Loss Formula Result = "
    f"{calculator_result:,.2f} km²**"
)


st.write(
    f"Percentage = "
    f"({calculator_baseline:,.2f} − "
    f"{calculator_comparison:,.2f}) "
    f"÷ {calculator_baseline:,.2f} × 100"
)


# ============================================================
# CALCULATOR INTERPRETATION
# ============================================================

if calculator_result > 0:

    st.error(
        f"🌲 Forest Loss = "
        f"{calculator_result:,.2f} km²\n\n"
        f"Deforestation = "
        f"{calculator_percentage:.2f}%"
    )


elif calculator_result < 0:

    forest_gain = abs(
        calculator_result
    )

    forest_gain_percentage = abs(
        calculator_percentage
    )

    st.success(
        f"🌱 Forest Gain = "
        f"{forest_gain:,.2f} km²\n\n"
        f"Net Forest Increase = "
        f"{forest_gain_percentage:.2f}%"
    )


else:

    st.info(
        "No net change in forest area."
    )


st.caption(
    "A positive forest-loss result indicates a decrease in forest "
    "area. A negative result indicates a net increase in forest area."
)


st.divider()


# ============================================================
# 5. DEFORESTATION MAP
# ============================================================

st.header("5. Deforestation Map")

st.write(
    "The change-detection model identifies pixels classified as "
    "Forest in 2020 that became a non-forest land-use class in 2025."
)


st.markdown("""
### Change-Detection Logic

**Forest in 2020**

↓

**Pixel-by-Pixel Comparison**

↓

**Non-Forest in 2025**

↓

🔴 **Forest → Non-Forest Change**
""")


deforestation_map = folium.Map(
    location=[30.2, 79.2],
    zoom_start=7,
    tiles="OpenStreetMap"
)


folium.Marker(
    [30.3165, 78.0322],
    tooltip="Forest Change Analysis",
    popup="Uttarakhand: Forest → Non-Forest 2020–2025"
).add_to(deforestation_map)


st_folium(
    deforestation_map,
    width=None,
    height=500,
    returned_objects=[]
)


st.info(
    "The actual Forest → Non-Forest raster has been generated "
    "in Google Earth Engine as TerraScope_Deforestation_2020_2025."
)


st.warning(
    "Net forest-area change and gross deforestation are different. "
    "Forest loss can occur in some locations even when total classified "
    "forest area increases overall."
)


st.divider()


# ============================================================
# 6. AREA-WISE COMPARISON TABLE
# ============================================================

st.header("6. Area-Wise Comparison Table")


comparison_table = landuse_data.copy()


comparison_table.columns = [
    "Land-Use Category",
    "Area 2020 (km²)",
    "Area 2025 (km²)",
    "Change (km²)",
    "Change (%)"
]


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
    "Source: TerraScope AI Random Forest classification "
    "processed in Google Earth Engine."
)


# ============================================================
# CHANGE INTERPRETATION
# ============================================================

st.subheader("Change Interpretation")


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
# 7. LAND-USE CHANGE GRAPH
# ============================================================

st.header("7. Land-Use Change Graph")


graph_data = landuse_data.melt(

    id_vars="Land Use",

    value_vars=[
        "2020",
        "2025"
    ],

    var_name="Year",

    value_name="Area (km²)"
)


comparison_fig = px.bar(

    graph_data,

    x="Land Use",

    y="Area (km²)",

    color="Year",

    barmode="group",

    title="Land-Use Area Comparison: 2020 vs 2025"
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
        "Change": "Area Change (km²)"
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
# FOREST COMPARISON
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
# 8. AI MODEL
# ============================================================

st.header("8. AI Classification Model")


model_col1, model_col2 = st.columns(2)


with model_col1:

    st.subheader("Random Forest")

    st.write(
        "Random Forest combines multiple decision trees to classify "
        "satellite pixels according to their spectral characteristics."
    )

    st.markdown("""
    **Predictor variables:**

    - Blue Band — B2
    - Green Band — B3
    - Red Band — B4
    - Near Infrared — B8
    - SWIR-1 — B11
    - SWIR-2 — B12
    - NDVI
    - NDWI
    - NDBI
    - BSI
    """)


with model_col2:

    st.subheader("Classification Classes")

    st.markdown("""
    **0 — Forest**

    **1 — Agriculture**

    **2 — Built-up Area**

    **3 — Water Body**

    **4 — Barren Land**
    """)


st.divider()


# ============================================================
# 9. WORKING PROCESS
# ============================================================

st.header("9. Working Process")


st.markdown("""
### Step 1 — Satellite Image Acquisition

Sentinel-2 satellite imagery for **2020 and 2025** was
accessed using Google Earth Engine.

---

### Step 2 — Image Pre-processing

The satellite images were:

- filtered to Uttarakhand,
- filtered for cloud cover,
- cloud masked,
- composited, and
- clipped to the study area.

---

### Step 3 — Spectral Feature Extraction

Four additional spectral indices were calculated:

- **NDVI** — vegetation
- **NDWI** — water
- **NDBI** — built-up areas
- **BSI** — bare soil

---

### Step 4 — Training Samples

ESA WorldCover 2020 reference classes were used to generate
labelled samples for the five required land-use categories.

---

### Step 5 — Random Forest Training

The labelled samples were divided into training and testing
datasets.

A Random Forest classifier was trained using the spectral
bands and indices.

---

### Step 6 — Land-Use Classification

The trained model classified Sentinel-2 imagery into:

1. Forest
2. Agriculture
3. Built-up Area
4. Water Body
5. Barren Land

---

### Step 7 — Change Detection

The classified images from **2020 and 2025** were compared.

Pixels changing from:

**Forest → Non-Forest**

were identified as potential forest-loss areas.

---

### Step 8 — Area Calculation

Pixel areas were converted to square kilometres to quantify
land-use change and forest-area change.
""")


st.divider()


# ============================================================
# 10. MODEL OUTPUTS
# ============================================================

st.header("10. Model Outputs")


output1, output2 = st.columns(2)


with output1:

    st.subheader("🗺️ Land-Use Classification Map")

    st.write(
        "Spatial classification of the five land-use categories "
        "for 2020 and 2025."
    )


    st.subheader("📋 Area-Wise Comparison Table")

    st.write(
        "Quantitative comparison of land-use area between "
        "2020 and 2025."
    )


with output2:

    st.subheader("🌲 Deforestation Map")

    st.write(
        "Spatial detection of Forest → Non-Forest transitions."
    )


    st.subheader("📊 Land-Use Change Graph")

    st.write(
        "Visual comparison of changes in all five land-use categories."
    )


st.divider()


# ============================================================
# 11. DATA SOURCES
# ============================================================

st.header("11. Data Sources")


st.markdown("""
### Sentinel-2

Multispectral satellite imagery used as the primary input
for land-use classification.

**Source:** Copernicus Sentinel-2 / European Union Space Programme

---

### ESA WorldCover 2020

Used as the reference land-cover dataset for generating
labelled training samples.

**Source:** European Space Agency WorldCover

---

### Google Earth Engine

Used for:

- satellite-image access,
- cloud masking,
- image compositing,
- spectral-index calculation,
- Random Forest classification,
- change detection,
- area calculation, and
- raster/CSV export.
""")


st.divider()


# ============================================================
# RESULT SUMMARY
# ============================================================

st.header("Result Summary")


st.success(
    f"The model estimates classified forest area of "
    f"{forest_2020:,.2f} km² in 2020 and "
    f"{forest_2025:,.2f} km² in 2025."
)


st.info(
    f"This corresponds to a model-derived net forest increase of "
    f"{net_forest_change:,.2f} km² "
    f"({net_forest_change_percentage:.2f}%). "
    f"Forest → Non-Forest transitions are analysed separately "
    f"through the change-detection raster."
)


st.warning(
    "TerraScope AI results are model-derived remote-sensing estimates "
    "for this project and are not official government forest statistics."
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
