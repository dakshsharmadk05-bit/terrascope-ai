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

/* Main page spacing */

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* Main heading */

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

/* Formula box */

.formula-card {
    border: 1px solid rgba(128,128,128,0.25);
    border-left: 5px solid #2e7d32;
    padding: 20px;
    border-radius: 10px;
    margin-top: 10px;
    margin-bottom: 15px;
}

/* Footer */

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
    [
        "Random Forest",
        "Support Vector Machine"
    ]
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


st.sidebar.markdown("### Satellite Data")

st.sidebar.markdown("""
**Satellite:** Sentinel-2

**Baseline:** 2020

**Comparison:** 2025

**Study Area:** Uttarakhand
""")


st.sidebar.caption(
    "Final results will be derived from classified satellite imagery."
)


# ============================================================
# DEMONSTRATION DATA
# ============================================================
#
# IMPORTANT:
#
# These values are ONLY demonstration values.
#
# They are NOT official Uttarakhand statistics.
#
# They will later be replaced by results calculated from
# classified Sentinel-2 satellite imagery.
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
# FOREST CALCULATIONS
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
# PROTOTYPE WARNING
# ============================================================

st.warning(
    "⚠️ **Prototype Data:** The numerical land-use values currently "
    "displayed are demonstration values for testing TerraScope AI. "
    "They are not official Uttarakhand forest statistics."
)


# ============================================================
# MODEL OVERVIEW
# ============================================================

st.header("Model Overview")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Study Area",
        study_area
    )


with col2:

    st.metric(
        "Baseline Year",
        baseline_year
    )


with col3:

    st.metric(
        "Comparison Year",
        comparison_year
    )


with col4:

    st.metric(
        "AI Model",
        model_choice
    )


st.divider()


# ============================================================
# 1. LAND-USE CLASSIFICATION MAP
# ============================================================

st.header("1. Land-Use Classification Map")


st.write(
    "The satellite image is classified into five land-use "
    "categories using a supervised machine-learning model."
)


map_year = st.radio(
    "Select classification year",
    [2020, 2025],
    horizontal=True
)


# ============================================================
# CREATE MAP
# ============================================================

classification_map = folium.Map(

    location=[30.2, 79.2],

    zoom_start=7,

    tiles="OpenStreetMap"

)


# ============================================================
# UTTARAKHAND REFERENCE LOCATIONS
# ============================================================

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

        location=[
            latitude,
            longitude
        ],

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


# ============================================================
# DISPLAY MAP
# ============================================================

st_folium(

    classification_map,

    width=None,

    height=500,

    returned_objects=[]

)


st.info(
    "This map currently identifies the Uttarakhand study region. "
    "The final version will display the classified Sentinel-2 "
    "land-use raster."
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
# 2. DEFORESTATION ASSESSMENT
# ============================================================

st.header("2. Deforestation Assessment")


st.write(
    "Forest cover from the baseline year is compared with "
    "forest cover from the comparison year to estimate forest loss."
)


# ============================================================
# FOREST METRICS
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
        "Forest Loss",
        f"{forest_loss:,.0f} km²"
    )


with col4:

    st.metric(
        "Deforestation",
        f"{deforestation_percentage:.2f}%"
    )


# ============================================================
# DEFORESTATION FORMULA
# ============================================================

st.subheader("Deforestation Calculation")


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
    r"Deforestation\ (\%)="
    r"\frac{A_{2020}-A_{2025}}{A_{2020}}\times100"
)


# ============================================================
# AUTOMATIC CALCULATION
# ============================================================

st.subheader("Calculated Result")


calculation_col1, calculation_col2 = st.columns(2)


with calculation_col1:

    st.write("**Forest Loss Calculation**")

    st.write(
        f"{forest_2020:,.0f} − "
        f"{forest_2025:,.0f}"
    )

    st.success(
        f"Forest Loss = "
        f"{forest_loss:,.0f} km²"
    )


with calculation_col2:

    st.write("**Deforestation Percentage**")

    st.write(
        f"({forest_2020:,.0f} − "
        f"{forest_2025:,.0f}) "
        f"÷ {forest_2020:,.0f} × 100"
    )

    st.success(
        f"Deforestation = "
        f"{deforestation_percentage:.2f}%"
    )


st.caption(
    "The current calculation uses demonstration values. "
    "Once satellite classification is connected, these values "
    "will be calculated automatically from the classified images."
)


st.divider()


# ============================================================
# 3. DEFORESTATION MAP
# ============================================================

st.header("3. Deforestation Map")


st.write(
    "Deforestation is identified where an area classified as "
    "forest in 2020 changes to a non-forest class in 2025."
)


# ============================================================
# CREATE DEFORESTATION MAP
# ============================================================

deforestation_map = folium.Map(

    location=[30.2, 79.2],

    zoom_start=7,

    tiles="OpenStreetMap"

)


# ============================================================
# DEMONSTRATION FOREST-CHANGE AREAS
# ============================================================
#
# THESE ARE NOT REAL DEFORESTATION HOTSPOTS.
#
# They only demonstrate how the final map will work.
#
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

        fill_opacity=0.35,

        tooltip="Demonstration forest-change area"

    ).add_to(deforestation_map)


# ============================================================
# DISPLAY DEFORESTATION MAP
# ============================================================

st_folium(

    deforestation_map,

    width=None,

    height=500,

    returned_objects=[]

)


st.warning(
    "The red areas shown above are demonstration markers only. "
    "They are NOT verified deforestation locations."
)


st.divider()


# ============================================================
# 4. AREA-WISE COMPARISON TABLE
# ============================================================

st.header("4. Area-Wise Comparison Table")


st.write(
    "Land-use areas from the baseline and comparison years "
    "are compared below."
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

st.subheader("Change Interpretation")


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
    "The graph compares the area of each land-use category "
    "between 2020 and 2025."
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
# 6. AI CLASSIFICATION MODEL
# ============================================================

st.header("6. AI Classification Model")


model_col1, model_col2 = st.columns(2)


with model_col1:

    st.subheader("Selected Model")

    st.info(
        f"🤖 {model_choice}"
    )


    if model_choice == "Random Forest":

        st.write(
            "Random Forest combines multiple decision trees "
            "to classify satellite pixels according to their "
            "spectral characteristics."
        )

    else:

        st.write(
            "Support Vector Machine separates land-use classes "
            "using decision boundaries generated from labelled "
            "training samples."
        )


with model_col2:

    st.subheader("Classification Classes")

    st.markdown("""
    **1. Forest**

    **2. Agriculture**

    **3. Built-up Area**

    **4. Water Body**

    **5. Barren Land**
    """)


# ============================================================
# AI-GIS WORKFLOW
# ============================================================

st.subheader("AI-GIS Workflow")


st.markdown("""
**Sentinel-2 Satellite Image**

↓

**Image Pre-processing**

↓

**Labelled Training Samples**

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

**Deforestation Map**

↓

**Forest-Loss Calculation**
""")


st.divider()


# ============================================================
# 7. WORKING PROCESS
# ============================================================

st.header("7. Working Process")


st.markdown("""
### Step 1 — Download Satellite Images

Satellite images from two different years are obtained from
**Google Earth Engine, Copernicus Data Space, or Sentinel Hub**.

For TerraScope AI:

- Baseline image: **2020**
- Comparison image: **2025**
- Satellite: **Sentinel-2**
- Study area: **Uttarakhand**

---

### Step 2 — Pre-process and Crop Images

The satellite images are prepared by:

- selecting Uttarakhand as the study area,
- filtering cloud-covered images,
- selecting appropriate spectral bands,
- generating a cloud-reduced image, and
- cropping the image to the study area.

---

### Step 3 — Divide the Area into Land-Use Classes

Five land-use classes are used:

1. Forest
2. Agriculture
3. Built-up Area
4. Water Body
5. Barren Land

---

### Step 4 — Train the AI Model

Labelled samples representing each land-use category are
used to train the machine-learning classifier.

The model can use:

**Random Forest**

or

**Support Vector Machine**

---

### Step 5 — Classify the Satellite Image

The trained AI model predicts the land-use class of each
satellite pixel.

The result is the:

**Land-Use Classification Map**

---

### Step 6 — Compare Images from Two Years

The classified images from **2020 and 2025** are compared
pixel by pixel.

This identifies areas where land use has changed.

---

### Step 7 — Calculate Forest Loss

Areas classified as:

**Forest in 2020 → Non-Forest in 2025**

are identified as potential forest-loss areas.

Forest loss is then calculated using:

**Forest Loss = Forest Area 2020 − Forest Area 2025**

and:

**Deforestation (%) = [(Forest Area 2020 − Forest Area 2025) / Forest Area 2020] × 100**
""")


st.divider()


# ============================================================
# 8. OUTPUTS
# ============================================================

st.header("8. Model Outputs")


output1, output2 = st.columns(2)


with output1:

    st.subheader("🗺️ Land-Use Classification Map")

    st.write(
        "Displays the five classified land-use categories "
        "for the selected satellite image."
    )


    st.subheader("📋 Area-Wise Comparison Table")

    st.write(
        "Compares land-use areas between 2020 and 2025."
    )


with output2:

    st.subheader("🌲 Deforestation Map")

    st.write(
        "Shows areas changing from forest to non-forest."
    )


    st.subheader("📊 Land-Use Change Graph")

    st.write(
        "Visualises changes in the five land-use categories."
    )


st.divider()


# ============================================================
# DATA SOURCES
# ============================================================

st.header("Data Sources")


st.markdown("""
### Satellite Imagery

**Copernicus Sentinel-2**

Sentinel-2 multispectral satellite imagery is used for
land-use and land-cover classification.

### Satellite Data Access

Satellite data can be obtained through:

- Google Earth Engine
- Copernicus Data Space Ecosystem
- Sentinel Hub

### Study Area

**Uttarakhand, India**

### Machine-Learning Models

- Random Forest
- Support Vector Machine
""")


st.divider()


# ============================================================
# IMPORTANT NOTE
# ============================================================

st.warning("""
### Important Data Note

TerraScope AI is currently a working project prototype.

The numerical land-use areas and the red forest-change areas
currently displayed are **demonstration values only**.

They must not be presented as measured or official
deforestation statistics for Uttarakhand.

The final values will be obtained from classified Sentinel-2
satellite imagery for 2020 and 2025.
""")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

    <b>TerraScope AI</b><br>

    AI-GIS Land Use & Deforestation Model<br>

    Uttarakhand, India

    </div>
    """,
    unsafe_allow_html=True
)
