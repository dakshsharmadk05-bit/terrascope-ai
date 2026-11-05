# ============================================================
# TERRASCOPE AI
# AI-GIS LAND USE & DEFORESTATION MODEL
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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

/* Main page */

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* Header */

.main-title {
    font-size: 2.6rem;
    font-weight: 800;
    margin-bottom: 0;
}

.subtitle {
    color: #667085;
    font-size: 1.05rem;
    margin-top: 4px;
    margin-bottom: 25px;
}

/* Section headings */

.section-title {
    font-size: 1.55rem;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 5px;
}

/* Cards */

.info-card {
    background: #f8faf9;
    border: 1px solid #e5e7eb;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 15px;
}

.formula-card {
    background: #f5f9f6;
    border-left: 5px solid #2e7d32;
    padding: 20px;
    border-radius: 10px;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background-color: #f7f9f8;
}

.small-note {
    font-size: 0.85rem;
    color: #667085;
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

st.sidebar.title("TerraScope AI")

st.sidebar.caption(
    "Land Use & Deforestation Model"
)

st.sidebar.markdown("---")

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
    [
        "Random Forest",
        "Support Vector Machine"
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown("### Land-Use Classes")

st.sidebar.markdown("""
🌲 **Forest**

🌾 **Agriculture**

🏙️ **Built-up Area**

💧 **Water Body**

🟫 **Barren Land**
""")

st.sidebar.markdown("---")

st.sidebar.markdown("### Satellite Data")

st.sidebar.markdown("""
**Satellite:** Sentinel-2

**Baseline:** 2020

**Comparison:** 2025

**Study Area:** Uttarakhand
""")

st.sidebar.caption(
    "Final classified values should be derived from processed satellite imagery."
)


# ============================================================
# DEMONSTRATION DATA
# ============================================================
#
# IMPORTANT:
# These values are ONLY for demonstrating the working of the
# Streamlit application.
#
# They are NOT official Uttarakhand forest statistics.
#
# When satellite classification results are available,
# replace these values with the calculated areas.
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
).round(2)


# ============================================================
# FOREST / DEFORESTATION CALCULATIONS
# ============================================================

forest_2020 = landuse_data.loc[
    landuse_data["Land Use"] == "Forest",
    "2020"
].iloc[0]

forest_2025 = landuse_data.loc[
    landuse_data["Land Use"] == "Forest",
    "2025"
].iloc[0]


forest_loss = max(
    forest_2020 - forest_2025,
    0
)


if forest_2020 > 0:

    deforestation_percentage = (
        forest_loss /
        forest_2020
    ) * 100

else:

    deforestation_percentage = 0


# ============================================================
# DATA STATUS WARNING
# ============================================================

st.warning(
    "⚠️ **Prototype Data:** The numerical land-use values currently "
    "shown in TerraScope AI are demonstration values used to test the "
    "model interface. They are NOT official Uttarakhand forest statistics. "
    "Final values must be generated from the classified satellite imagery."
)


# ============================================================
# MODEL OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">Model Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Study Area",
        "Uttarakhand"
    )

with col2:
    st.metric(
        "Baseline",
        str(baseline_year)
    )

with col3:
    st.metric(
        "Comparison",
        str(comparison_year)
    )

with col4:
    st.metric(
        "AI Model",
        model_choice
    )


st.divider()


# ============================================================
# 1. LAND-USE CLASSIFICATION
# ============================================================

st.header("1. Land-Use Classification")

st.write(
    "Satellite imagery is classified into five land-use categories "
    "using a supervised machine-learning model."
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
    tiles=None
)

folium.TileLayer(
    tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attr="© OpenStreetMap contributors",
    name="OpenStreetMap",
    control=True
).add_to(classification_map)


# ============================================================
# STUDY AREA MARKERS
# ============================================================

locations = [
    ["Dehradun", 30.3165, 78.0322],
    ["Nainital", 29.3919, 79.4542],
    ["Almora", 29.5892, 79.6467],
    ["Pithoragarh", 29.5829, 80.2182],
    ["Chamoli", 30.4036, 79.3220],
    ["Uttarkashi", 30.7268, 78.4354],
    ["Haridwar", 29.9457, 78.1642]
]


for place, latitude, longitude in locations:

    folium.CircleMarker(
        location=[latitude, longitude],
        radius=5,
        tooltip=place,
        popup=f"{place} | Classification Year: {map_year}",
        color="#2e7d32",
        fill=True,
        fill_opacity=0.8
    ).add_to(classification_map)


folium.LayerControl().add_to(
    classification_map
)


st_folium(
    classification_map,
    width=None,
    height=500,
    returned_objects=[]
)


st.info(
    "The current map identifies the Uttarakhand study region. "
    "The final version will overlay the classified Sentinel-2 "
    "raster produced by the machine-learning model."
)


# ============================================================
# LAND-USE LEGEND
# ============================================================

st.markdown("#### Classification Classes")

c1, c2, c3, c4, c5 = st.columns(5)

c1.success("🌲 Forest")
c2.warning("🌾 Agriculture")
c3.error("🏙️ Built-up")
c4.info("💧 Water Body")
c5.markdown("🟫 **Barren Land**")


st.divider()


# ============================================================
# 2. DEFORESTATION ASSESSMENT
# ============================================================

st.header("2. Deforestation Assessment")

st.write(
    "Forest cover from the baseline classified image is compared "
    "with the comparison-year classified image to identify forest "
    "converted into non-forest land."
)


# ============================================================
# DEFORESTATION METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        f"Forest Area {baseline_year}",
        f"{forest_2020:,.0f} km²"
    )


with col2:

    st.metric(
        f"Forest Area {comparison_year}",
        f"{forest_2025:,.0f} km²"
    )


with col3:

    st.metric(
        "Estimated Forest Loss",
        f"{forest_loss:,.0f} km²"
    )


with col4:

    st.metric(
        "Deforestation",
        f"{deforestation_percentage:.2f}%"
    )


# ============================================================
# FORMULA
# ============================================================

st.markdown("### Deforestation Calculation")

st.markdown(
    '<div class="formula-card">'
    '<b>Forest Loss</b> = Forest Area in Baseline Year '
    '− Forest Area in Comparison Year'
    '</div>',
    unsafe_allow_html=True
)

st.write("")

st.latex(
    r"Forest\ Loss = A_{2020} - A_{2025}"
)

st.latex(
    r"Deforestation\ (\%)="
    r"\frac{A_{2020}-A_{2025}}{A_{2020}}\times100"
)


# ============================================================
# SHOW CALCULATION
# ============================================================

st.markdown("#### Current Calculation")

st.write(
    f"Forest Loss = {forest_2020:,.0f} − "
    f"{forest_2025:,.0f}"
)

st.write(
    f"**Forest Loss = {forest_loss:,.0f} km²**"
)

st.write(
    f"Deforestation (%) = "
    f"({forest_2020:,.0f} − {forest_2025:,.0f}) "
    f"/ {forest_2020:,.0f} × 100"
)

st.success(
    f"Estimated Deforestation = "
    f"{deforestation_percentage:.2f}%"
)

st.caption(
    "This calculation currently uses demonstration values. "
    "It will automatically use satellite-derived forest areas "
    "when the final classification results are connected."
)


# ============================================================
# 3. DEFORESTATION MAP
# ============================================================

st.header("3. Deforestation Map")

st.write(
    "The deforestation layer represents locations where pixels "
    "classified as forest in 2020 become a non-forest land-use "
    "class in 2025."
)


deforestation_map = folium.Map(
    location=[30.2, 79.2],
    zoom_start=7,
    tiles=None
)


folium.TileLayer(
    tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attr="© OpenStreetMap contributors",
    name="OpenStreetMap"
).add_to(deforestation_map)


# ============================================================
# DEMONSTRATION CHANGE LOCATIONS
# ============================================================
#
# These are visual placeholders ONLY.
# They are NOT actual deforestation hotspots.
# ============================================================

demo_change_locations = [
    [30.31, 78.10],
    [29.95, 78.20],
    [29.45, 79.40],
    [29.60, 79.70],
    [30.40, 79.30]
]


for point in demo_change_locations:

    folium.Circle(
        location=point,
        radius=9000,
        color="#c62828",
        fill=True,
        fill_color="#ef5350",
        fill_opacity=0.30,
        tooltip="Demonstration forest-change area"
    ).add_to(deforestation_map)


st_folium(
    deforestation_map,
    width=None,
    height=500,
    returned_objects=[]
)


st.warning(
    "Red areas on this prototype map are demonstration markers only. "
    "They are NOT verified deforestation locations. Final forest-loss "
    "pixels must be generated by comparing the classified 2020 and "
    "2025 satellite images."
)


st.divider()


# ============================================================
# 4. AREA-WISE COMPARISON TABLE
# ============================================================

st.header("4. Area-Wise Comparison Table")

st.write(
    "The table compares the estimated area occupied by each "
    "land-use class between the two selected years."
)


comparison_table = landuse_data.copy()

comparison_table.columns = [
    "Land-Use Category",
    "Area 2020 (km²)",
    "Area 2025 (km²)",
    "Change (km²)",
    "Change (%)"
]


st.dataframe(
    comparison_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# CHANGE INTERPRETATION
# ============================================================

st.markdown("#### Change Interpretation")

interpretation_data = landuse_data.copy()

interpretation_data["Trend"] = np.where(
    interpretation_data["Change"] > 0,
    "Increase",
    np.where(
        interpretation_data["Change"] < 0,
        "Decrease",
        "No Change"
    )
)

st.dataframe(
    interpretation_data[
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
# 5. LAND-USE CHANGE GRAPH
# ============================================================

st.header("5. Land-Use Change Graph")

st.write(
    "The graph compares land-use area between 2020 and 2025."
)


graph_data = landuse_data.melt(

    id_vars="Land Use",

    value_vars=[
        "2020",
        "2025"
    ],

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

    legend_title="Year",

    hovermode="x unified"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# LAND-USE CHANGE GRAPH
# ============================================================

st.markdown("### Net Land-Use Change")


change_fig = px.bar(

    landuse_data,

    x="Land Use",

    y="Change",

    title="Net Change in Land-Use Area (2020–2025)",

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


st.divider()


# ============================================================
# 6. AI MODEL
# ============================================================

st.header("6. AI Classification Model")


left, right = st.columns([1, 1])


with left:

    st.markdown("### Selected Model")

    st.info(
        f"🤖 {model_choice}"
    )

    if model_choice == "Random Forest":

        st.write(
            "Random Forest uses multiple decision trees to classify "
            "satellite pixels according to their spectral characteristics."
        )

    else:

        st.write(
            "Support Vector Machine separates land-use classes by "
            "finding decision boundaries between labelled training samples."
        )


with right:

    st.markdown("### Input Classes")

    st.markdown("""
    **1. Forest**

    **2. Agriculture**

    **3. Built-up Area**

    **4. Water Body**

    **5. Barren Land**
    """)


# ============================================================
# AI WORKFLOW
# ============================================================

st.markdown("### AI-GIS Workflow")

st.markdown("""
**Satellite Image**

↓  

**Image Pre-processing**

↓

**Training Samples**

↓

**Random Forest / Support Vector Machine**

↓

**Pixel Classification**

↓

**Land-Use Classification Map**

↓

**2020 vs 2025 Comparison**

↓

**Forest → Non-Forest Detection**

↓

**Deforestation Map + Area Calculation**
""")


st.divider()


# ============================================================
# 7. METHODOLOGY
# ============================================================

st.header("7. Methodology")


st.markdown("""
### Step 1 — Satellite Image Acquisition

Satellite images for **2020 and 2025** are obtained from
**Sentinel-2** through platforms such as Google Earth Engine
or Copernicus Data Space.

---

### Step 2 — Image Pre-processing

Satellite images are prepared by:

- selecting the study area,
- filtering cloud-covered images,
- creating cloud-reduced composites,
- selecting required spectral bands, and
- cropping the imagery to Uttarakhand.

---

### Step 3 — Land-Use Classes

Training samples are created for five categories:

1. Forest
2. Agriculture
3. Built-up Area
4. Water Body
5. Barren Land

---

### Step 4 — AI Model Training

The labelled training samples are used to train a
**Random Forest** or **Support Vector Machine** classifier.

---

### Step 5 — Image Classification

The trained model predicts the land-use category of satellite
pixels and generates a classified land-use map.

---

### Step 6 — Change Detection

The classified **2020** and **2025** images are compared.

Land-use transitions are detected by comparing the class of
each corresponding pixel.

---

### Step 7 — Deforestation Detection

Pixels classified as:

**Forest in 2020 → Non-Forest in 2025**

are identified as potential forest-loss areas.

Forest loss and percentage deforestation are then calculated.
""")


st.divider()


# ============================================================
# 8. EXPECTED OUTPUTS
# ============================================================

st.header("8. Model Outputs")


output1, output2 = st.columns(2)


with output1:

    st.markdown("""
    ### 🗺️ Land-Use Classification Map

    Displays:

    - Forest
    - Agriculture
    - Built-up Area
    - Water Body
    - Barren Land
    """)


    st.markdown("""
    ### 📋 Area-Wise Comparison Table

    Compares land-use area between:

    **2020 and 2025**
    """)


with output2:

    st.markdown("""
    ### 🌲 Deforestation Map

    Identifies areas changing from:

    **Forest → Non-Forest**
    """)


    st.markdown("""
    ### 📊 Land-Use Change Graph

    Visualises changes in the five land-use categories
    between the two years.
    """)


st.divider()


# ============================================================
# DATA SOURCES
# ============================================================

st.header("Data Sources")


st.markdown("""
**Satellite imagery**

Copernicus Sentinel-2 / European Union Space Programme

**Satellite data access**

Google Earth Engine or Copernicus Data Space Ecosystem

**Study Area**

Uttarakhand, India

**Machine-Learning Methods**

Random Forest / Support Vector Machine

**GIS Processing**

Satellite-image classification and land-use change detection
""")


# ============================================================
# FINAL DISCLAIMER
# ============================================================

st.warning("""
### Important Data Note

TerraScope AI is currently operating as a project prototype.

The numerical land-use areas and red forest-change locations
displayed in this version are **demonstration values** and must
not be cited as measured deforestation in Uttarakhand.

The final results should be generated from classified Sentinel-2
satellite imagery for 2020 and 2025.
""")


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#667085;">
    <b>TerraScope AI</b><br>
    AI-GIS Land Use & Deforestation Model<br>
    Uttarakhand, India
    </div>
    """,
    unsafe_allow_html=True
)
