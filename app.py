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
# CSS
# ============================================================

st.markdown("""
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
    font-size: 1.1rem;
    color: #8b949e;
    margin-top: 4px;
    margin-bottom: 20px;
}

.section-label {
    font-size: 0.9rem;
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
# FOREST RESULTS
# ============================================================

forest_2020 = float(
    landuse_data.loc[
        landuse_data["Land Use"] == "Forest",
        "2020"
    ].iloc[0]
)


forest_2025 = float(
    landuse_data.loc[
        landuse_data["Land Use"] == "Forest",
        "2025"
    ].iloc[0]
)


net_forest_change = (
    forest_2025 -
    forest_2020
)


net_forest_percentage = (
    net_forest_change /
    forest_2020 *
    100
)


formula_forest_loss = (
    forest_2020 -
    forest_2025
)


formula_percentage = (
    formula_forest_loss /
    forest_2020 *
    100
)


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
        "🧮 Deforestation Calculator",
        "🤖 AI Model",
        "📖 Methodology"
    ]
)


st.sidebar.divider()


st.sidebar.markdown("### Project")

st.sidebar.markdown("""
**Study Area**  
Uttarakhand, India

**Satellite**  
Sentinel-2

**Years**  
2020 → 2025

**AI Model**  
Random Forest
""")


st.sidebar.divider()


st.sidebar.markdown("### Land-Use Classes")

st.sidebar.markdown("""
🌲 Forest

🌾 Agriculture

🏙️ Built-up Area

💧 Water Body

🟫 Barren Land
""")


st.sidebar.divider()


st.sidebar.caption(
    "TerraScope AI • Google Earth Engine"
)


# ============================================================
# COMMON HEADER
# ============================================================

st.markdown(
    '<div class="hero-title">🌍 TerraScope AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-subtitle">'
    'AI-GIS Land Use Classification & Deforestation Assessment'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# PAGE 1 — OVERVIEW
# ============================================================

if page == "🏠 Overview":

    st.markdown(
        '<div class="section-label">Project Dashboard</div>',
        unsafe_allow_html=True
    )

    st.header(
        "Land-Use Change in Uttarakhand"
    )


    st.write(
        "TerraScope AI combines satellite remote sensing, "
        "machine learning and GIS to classify land use and "
        "analyse forest change between 2020 and 2025."
    )


    # --------------------------------------------------------
    # PROJECT CARDS
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "Study Area",
            "Uttarakhand"
        )


    with c2:

        st.metric(
            "Satellite",
            "Sentinel-2"
        )


    with c3:

        st.metric(
            "Analysis Period",
            "2020–2025"
        )


    with c4:

        st.metric(
            "AI Model",
            "Random Forest"
        )


    st.divider()


    # --------------------------------------------------------
    # KEY RESULTS
    # --------------------------------------------------------

    st.subheader("Key Results")


    r1, r2, r3, r4 = st.columns(4)


    with r1:

        st.metric(
            "Forest Area 2020",
            f"{forest_2020:,.2f} km²"
        )


    with r2:

        st.metric(
            "Forest Area 2025",
            f"{forest_2025:,.2f} km²"
        )


    with r3:

        st.metric(
            "Net Forest Change",
            f"+{net_forest_change:,.2f} km²"
        )


    with r4:

        st.metric(
            "Net Change",
            f"+{net_forest_percentage:.2f}%"
        )


    st.success(
        f"The classification estimates a net increase of "
        f"{net_forest_change:,.2f} km² "
        f"({net_forest_percentage:.2f}%) in total classified "
        f"forest area between 2020 and 2025."
    )


    st.warning(
        "These are model-derived remote-sensing estimates. "
        "They are not official government forest statistics."
    )


    st.divider()


    # --------------------------------------------------------
    # STUDY AREA MAP
    # --------------------------------------------------------

    st.subheader("Study Area")


    overview_map = folium.Map(

        location=[30.2, 79.2],

        zoom_start=7,

        tiles="OpenStreetMap"
    )


    cities = [

        ["Dehradun", 30.3165, 78.0322],

        ["Haridwar", 29.9457, 78.1642],

        ["Nainital", 29.3919, 79.4542],

        ["Almora", 29.5892, 79.6467],

        ["Pithoragarh", 29.5829, 80.2182],

        ["Chamoli", 30.4036, 79.3220],

        ["Uttarkashi", 30.7268, 78.4354]

    ]


    for name, lat, lon in cities:

        folium.CircleMarker(

            [lat, lon],

            radius=5,

            tooltip=name,

            color="#2e7d32",

            fill=True

        ).add_to(overview_map)


    st_folium(

        overview_map,

        width=None,

        height=480,

        returned_objects=[]
    )


    st.divider()


    # --------------------------------------------------------
    # PROJECT OUTPUTS
    # --------------------------------------------------------

    st.subheader("Project Outputs")


    o1, o2 = st.columns(2)


    with o1:

        st.markdown("""
        ### 🗺️ Land-Use Classification

        Classification of satellite imagery into:

        - Forest
        - Agriculture
        - Built-up Area
        - Water Body
        - Barren Land
        """)


        st.markdown("""
        ### 📋 Area Comparison

        Quantitative comparison of land-use areas
        between 2020 and 2025.
        """)


    with o2:

        st.markdown("""
        ### 🌲 Deforestation Detection

        Identification of pixels changing from:

        **Forest → Non-Forest**
        """)


        st.markdown("""
        ### 📊 Change Analysis

        Graphical analysis of land-use change
        between the two years.
        """)


# ============================================================
# PAGE 2 — LAND USE ANALYSIS
# ============================================================

elif page == "🗺️ Land-Use Analysis":

    st.markdown(
        '<div class="section-label">Satellite Classification</div>',
        unsafe_allow_html=True
    )

    st.header("Land-Use Analysis")


    st.write(
        "Explore the Random Forest classification results "
        "for the five required land-use categories."
    )


    # --------------------------------------------------------
    # YEAR SELECTION
    # --------------------------------------------------------

    selected_year = st.radio(

        "Classification Year",

        [2020, 2025],

        horizontal=True
    )


    st.info(
        f"Displaying classification information for "
        f"**{selected_year}**."
    )


    # --------------------------------------------------------
    # LAND USE MAP PLACEHOLDER
    # --------------------------------------------------------

    st.subheader(
        f"Land-Use Classification Map — {selected_year}"
    )


    classification_map = folium.Map(

        location=[30.2, 79.2],

        zoom_start=7,

        tiles="OpenStreetMap"
    )


    folium.Marker(

        [30.3165, 78.0322],

        tooltip="Uttarakhand",

        popup=(
            f"TerraScope AI Classification {selected_year}"
        )

    ).add_to(classification_map)


    st_folium(

        classification_map,

        width=None,

        height=500,

        returned_objects=[]
    )


    st.caption(
        "The exported Google Earth Engine classification "
        "GeoTIFF will replace this base-map view once raster "
        "processing is complete."
    )


    # --------------------------------------------------------
    # LEGEND
    # --------------------------------------------------------

    st.subheader("Classification Legend")


    l1, l2, l3, l4, l5 = st.columns(5)


    l1.success("🌲 Forest")
    l2.warning("🌾 Agriculture")
    l3.error("🏙️ Built-up")
    l4.info("💧 Water")
    l5.markdown("🟫 **Barren Land**")


    st.divider()


    # --------------------------------------------------------
    # AREA TABLE
    # --------------------------------------------------------

    st.subheader("Area-Wise Comparison")


    table = landuse_data.copy()


    table.columns = [

        "Land-Use Category",

        "Area 2020 (km²)",

        "Area 2025 (km²)",

        "Change (km²)",

        "Change (%)"
    ]


    numeric_columns = [

        "Area 2020 (km²)",

        "Area 2025 (km²)",

        "Change (km²)",

        "Change (%)"
    ]


    for col in numeric_columns:

        table[col] = table[col].round(2)


    st.dataframe(

        table,

        use_container_width=True,

        hide_index=True
    )


    st.divider()


    # --------------------------------------------------------
    # COMPARISON GRAPH
    # --------------------------------------------------------

    st.subheader("2020 vs 2025")


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

        title=(
            "Land-Use Area Comparison: "
            "2020 vs 2025"
        )
    )


    comparison_fig.update_layout(

        xaxis_title="Land-Use Category",

        yaxis_title="Area (km²)",

        legend_title="Year"
    )


    st.plotly_chart(

        comparison_fig,

        use_container_width=True
    )


    # --------------------------------------------------------
    # NET CHANGE
    # --------------------------------------------------------

    st.subheader("Net Land-Use Change")


    change_fig = px.bar(

        landuse_data,

        x="Land Use",

        y="Change",

        title=(
            "Net Change in Land-Use Area "
            "(2020–2025)"
        ),

        labels={
            "Change": "Change (km²)"
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


    st.caption(
        "Source: TerraScope AI Random Forest classification "
        "processed using Google Earth Engine."
    )


# ============================================================
# PAGE 3 — FOREST CHANGE
# ============================================================

elif page == "🌲 Forest Change":

    st.markdown(
        '<div class="section-label">Change Detection</div>',
        unsafe_allow_html=True
    )

    st.header(
        "Forest Change & Deforestation Assessment"
    )


    st.write(
        "Forest change is assessed using both total classified "
        "forest area and pixel-level Forest → Non-Forest transitions."
    )


    # --------------------------------------------------------
    # FOREST METRICS
    # --------------------------------------------------------

    f1, f2, f3, f4 = st.columns(4)


    with f1:

        st.metric(
            "Forest 2020",
            f"{forest_2020:,.2f} km²"
        )


    with f2:

        st.metric(
            "Forest 2025",
            f"{forest_2025:,.2f} km²"
        )


    with f3:

        st.metric(
            "Net Change",
            f"+{net_forest_change:,.2f} km²"
        )


    with f4:

        st.metric(
            "Net Change",
            f"+{net_forest_percentage:.2f}%"
        )


    st.success(
        "The model estimates a net increase in total "
        "classified forest area."
    )


    st.divider()


    # --------------------------------------------------------
    # FORMULA
    # --------------------------------------------------------

    st.subheader("Required Forest-Loss Formula")


    st.markdown(
        """
        <div class="formula-box">

        <b>Forest Loss</b> =
        Baseline Forest Area − Comparison Forest Area

        </div>
        """,
        unsafe_allow_html=True
    )


    st.latex(
        r"Forest\ Loss=A_{2020}-A_{2025}"
    )


    st.latex(
        r"Deforestation\ (\%)="
        r"\frac{A_{2020}-A_{2025}}"
        r"{A_{2020}}\times100"
    )


    c1, c2 = st.columns(2)


    with c1:

        st.metric(
            "Formula Result",
            f"{formula_forest_loss:,.2f} km²"
        )


    with c2:

        st.metric(
            "Formula Percentage",
            f"{formula_percentage:.2f}%"
        )


    st.info(
        "The negative forest-loss result indicates a "
        "net forest-area increase, rather than net deforestation."
    )


    st.divider()


    # --------------------------------------------------------
    # FOREST GRAPH
    # --------------------------------------------------------

    st.subheader("Forest Area Comparison")


    forest_df = pd.DataFrame({

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

        forest_df,

        x="Year",

        y="Forest Area (km²)",

        text_auto=".2f",

        title=(
            "Classified Forest Area: "
            "2020 vs 2025"
        )
    )


    st.plotly_chart(

        forest_fig,

        use_container_width=True
    )


    st.divider()


    # --------------------------------------------------------
    # DEFORESTATION MAP
    # --------------------------------------------------------

    st.subheader(
        "Forest → Non-Forest Change Map"
    )


    st.markdown("""
    **Detection logic**

    Forest in 2020  
    ↓  
    Corresponding pixel analysed in 2025  
    ↓  
    Non-Forest in 2025  
    ↓  
    **Potential Forest-Loss Pixel**
    """)


    change_map = folium.Map(

        location=[30.2, 79.2],

        zoom_start=7,

        tiles="OpenStreetMap"
    )


    st_folium(

        change_map,

        width=None,

        height=500,

        returned_objects=[]
    )


    st.info(
        "The actual Forest → Non-Forest raster is currently "
        "being exported from Google Earth Engine. It will be "
        "inserted here once the export is complete."
    )


    st.warning(
        "Net forest change and gross deforestation are not the "
        "same measure. Forest loss can occur in individual "
        "locations even when total forest area increases."
    )


# ============================================================
# PAGE 4 — DEFORESTATION CALCULATOR
# ============================================================

elif page == "🧮 Deforestation Calculator":

    st.markdown(
        '<div class="section-label">Interactive Tool</div>',
        unsafe_allow_html=True
    )

    st.header(
        "🌲 Deforestation Calculator"
    )


    st.write(
        "Enter forest-area values for any two periods to "
        "calculate forest loss, forest gain and percentage change."
    )


    # --------------------------------------------------------
    # FORMULA
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="formula-box">

        <b>Forest Loss</b> =
        Baseline Forest Area − Comparison Forest Area

        </div>
        """,
        unsafe_allow_html=True
    )


    st.latex(
        r"Forest\ Loss="
        r"A_{baseline}-A_{comparison}"
    )


    st.latex(
        r"Deforestation\ (\%)="
        r"\frac{A_{baseline}-A_{comparison}}"
        r"{A_{baseline}}\times100"
    )


    st.divider()


    # --------------------------------------------------------
    # INPUTS
    # --------------------------------------------------------

    input1, input2 = st.columns(2)


    with input1:

        baseline_input = st.number_input(

            "Baseline Forest Area (km²)",

            min_value=0.01,

            value=float(
                round(forest_2020, 2)
            ),

            step=1.0
        )


    with input2:

        comparison_input = st.number_input(

            "Comparison Forest Area (km²)",

            min_value=0.0,

            value=float(
                round(forest_2025, 2)
            ),

            step=1.0
        )


    # --------------------------------------------------------
    # CALCULATION
    # --------------------------------------------------------

    calculator_change = (
        baseline_input -
        comparison_input
    )


    calculator_percentage = (
        calculator_change /
        baseline_input *
        100
    )


    st.subheader("Calculation")


    st.write(
        f"Forest Loss = "
        f"{baseline_input:,.2f} − "
        f"{comparison_input:,.2f}"
    )


    st.write(
        f"**Result = "
        f"{calculator_change:,.2f} km²**"
    )


    st.write(
        f"Percentage = "
        f"({baseline_input:,.2f} − "
        f"{comparison_input:,.2f}) ÷ "
        f"{baseline_input:,.2f} × 100"
    )


    st.divider()


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    r1, r2, r3 = st.columns(3)


    r1.metric(
        "Baseline",
        f"{baseline_input:,.2f} km²"
    )


    r2.metric(
        "Comparison",
        f"{comparison_input:,.2f} km²"
    )


    if calculator_change > 0:

        r3.metric(
            "Forest Loss",
            f"{calculator_change:,.2f} km²"
        )


        st.error(
            f"🌲 Forest Loss: "
            f"{calculator_change:,.2f} km²\n\n"
            f"Deforestation: "
            f"{calculator_percentage:.2f}%"
        )


    elif calculator_change < 0:

        gain = abs(
            calculator_change
        )


        gain_percentage = abs(
            calculator_percentage
        )


        r3.metric(
            "Forest Gain",
            f"{gain:,.2f} km²"
        )


        st.success(
            f"🌱 Forest Gain: "
            f"{gain:,.2f} km²\n\n"
            f"Net Forest Increase: "
            f"{gain_percentage:.2f}%"
        )


    else:

        r3.metric(
            "Change",
            "0.00 km²"
        )


        st.info(
            "No net forest-area change."
        )


    st.caption(
        "A positive forest-loss result represents a decrease "
        "in forest area. A negative result represents a net "
        "increase in forest area."
    )


# ============================================================
# PAGE 5 — AI MODEL
# ============================================================

elif page == "🤖 AI Model":

    st.markdown(
        '<div class="section-label">Machine Learning</div>',
        unsafe_allow_html=True
    )

    st.header(
        "Random Forest Classification Model"
    )


    st.write(
        "TerraScope AI uses supervised machine learning to "
        "classify Sentinel-2 satellite pixels into five "
        "land-use categories."
    )


    st.divider()


    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    m1, m2 = st.columns(2)


    with m1:

        st.subheader("Model")

        st.metric(
            "Algorithm",
            "Random Forest"
        )


        st.write(
            "Random Forest combines multiple decision trees "
            "and assigns each pixel to a land-use category "
            "based on its spectral characteristics."
        )


    with m2:

        st.subheader("Training Reference")

        st.metric(
            "Reference Dataset",
            "ESA WorldCover 2020"
        )


        st.write(
            "ESA WorldCover reference classes were used to "
            "generate labelled samples for model training."
        )


    st.divider()


    # --------------------------------------------------------
    # INPUT VARIABLES
    # --------------------------------------------------------

    st.subheader("Predictor Variables")


    spectral_data = pd.DataFrame({

        "Variable": [

            "B2",
            "B3",
            "B4",
            "B8",
            "B11",
            "B12",
            "NDVI",
            "NDWI",
            "NDBI",
            "BSI"
        ],

        "Purpose": [

            "Blue spectral band",
            "Green spectral band",
            "Red spectral band",
            "Near Infrared",
            "Short-Wave Infrared 1",
            "Short-Wave Infrared 2",
            "Vegetation information",
            "Water information",
            "Built-up information",
            "Bare-soil information"
        ]
    })


    st.dataframe(

        spectral_data,

        use_container_width=True,

        hide_index=True
    )


    st.divider()


    # --------------------------------------------------------
    # CLASSES
    # --------------------------------------------------------

    st.subheader("Target Classes")


    t1, t2, t3, t4, t5 = st.columns(5)


    t1.success("0 — Forest")
    t2.warning("1 — Agriculture")
    t3.error("2 — Built-up")
    t4.info("3 — Water")
    t5.markdown("🟫 **4 — Barren**")


    st.divider()


    # --------------------------------------------------------
    # WORKFLOW
    # --------------------------------------------------------

    st.subheader("AI Workflow")


    st.markdown("""
    **Sentinel-2 Imagery**

    ↓

    **Cloud Masking & Pre-processing**

    ↓

    **Spectral Bands + NDVI + NDWI + NDBI + BSI**

    ↓

    **ESA WorldCover Reference Samples**

    ↓

    **Training / Testing Split**

    ↓

    **Random Forest Training**

    ↓

    **Pixel Classification**

    ↓

    **Five-Class Land-Use Map**
    """)


    st.info(
        "Model accuracy and confusion-matrix results can be "
        "added here once the Earth Engine computation/export "
        "results are available."
    )


# ============================================================
# PAGE 6 — METHODOLOGY
# ============================================================

elif page == "📖 Methodology":

    st.markdown(
        '<div class="section-label">Project Method</div>',
        unsafe_allow_html=True
    )

    st.header(
        "Methodology & Data Sources"
    )


    st.write(
        "The workflow follows the required AI-GIS land-use "
        "classification and deforestation assessment process."
    )


    st.divider()


    # --------------------------------------------------------
    # OBJECTIVE
    # --------------------------------------------------------

    st.subheader("Objective")


    st.write(
        "To detect land-use changes and estimate forest change "
        "in Uttarakhand by comparing satellite imagery from "
        "two different years using machine learning and GIS."
    )


    st.divider()


    # --------------------------------------------------------
    # INPUTS
    # --------------------------------------------------------

    st.subheader("Inputs")


    st.markdown("""
    - Sentinel-2 satellite imagery from **2020 and 2025**
    - GIS boundary of the selected study area
    - Five land-use categories:
      - Forest
      - Agriculture
      - Built-up Area
      - Water Body
      - Barren Land
    """)


    st.divider()


    # --------------------------------------------------------
    # WORKING PROCESS
    # --------------------------------------------------------

    st.subheader("Working Process")


    st.markdown("""
    ### 1. Satellite Image Acquisition

    Sentinel-2 imagery for 2020 and 2025 was accessed
    through **Google Earth Engine**.

    ### 2. Pre-processing

    Images were filtered to Uttarakhand, cloud masked,
    composited and clipped to the study area.

    ### 3. Land-Use Classes

    Five target classes were defined:

    **Forest • Agriculture • Built-up • Water • Barren**

    ### 4. AI Model Training

    ESA WorldCover 2020 reference labels were used to
    generate samples for training the Random Forest model.

    ### 5. Satellite Classification

    The trained classifier was applied to Sentinel-2 imagery
    to generate land-use maps for both years.

    ### 6. Change Detection

    The 2020 and 2025 classified images were compared
    to identify land-use transitions.

    ### 7. Forest-Loss Calculation

    Forest-area change was calculated using:

    **Forest Loss = Baseline Forest Area − Comparison Forest Area**

    Pixel-level Forest → Non-Forest transitions were also
    extracted to create the deforestation map.
    """)


    st.divider()


    # --------------------------------------------------------
    # OUTPUTS
    # --------------------------------------------------------

    st.subheader("Outputs")


    st.markdown("""
    **1. Land-Use Classification Map**

    **2. Deforestation Map**

    **3. Area-Wise Comparison Table**

    **4. Land-Use Change Graph**
    """)


    st.divider()


    # --------------------------------------------------------
    # SOURCES
    # --------------------------------------------------------

    st.subheader("Data Sources")


    st.markdown("""
    ### Sentinel-2

    Multispectral Earth-observation imagery used for
    classification.

    **Source:** Copernicus Sentinel-2 / European Union
    Space Programme

    ### ESA WorldCover 2020

    Global land-cover product used as a reference source
    for labelled training samples.

    **Source:** European Space Agency

    ### Google Earth Engine

    Used for satellite-data access, pre-processing,
    machine-learning classification, change detection,
    area calculation and raster export.
    """)


    st.divider()


    # --------------------------------------------------------
    # LIMITATIONS
    # --------------------------------------------------------

    st.subheader("Limitations")


    st.warning(
        "The land-use areas produced by TerraScope AI are "
        "model-derived remote-sensing estimates. They should "
        "not be interpreted as official government forest "
        "statistics."
    )


    st.write(
        "Classification uncertainty may arise from cloud masking, "
        "seasonal differences, spectral similarity between classes, "
        "reference-label quality and model generalisation."
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
