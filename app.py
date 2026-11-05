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
    }
)

default_landuse_data["Change"] = (
    default_landuse_data["2025"]
    - default_landuse_data["2020"]
)

default_landuse_data["Change (%)"] = (
    default_landuse_data["Change"]
    / default_landuse_data["2020"]
    * 100
)


# ============================================================
# FOREST RESULTS
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
    net_forest_change / forest_2020 * 100
)

formula_loss = forest_2020 - forest_2025

formula_percentage = (
    formula_loss / forest_2020 * 100
)


# ============================================================
# FUNCTIONS
# ============================================================

def safe_index(numerator, denominator):
    if denominator == 0:
        return None
    return numerator / denominator


def standardise_csv(df):

    df = df.copy()

    earth_engine_columns = {
        "land_use",
        "area_2020_km2",
        "area_2025_km2"
    }

    simple_columns = {
        "Land Use",
        "2020",
        "2025"
    }

    if earth_engine_columns.issubset(df.columns):

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

    elif simple_columns.issubset(df.columns):

        clean = df[
            [
                "Land Use",
                "2020",
                "2025"
            ]
        ].copy()

    else:
        return None

    clean["2020"] = pd.to_numeric(
        clean["2020"],
        errors="coerce"
    )

    clean["2025"] = pd.to_numeric(
        clean["2025"],
        errors="coerce"
    )

    clean["Change"] = (
        clean["2025"] - clean["2020"]
    )

    clean["Change (%)"] = np.where(
        clean["2020"] != 0,
        clean["Change"] / clean["2020"] * 100,
        np.nan
    )

    return clean


def create_base_map():

    m = folium.Map(
        location=[30.2, 79.2],
        zoom_start=7,
        tiles="OpenStreetMap"
    )

    return m


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
        "📡 Spectral Index Calculator",
        "🤖 AI Model",
        "📖 Methodology"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("### Project")

st.sidebar.write("**Study Area:** Uttarakhand, India")
st.sidebar.write("**Satellite:** Sentinel-2")
st.sidebar.write("**Years:** 2020 → 2025")
st.sidebar.write("**AI Model:** Random Forest")

st.sidebar.divider()

st.sidebar.markdown("### Land-Use Classes")

st.sidebar.write("🌲 Forest")
st.sidebar.write("🌾 Agriculture")
st.sidebar.write("🏙️ Built-up Area")
st.sidebar.write("💧 Water Body")
st.sidebar.write("🟫 Barren Land")

st.sidebar.divider()

st.sidebar.caption(
    "Sentinel-2 • ESA WorldCover • Google Earth Engine"
)


# ============================================================
# HEADER
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
# OVERVIEW
# ============================================================

if page == "🏠 Overview":

    st.markdown(
        '<div class="section-label">Project Dashboard</div>',
        unsafe_allow_html=True
    )

    st.header("Land-Use Change in Uttarakhand")

    st.write(
        "TerraScope AI combines satellite remote sensing, "
        "machine learning and GIS to classify land use and "
        "analyse forest change between 2020 and 2025."
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Study Area",
        "Uttarakhand"
    )

    c2.metric(
        "Satellite",
        "Sentinel-2"
    )

    c3.metric(
        "Period",
        "2020–2025"
    )

    c4.metric(
        "AI Model",
        "Random Forest"
    )

    st.divider()

    st.subheader("Key Results")

    r1, r2, r3, r4 = st.columns(4)

    r1.metric(
        "Forest Area 2020",
        f"{forest_2020:,.2f} km²"
    )

    r2.metric(
        "Forest Area 2025",
        f"{forest_2025:,.2f} km²"
    )

    r3.metric(
        "Net Forest Change",
        f"{net_forest_change:+,.2f} km²"
    )

    r4.metric(
        "Net Change",
        f"{net_forest_percentage:+.2f}%"
    )

    if net_forest_change >= 0:

        st.success(
            f"The model estimates a net forest-area increase "
            f"of {net_forest_change:,.2f} km² "
            f"({net_forest_percentage:.2f}%)."
        )

    else:

        st.error(
            f"The model estimates a net forest-area decrease "
            f"of {abs(net_forest_change):,.2f} km²."
        )

    st.warning(
        "These values are model-derived remote-sensing "
        "estimates and are not official government statistics."
    )

    st.divider()

    st.subheader("Study Area")

    overview_map = create_base_map()

    locations = [
        ("Dehradun", 30.3165, 78.0322),
        ("Haridwar", 29.9457, 78.1642),
        ("Nainital", 29.3919, 79.4542),
        ("Almora", 29.5892, 79.6467),
        ("Pithoragarh", 29.5829, 80.2182),
        ("Chamoli", 30.4036, 79.3220),
        ("Uttarkashi", 30.7268, 78.4354)
    ]

    for name, lat, lon in locations:

        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            tooltip=name,
            fill=True,
            fill_opacity=0.8
        ).add_to(overview_map)

    st_folium(
        overview_map,
        width=None,
        height=480,
        returned_objects=[]
    )

    st.divider()

    st.subheader("Project Outputs")

    o1, o2 = st.columns(2)

    with o1:

        st.markdown("### 🗺️ Land-Use Classification Map")

        st.write(
            "Classification of Uttarakhand into Forest, "
            "Agriculture, Built-up Area, Water Body and "
            "Barren Land."
        )

        st.markdown("### 📋 Area-Wise Comparison")

        st.write(
            "Comparison of classified land-use area "
            "between 2020 and 2025."
        )

    with o2:

        st.markdown("### 🌲 Deforestation Map")

        st.write(
            "Identification of Forest → Non-Forest "
            "pixel transitions."
        )

        st.markdown("### 📊 Land-Use Change Graph")

        st.write(
            "Graphical representation of land-use change."
        )


# ============================================================
# LAND-USE ANALYSIS
# ============================================================

elif page == "🗺️ Land-Use Analysis":

    st.markdown(
        '<div class="section-label">Satellite Classification</div>',
        unsafe_allow_html=True
    )

    st.header("Land-Use Analysis")

    st.write(
        "Upload an Earth Engine CSV or use the existing "
        "TerraScope AI classification results."
    )

    st.subheader("📂 Upload Land-Use Data")

    landuse_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        key="landuse_csv"
    )

    active_data = default_landuse_data.copy()

    if landuse_file is not None:

        try:

            uploaded_df = pd.read_csv(
                landuse_file
            )

            processed_df = standardise_csv(
                uploaded_df
            )

            if processed_df is not None:

                active_data = processed_df

                st.success(
                    "CSV successfully loaded and analysed."
                )

            else:

                st.warning(
                    "The uploaded CSV does not contain the "
                    "expected land-use columns."
                )

                st.dataframe(
                    uploaded_df,
                    use_container_width=True
                )

        except Exception as error:

            st.error(
                f"Could not read the file: {error}"
            )

    st.divider()

    selected_year = st.radio(
        "Select Classification Year",
        [2020, 2025],
        horizontal=True
    )

    st.subheader(
        f"Land-Use Classification Map — {selected_year}"
    )

    classification_map = create_base_map()

    folium.Marker(
        location=[30.3165, 78.0322],
        tooltip="Uttarakhand",
        popup=f"Classification Year: {selected_year}"
    ).add_to(classification_map)

    st_folium(
        classification_map,
        width=None,
        height=500,
        returned_objects=[]
    )

    st.caption(
        "The exported Google Earth Engine GeoTIFF can "
        "later be overlaid here as the classified raster."
    )

    st.subheader("Classification Legend")

    l1, l2, l3, l4, l5 = st.columns(5)

    l1.success("🌲 Forest")
    l2.warning("🌾 Agriculture")
    l3.error("🏙️ Built-up")
    l4.info("💧 Water")
    l5.markdown("🟫 **Barren Land**")

    st.divider()

    st.subheader("Area-Wise Comparison")

    display_table = active_data.copy()

    display_table.columns = [
        "Land-Use Category",
        "Area 2020 (km²)",
        "Area 2025 (km²)",
        "Change (km²)",
        "Change (%)"
    ]

    st.dataframe(
        display_table.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Land-Use Comparison Graph")

    graph_data = active_data.melt(
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
        title="Land-Use Area Comparison: 2020 vs 2025"
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

    st.subheader("Net Land-Use Change")

    change_fig = px.bar(
        active_data,
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
# FOREST CHANGE
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
        "Upload land-use results or use the default "
        "Earth Engine classification values."
    )

    st.subheader("📂 Upload Forest-Change Data")

    forest_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        key="forest_csv"
    )

    current_forest_2020 = forest_2020
    current_forest_2025 = forest_2025

    if forest_file is not None:

        try:

            uploaded_forest_df = pd.read_csv(
                forest_file
            )

            processed_forest_df = standardise_csv(
                uploaded_forest_df
            )

            if processed_forest_df is not None:

                forest_rows = processed_forest_df[
                    processed_forest_df[
                        "Land Use"
                    ].astype(str).str.lower() == "forest"
                ]

                if not forest_rows.empty:

                    current_forest_2020 = float(
                        forest_rows["2020"].iloc[0]
                    )

                    current_forest_2025 = float(
                        forest_rows["2025"].iloc[0]
                    )

                    st.success(
                        "Forest values extracted from CSV."
                    )

                st.dataframe(
                    processed_forest_df.round(2),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.warning(
                    "Could not identify standard land-use columns."
                )

                st.dataframe(
                    uploaded_forest_df,
                    use_container_width=True
                )

        except Exception as error:

            st.error(
                f"Could not process file: {error}"
            )

    current_change = (
        current_forest_2025
        - current_forest_2020
    )

    current_change_percent = (
        current_change
        / current_forest_2020
        * 100
        if current_forest_2020 != 0
        else 0
    )

    st.divider()

    f1, f2, f3, f4 = st.columns(4)

    f1.metric(
        "Forest Area 2020",
        f"{current_forest_2020:,.2f} km²"
    )

    f2.metric(
        "Forest Area 2025",
        f"{current_forest_2025:,.2f} km²"
    )

    f3.metric(
        "Net Forest Change",
        f"{current_change:+,.2f} km²"
    )

    f4.metric(
        "Net Change",
        f"{current_change_percent:+.2f}%"
    )

    st.divider()

    st.subheader("Forest-Loss Formula")

    st.latex(
        r"Forest\ Loss=A_{2020}-A_{2025}"
    )

    st.latex(
        r"Deforestation\ (\%)="
        r"\frac{A_{2020}-A_{2025}}{A_{2020}}\times100"
    )

    current_loss = (
        current_forest_2020
        - current_forest_2025
    )

    current_loss_percentage = (
        current_loss
        / current_forest_2020
        * 100
        if current_forest_2020 != 0
        else 0
    )

    x1, x2 = st.columns(2)

    x1.metric(
        "Formula Result",
        f"{current_loss:,.2f} km²"
    )

    x2.metric(
        "Percentage",
        f"{current_loss_percentage:.2f}%"
    )

    if current_loss > 0:

        st.error(
            f"Forest Loss: {current_loss:,.2f} km² | "
            f"Deforestation: {current_loss_percentage:.2f}%"
        )

    elif current_loss < 0:

        st.success(
            f"Net Forest Gain: {abs(current_loss):,.2f} km² | "
            f"Increase: {abs(current_loss_percentage):.2f}%"
        )

    else:

        st.info(
            "No net forest-area change."
        )

    st.divider()

    st.subheader("Forest Area Comparison")

    forest_graph_data = pd.DataFrame(
        {
            "Year": ["2020", "2025"],
            "Forest Area (km²)": [
                current_forest_2020,
                current_forest_2025
            ]
        }
    )

    forest_fig = px.bar(
        forest_graph_data,
        x="Year",
        y="Forest Area (km²)",
        text_auto=".2f",
        title="Forest Area: 2020 vs 2025"
    )

    st.plotly_chart(
        forest_fig,
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "Forest → Non-Forest Change Map"
    )

    st.write(
        "A pixel is flagged as potential forest loss "
        "when it is classified as Forest in 2020 and "
        "Non-Forest in 2025."
    )

    change_map = create_base_map()

    st_folium(
        change_map,
        width=None,
        height=500,
        returned_objects=[]
    )

    st.info(
        "The exported Earth Engine deforestation GeoTIFF "
        "can later be displayed on this map."
    )

    st.warning(
        "Net forest change and gross forest loss are "
        "different measures. Forest loss can occur in one "
        "location while forest gain occurs elsewhere."
    )


# ============================================================
# DEFORESTATION CALCULATOR
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
        "Enter forest-area values for any baseline and "
        "comparison period."
    )

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
        r"Forest\ Loss=A_{baseline}-A_{comparison}"
    )

    st.latex(
        r"Deforestation\ (\%)="
        r"\frac{A_{baseline}-A_{comparison}}"
        r"{A_{baseline}}\times100"
    )

    input1, input2 = st.columns(2)

    with input1:

        baseline_input = st.number_input(
            "Baseline Forest Area (km²)",
            min_value=0.01,
            value=float(round(forest_2020, 2)),
            step=1.0
        )

    with input2:

        comparison_input = st.number_input(
            "Comparison Forest Area (km²)",
            min_value=0.0,
            value=float(round(forest_2025, 2)),
            step=1.0
        )

    calculator_result = (
        baseline_input
        - comparison_input
    )

    calculator_percentage = (
        calculator_result
        / baseline_input
        * 100
    )

    st.divider()

    st.subheader("Calculation")

    st.write(
        f"Forest Loss = "
        f"{baseline_input:,.2f} − "
        f"{comparison_input:,.2f}"
    )

    st.write(
        f"**Result = "
        f"{calculator_result:,.2f} km²**"
    )

    st.write(
        f"Percentage = "
        f"({baseline_input:,.2f} − "
        f"{comparison_input:,.2f}) ÷ "
        f"{baseline_input:,.2f} × 100"
    )

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Baseline",
        f"{baseline_input:,.2f} km²"
    )

    r2.metric(
        "Comparison",
        f"{comparison_input:,.2f} km²"
    )

    if calculator_result > 0:

        r3.metric(
            "Forest Loss",
            f"{calculator_result:,.2f} km²"
        )

        st.error(
            f"🌲 Forest Loss = "
            f"{calculator_result:,.2f} km² | "
            f"Deforestation = "
            f"{calculator_percentage:.2f}%"
        )

    elif calculator_result < 0:

        gain = abs(
            calculator_result
        )

        gain_percent = abs(
            calculator_percentage
        )

        r3.metric(
            "Forest Gain",
            f"{gain:,.2f} km²"
        )

        st.success(
            f"🌱 Forest Gain = "
            f"{gain:,.2f} km² | "
            f"Net Increase = "
            f"{gain_percent:.2f}%"
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
        "in forest area. A negative result represents net gain."
    )


# ============================================================
# SPECTRAL INDEX CALCULATOR
# ============================================================

elif page == "📡 Spectral Index Calculator":

    st.markdown(
        '<div class="section-label">Remote Sensing Tool</div>',
        unsafe_allow_html=True
    )

    st.header(
        "📡 Spectral Index Calculator"
    )

    st.write(
        "Enter Sentinel-2 reflectance values to calculate "
        "NDVI, NDWI, NDBI and BSI."
    )

    st.info(
        "B2 = Blue | B3 = Green | B4 = Red | "
        "B8 = Near Infrared | B11 = SWIR"
    )

    st.divider()

    st.subheader("Sentinel-2 Band Values")

    c1, c2, c3 = st.columns(3)

    with c1:

        blue = st.number_input(
            "B2 — Blue",
            value=0.10,
            step=0.01,
            format="%.4f"
        )

        green = st.number_input(
            "B3 — Green",
            value=0.15,
            step=0.01,
            format="%.4f"
        )

    with c2:

        red = st.number_input(
            "B4 — Red",
            value=0.20,
            step=0.01,
            format="%.4f"
        )

        nir = st.number_input(
            "B8 — Near Infrared",
            value=0.60,
            step=0.01,
            format="%.4f"
        )

    with c3:

        swir = st.number_input(
            "B11 — SWIR",
            value=0.30,
            step=0.01,
            format="%.4f"
        )

    ndvi = safe_index(
        nir - red,
        nir + red
    )

    ndwi = safe_index(
        green - nir,
        green + nir
    )

    ndbi = safe_index(
        swir - nir,
        swir + nir
    )

    bsi = safe_index(
        (swir + red) - (nir + blue),
        (swir + red) + (nir + blue)
    )

    st.divider()

    st.subheader("Calculated Indices")

    i1, i2, i3, i4 = st.columns(4)

    i1.metric(
        "NDVI",
        "Undefined"
        if ndvi is None
        else f"{ndvi:.3f}"
    )

    i2.metric(
        "NDWI",
        "Undefined"
        if ndwi is None
        else f"{ndwi:.3f}"
    )

    i3.metric(
        "NDBI",
        "Undefined"
        if ndbi is None
        else f"{ndbi:.3f}"
    )

    i4.metric(
        "BSI",
        "Undefined"
        if bsi is None
        else f"{bsi:.3f}"
    )

    st.divider()

    st.subheader("🌿 NDVI — Vegetation")

    st.latex(
        r"NDVI=\frac{B8-B4}{B8+B4}"
    )

    st.write(
        "NDVI uses Near Infrared and Red. "
        "Healthy vegetation generally produces higher "
        "positive NDVI values."
    )

    st.subheader("💧 NDWI — Water")

    st.latex(
        r"NDWI=\frac{B3-B8}{B3+B8}"
    )

    st.write(
        "NDWI uses Green and Near Infrared and helps "
        "identify water bodies."
    )

    st.subheader("🏙️ NDBI — Built-up")

    st.latex(
        r"NDBI=\frac{B11-B8}{B11+B8}"
    )

    st.write(
        "NDBI uses SWIR and Near Infrared and helps "
        "identify built-up surfaces."
    )

    st.subheader("🟫 BSI — Bare Soil")

    st.latex(
        r"BSI="
        r"\frac{(B11+B4)-(B8+B2)}"
        r"{(B11+B4)+(B8+B2)}"
    )

    st.write(
        "BSI combines SWIR, Red, Near Infrared and Blue "
        "to highlight exposed soil and barren surfaces."
    )

    st.divider()

    st.subheader("Quick NDVI Interpretation")

    if ndvi is None:

        st.warning(
            "NDVI is undefined because the denominator is zero."
        )

    elif ndvi >= 0.6:

        st.success(
            "🌲 High NDVI — dense or healthy vegetation."
        )

    elif ndvi >= 0.3:

        st.info(
            "🌿 Moderate NDVI — moderate vegetation."
        )

    elif ndvi >= 0:

        st.warning(
            "Low NDVI — sparse vegetation or "
            "non-vegetated surface."
        )

    else:

        st.info(
            "Negative NDVI — commonly associated with "
            "water or non-vegetated surfaces."
        )

    st.caption(
        "These indices are predictor features. TerraScope AI "
        "combines them with the original Sentinel-2 bands "
        "inside the Random Forest classifier."
    )


# ============================================================
# AI MODEL
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
        "TerraScope AI uses supervised machine learning "
        "to classify Sentinel-2 satellite pixels."
    )

    st.divider()

    m1, m2 = st.columns(2)

    with m1:

        st.subheader("Model")

        st.metric(
            "Algorithm",
            "Random Forest"
        )

        st.metric(
            "Decision Trees",
            "100"
        )

        st.write(
            "Random Forest combines multiple decision trees "
            "to classify each satellite pixel."
        )

    with m2:

        st.subheader("Training")

        st.metric(
            "Reference Dataset",
            "ESA WorldCover 2020"
        )

        st.metric(
            "Train / Test Split",
            "80% / 20%"
        )

        st.write(
            "Stratified samples represent all five "
            "land-use categories."
        )

    st.divider()

    st.subheader("Predictor Variables")

    predictor_table = pd.DataFrame(
        {
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
            "Meaning": [
                "Blue",
                "Green",
                "Red",
                "Near Infrared",
                "SWIR 1",
                "SWIR 2",
                "Vegetation Index",
                "Water Index",
                "Built-up Index",
                "Bare Soil Index"
            ]
        }
    )

    st.dataframe(
        predictor_table,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Classification Classes")

    t1, t2, t3, t4, t5 = st.columns(5)

    t1.success("0 — Forest")
    t2.warning("1 — Agriculture")
    t3.error("2 — Built-up")
    t4.info("3 — Water")
    t5.markdown("🟫 **4 — Barren**")

    st.divider()

    st.subheader("AI Workflow")

    st.markdown(
        """
**Sentinel-2 imagery**

↓

**Cloud masking and median composite**

↓

**B2, B3, B4, B8, B11, B12 + spectral indices**

↓

**ESA WorldCover reference samples**

↓

**80% training / 20% testing**

↓

**Random Forest — 100 trees**

↓

**Five-class land-use classification**

↓

**2020 vs 2025 change detection**
"""
    )


# ============================================================
# METHODOLOGY
# ============================================================

elif page == "📖 Methodology":

    st.markdown(
        '<div class="section-label">Project Method</div>',
        unsafe_allow_html=True
    )

    st.header(
        "Methodology & Data Sources"
    )

    st.subheader("Objective")

    st.write(
        "To detect land-use changes and assess forest change "
        "in Uttarakhand using Sentinel-2 satellite imagery, "
        "machine learning and GIS."
    )

    st.divider()

    st.subheader("1. Data Acquisition")

    st.write(
        "Sentinel-2 Level-2A Surface Reflectance imagery "
        "for 2020 and 2025 is accessed through "
        "Google Earth Engine."
    )

    st.write(
        "Images are filtered to Uttarakhand and a "
        "scene-level cloud threshold of less than 30% is used."
    )

    st.subheader("2. Pre-processing")

    st.write(
        "Clouds, cloud shadows, cirrus and snow/ice are "
        "masked using the Sentinel-2 Scene Classification Layer."
    )

    st.write(
        "A median composite is created and clipped "
        "to Uttarakhand."
    )

    st.subheader("3. Feature Extraction")

    st.write(
        "The model uses B2, B3, B4, B8, B11 and B12, "
        "along with NDVI, NDWI, NDBI and BSI."
    )

    st.subheader("4. Training Data")

    st.write(
        "ESA WorldCover 2020 provides reference labels "
        "for Forest, Agriculture, Built-up Area, "
        "Water Body and Barren Land."
    )

    st.subheader("5. Random Forest")

    st.write(
        "The model uses 100 decision trees and an "
        "approximately 80:20 training/testing split."
    )

    st.subheader("6. Validation")

    st.write(
        "The held-out testing samples are used to generate "
        "a confusion matrix, Overall Accuracy and "
        "Cohen's Kappa."
    )

    st.subheader("7. Change Detection")

    st.write(
        "The 2020 and 2025 classified maps are compared "
        "pixel by pixel."
    )

    st.write(
        "Forest in 2020 changing to Non-Forest in 2025 "
        "is identified as potential forest loss."
    )

    st.subheader("8. Area Calculation")

    st.write(
        "Google Earth Engine's pixel-area image is used "
        "to calculate land-use area in square kilometres."
    )

    st.subheader("9. Outputs")

    st.write("1. Land-Use Classification Map")
    st.write("2. Deforestation Map")
    st.write("3. Area-Wise Comparison Table")
    st.write("4. Land-Use Change Graph")

    st.divider()

    st.subheader("Data Sources")

    st.write(
        "**Sentinel-2:** Copernicus / "
        "European Union Space Programme"
    )

    st.write(
        "**ESA WorldCover 2020:** "
        "European Space Agency"
    )

    st.write(
        "**Google Earth Engine:** "
        "Satellite processing, classification and change detection"
    )

    st.divider()

    st.subheader("Limitations")

    st.warning(
        "TerraScope AI results are model-derived "
        "remote-sensing estimates and should not be "
        "interpreted as official government forest statistics."
    )

    st.write(
        "Classification uncertainty may arise from spectral "
        "similarity, seasonal variation, cloud masking, "
        "reference-label quality and model error."
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
