from pathlib import Path
import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import rasterio
from rasterio.io import MemoryFile

st.set_page_config(page_title="TerraScope AI", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")
st.markdown('''<style>
.stApp {background:linear-gradient(135deg,#07131e 0%,#0b1c28 55%,#07151b 100%);color:#e8f5f1}
[data-testid="stSidebar"] {background:#091824;border-right:1px solid #204c51}
.block-container {max-width:1400px;padding-top:1.5rem}
h1,h2,h3 {letter-spacing:-.025em;color:#e6fff5}
[data-testid="stMetric"] {background:#102633;border:1px solid #1d5555;padding:15px;border-radius:13px}
[data-testid="stMetricLabel"] {color:#9ad5c9}
[data-testid="stMetricValue"] {color:#e8fff8}
.stButton>button[kind="primary"] {background:#10a98b;color:white;border:0}
</style>''', unsafe_allow_html=True)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "Website_Data"
MAP_PATH = DATA / "maps" / "Uttarakhand_Vegetation_Change_2016_2025_Expanded.png"
CSV_PATH = DATA / "statistics" / "Uttarakhand_Vegetation_Change_Statistics_Expanded.csv"
REQUIRED = {
    "NDVI": ["NIR", "Red"], "NDWI": ["Green", "NIR"],
    "NDMI": ["NIR", "SWIR1"], "NBR": ["NIR", "SWIR2"],
    "NDBI": ["SWIR1", "NIR"], "EVI": ["NIR", "Red", "Blue"],
    "SAVI": ["NIR", "Red"], "GNDVI": ["NIR", "Green"],
    "BSI": ["SWIR1", "Red", "NIR", "Blue"]
}


def divide(a, b):
    a, b = np.broadcast_arrays(np.asarray(a, dtype=float), np.asarray(b, dtype=float))
    result = np.full(a.shape, np.nan, dtype=float)
    np.divide(a, b, out=result, where=np.isfinite(a) & np.isfinite(b) & (np.abs(b) > 1e-12))
    return result


def calculate(index, b):
    if index == "NDVI": return divide(b["NIR"]-b["Red"], b["NIR"]+b["Red"])
    if index == "NDWI": return divide(b["Green"]-b["NIR"], b["Green"]+b["NIR"])
    if index == "NDMI": return divide(b["NIR"]-b["SWIR1"], b["NIR"]+b["SWIR1"])
    if index == "NBR": return divide(b["NIR"]-b["SWIR2"], b["NIR"]+b["SWIR2"])
    if index == "NDBI": return divide(b["SWIR1"]-b["NIR"], b["SWIR1"]+b["NIR"])
    if index == "EVI": return divide(2.5*(b["NIR"]-b["Red"]), b["NIR"]+6*b["Red"]-7.5*b["Blue"]+1)
    if index == "SAVI": return divide(1.5*(b["NIR"]-b["Red"]), b["NIR"]+b["Red"]+0.5)
    if index == "GNDVI": return divide(b["NIR"]-b["Green"], b["NIR"]+b["Green"])
    if index == "BSI": return divide((b["SWIR1"]+b["Red"])-(b["NIR"]+b["Blue"]), (b["SWIR1"]+b["Red"])+(b["NIR"]+b["Blue"]))
    raise ValueError("Unknown index")


def load_raster(upload):
    with MemoryFile(upload.getvalue()) as mem:
        with mem.open() as src:
            if src.width * src.height * src.count > 45_000_000:
                raise ValueError("Raster exceeds hosted limit of 45 million samples. Clip or downsample first.")
            return src.read(masked=True), src.profile.copy(), src.descriptions


def grid_matches(a, b):
    return all(a[k] == b[k] for k in ("width", "height", "transform", "crs"))


def pixel_area_km2(profile):
    crs = profile["crs"]
    if crs is None or not crs.is_projected:
        raise ValueError("Area analysis requires a projected CRS with metre units; preferably an equal-area projection.")
    if (crs.linear_units or "").lower() not in ("metre", "meter", "metres", "meters", "m"):
        raise ValueError("Projected coordinates must be in metres.")
    t = profile["transform"]
    return abs(t.a*t.e-t.b*t.d)/1_000_000


def as_float(masked):
    return np.asarray(masked.filled(np.nan), dtype=float)


def geotiff_bytes(array, profile):
    arr = np.asarray(array, dtype="float32")
    meta = profile.copy()
    meta.update(driver="GTiff", count=1, height=arr.shape[0], width=arr.shape[1], dtype="float32", nodata=-9999.0)
    with MemoryFile() as mem:
        with mem.open(**meta) as ds:
            ds.write(np.where(np.isfinite(arr), arr, -9999.0).astype("float32"), 1)
        return mem.read()


def show_result(array, profile, name):
    valid = np.asarray(array)[np.isfinite(array)]
    if not valid.size:
        st.warning("No valid output pixels. Check scaling, band assignments and NoData masks.")
        return
    cols = st.columns(4)
    for col, label, value in zip(cols, ("Mean", "Median", "Minimum", "Maximum"), (valid.mean(), np.median(valid), valid.min(), valid.max())):
        col.metric(label, f"{value:.4f}")
    st.caption(f"{valid.size:,} valid pixels. Raster preview is not a georeferenced map.")
    stride = max(1, int(np.ceil(max(array.shape)/700)))
    st.image(np.ma.masked_invalid(np.asarray(array)[::stride, ::stride]), caption=f"{name} raster preview", clamp=True)
    sample = valid[::max(1, len(valid)//150000)]
    st.plotly_chart(px.histogram(x=sample, nbins=60, labels={"x": name}, title=f"{name} distribution", template="plotly_dark"), use_container_width=True)
    st.download_button("Download result GeoTIFF", geotiff_bytes(array, profile), f"{name.lower().replace(' ', '_')}.tif", mime="image/tiff")
    stats = pd.DataFrame([{"metric": k, "value": v} for k, v in {"mean": valid.mean(), "median": np.median(valid), "min": valid.min(), "max": valid.max(), "valid_pixels": valid.size}.items()])
    st.download_button("Download statistics CSV", stats.to_csv(index=False), f"{name.lower().replace(' ', '_')}_stats.csv", mime="text/csv")


def landuse_table(df):
    if not {"Class", "Baseline", "Comparison"}.issubset(df.columns):
        raise ValueError("CSV must contain Class, Baseline, Comparison.")
    d = df[["Class", "Baseline", "Comparison"]].copy()
    for col in ("Baseline", "Comparison"):
        d[col] = pd.to_numeric(d[col], errors="coerce")
    if d[["Baseline", "Comparison"]].isna().any().any() or (d[["Baseline", "Comparison"]] < 0).any().any():
        raise ValueError("Areas must be finite nonnegative numbers.")
    if d["Class"].astype(str).str.strip().eq("").any() or d["Class"].duplicated().any():
        raise ValueError("Class names must be nonempty and unique.")
    d["Change (km²)"] = d["Comparison"] - d["Baseline"]
    d["Change (%)"] = np.where(d["Baseline"] > 0, 100*d["Change (km²)"]/d["Baseline"], np.nan)
    return d


def classified_pair(prefix):
    f1 = st.file_uploader("Baseline classified GeoTIFF", type=["tif", "tiff"], key=prefix+"a")
    f2 = st.file_uploader("Comparison classified GeoTIFF", type=["tif", "tiff"], key=prefix+"b")
    if f1 is None or f2 is None:
        return None
    a, pa, _ = load_raster(f1)
    b, pb, _ = load_raster(f2)
    if a.shape[0] != 1 or b.shape[0] != 1 or not grid_matches(pa, pb):
        raise ValueError("Both rasters must be single-band categorical maps on the same grid and CRS.")
    aa, bb = as_float(a[0]), as_float(b[0])
    valid = np.isfinite(aa) & np.isfinite(bb)
    if not valid.any():
        raise ValueError("No overlapping valid pixels.")
    return aa, bb, valid, pixel_area_km2(pa), pa


def read_change_stats(path):
    df = pd.read_csv(path)
    if not {"Category", "Pixels", "Area_km2"}.issubset(df.columns):
        raise ValueError("Expanded CSV must have Category, Pixels and Area_km2 columns.")
    areas = {}
    for _, row in df.iterrows():
        key = str(row["Category"]).strip().lower()
        areas[key] = float(row["Area_km2"])
    required = ("stable vegetation", "vegetation loss", "vegetation gain", "stable non-vegetation", "common observed area", "net vegetation change")
    missing = [x for x in required if x not in areas]
    if missing:
        raise ValueError("CSV missing categories: " + ", ".join(missing))
    return df, areas


st.sidebar.title("🌍 TerraScope AI")
st.sidebar.caption("GEOSPATIAL INTELLIGENCE / RESEARCH PREVIEW")
page = st.sidebar.radio("Navigation", ["🏠 Command Center", "🛰️ Vegetation Intelligence", "🌿 Spectral Index Calculator", "🗺️ Land-Use Calculator", "🌲 Forest Change Calculator", "🔄 Change Detection", "📘 Methodology"])
st.sidebar.divider()
st.sidebar.caption("Raster processing runs in Streamlit with Rasterio + NumPy. QGIS is used to prepare the showcased study.")

if page == "🏠 Command Center":
    st.title("TERRASCOPE AI")
    st.caption("ENVIRONMENTAL INTELLIGENCE • SATELLITE ANALYTICS • GEOSPATIAL RESEARCH")
    st.markdown("### Mission control")
    c1, c2, c3 = st.columns(3)
    c1.metric("Spectral indices", "9")
    c2.metric("Analysis inputs", "Manual + GeoTIFF")
    c3.metric("Case study", "Uttarakhand")
    st.info("Open **Vegetation Intelligence** for the preliminary 2016–2025 QGIS case study, or use the calculators with your own data.")
    if MAP_PATH.exists():
        st.image(str(MAP_PATH), caption="Uttarakhand 2016–2025 preliminary NDVI-based vegetation-change map", use_container_width=True)
    else:
        st.warning("Case-study map is not yet available at Website_Data/maps/. Upload the expanded PNG to GitHub.")

elif page == "🛰️ Vegetation Intelligence":
    st.title("Uttarakhand | Vegetation Intelligence")
    st.caption("2016–2025 • Expanded six-scene 2016 analysis • Preliminary results")
    if not CSV_PATH.exists():
        st.error(f"Statistics CSV not found: {CSV_PATH.relative_to(ROOT)}. Check its GitHub path and filename.")
    else:
        try:
            df, s = read_change_stats(CSV_PATH)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Common observed area", f"{s['common observed area']:,.2f} km²")
            c2.metric("Vegetation loss", f"{s['vegetation loss']:,.2f} km²")
            c3.metric("Vegetation gain", f"{s['vegetation gain']:,.2f} km²")
            c4.metric("Net classified change", f"{s['net vegetation change']:+,.2f} km²")
            st.warning("Preliminary NDVI-threshold vegetation transitions (NDVI > 0.30), not verified forest loss or statewide deforestation. Scene-boundary and cross-year consistency checks remain pending.")
            if MAP_PATH.exists():
                st.image(str(MAP_PATH), caption="QGIS-exported map • Only common valid observations are classified", use_container_width=True)
                st.download_button("Download study map PNG", MAP_PATH.read_bytes(), MAP_PATH.name, mime="image/png")
            else:
                st.info("Map PNG missing. Upload it to Website_Data/maps/.")
            names = ["Stable vegetation", "Vegetation loss", "Vegetation gain", "Stable non-vegetation"]
            chart = pd.DataFrame({"Category": names, "Area (km²)": [s[n.lower()] for n in names]})
            left, right = st.columns(2)
            colors = {"Stable vegetation": "#1B5E20", "Vegetation loss": "#E53935", "Vegetation gain": "#28A64A", "Stable non-vegetation": "#A67C52"}
            with left:
                fig = px.bar(chart, x="Category", y="Area (km²)", color="Category", color_discrete_map=colors, template="plotly_dark", title="Observed change classes")
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            with right:
                fig = px.pie(chart, names="Category", values="Area (km²)", color="Category", color_discrete_map=colors, template="plotly_dark", title="Share of common observed area")
                st.plotly_chart(fig, use_container_width=True)
            st.dataframe(chart, hide_index=True, use_container_width=True)
            st.download_button("Download original QGIS statistics CSV", CSV_PATH.read_bytes(), CSV_PATH.name, mime="text/csv")
        except Exception as exc:
            st.error(f"Could not read study statistics: {exc}")

elif page == "🌿 Spectral Index Calculator":
    st.title("Spectral Index Calculator")
    index = st.selectbox("Choose spectral index", list(REQUIRED))
    st.caption("NDWI here is the McFeeters water index. Supply correctly scaled reflectance and cloud-masked data for research use.")
    mode = st.radio("Input method", ["Manual reflectance", "Multiband GeoTIFF", "Individual band GeoTIFFs"], horizontal=True)
    if mode == "Manual reflectance":
        cols = st.columns(min(3, len(REQUIRED[index])))
        bands = {name: cols[i % len(cols)].number_input(f"{name} reflectance", min_value=0.0, max_value=1.0, value=0.6 if name == "NIR" else 0.2, step=0.01, format="%.4f", key="manual_"+name) for i, name in enumerate(REQUIRED[index])}
        value = float(calculate(index, bands))
        st.metric(index, f"{value:.5f}" if np.isfinite(value) else "Undefined")
        st.caption("Manual mode evaluates reflectance values; it does not analyse an image.")
    else:
        try:
            bands, profile = None, None
            if mode == "Multiband GeoTIFF":
                f = st.file_uploader("Upload multiband GeoTIFF", type=["tif", "tiff"])
                if f is not None:
                    data, profile, descriptions = load_raster(f)
                    st.caption(f"{data.shape[0]} bands detected. Confirm the wavelength-to-band mapping.")
                    mapping = {name: st.selectbox(f"{name} band", list(range(1, data.shape[0]+1)), index=min(i, data.shape[0]-1), key="map_"+name) for i, name in enumerate(REQUIRED[index])}
                    if len(set(mapping.values())) != len(mapping):
                        st.warning("Multiple wavelengths use the same band. Verify mapping.")
                    bands = {name: as_float(data[number-1]) for name, number in mapping.items()}
            else:
                collected = {}
                for name in REQUIRED[index]:
                    f = st.file_uploader(f"{name} GeoTIFF", type=["tif", "tiff"], key="single_"+name)
                    if f is None:
                        continue
                    data, p, _ = load_raster(f)
                    if data.shape[0] != 1:
                        raise ValueError(f"{name} must contain exactly one band.")
                    if profile is not None and not grid_matches(profile, p):
                        raise ValueError("Input bands must share CRS, extent, resolution and grid.")
                    profile = p
                    collected[name] = as_float(data[0])
                if len(collected) == len(REQUIRED[index]):
                    bands = collected
            if bands is not None:
                scale = st.number_input("Reflectance multiplier", min_value=0.000001, max_value=10.0, value=1.0, format="%.6f")
                offset = st.number_input("Reflectance additive offset", value=0.0, format="%.6f")
                st.warning("Cloud/shadow masking and sensor-specific scaling are not automatic. For Landsat Collection 2 Level-2 surface reflectance, use multiplier 0.0000275 and offset -0.2 when processing raw SR bands.")
                if st.button("Calculate raster index", type="primary"):
                    result = calculate(index, {k: v*scale+offset for k, v in bands.items()})
                    show_result(result, profile, index)
        except Exception as exc:
            st.error(f"Cannot analyse raster: {exc}")

elif page == "🗺️ Land-Use Calculator":
    st.title("Land-Use Analysis")
    mode = st.radio("Input method", ["Manual area table", "Upload area CSV", "Upload classified maps"], horizontal=True)
    if mode != "Upload classified maps":
        default = pd.DataFrame({"Class": ["Forest", "Agriculture", "Built-up", "Water", "Barren"], "Baseline": [0.0]*5, "Comparison": [0.0]*5})
        if mode == "Upload area CSV":
            f = st.file_uploader("CSV with Class, Baseline, Comparison (km²)", type=["csv"])
            if f is not None:
                try:
                    default = pd.read_csv(f)
                except Exception as exc:
                    st.error(f"Invalid CSV: {exc}")
        if not {"Class", "Baseline", "Comparison"}.issubset(default.columns):
            st.error("CSV must contain Class, Baseline, Comparison columns.")
        else:
            edited = st.data_editor(default[["Class", "Baseline", "Comparison"]], num_rows="dynamic", use_container_width=True)
            try:
                out = landuse_table(edited)
                st.dataframe(out.round(3), hide_index=True, use_container_width=True)
                st.plotly_chart(px.bar(out, x="Class", y=["Baseline", "Comparison"], barmode="group", template="plotly_dark"), use_container_width=True)
                st.download_button("Download area analysis CSV", out.to_csv(index=False), "landuse_analysis.csv", mime="text/csv")
            except Exception as exc:
                st.error(str(exc))
    else:
        st.info("Upload two aligned, already-classified categorical rasters. This does not classify raw imagery.")
        codes_text = st.text_input("Class codes", "1:Forest,2:Agriculture,3:Built-up,4:Water,5:Barren")
        try:
            pair = classified_pair("land_")
            if pair is not None:
                a, b, valid, area, _ = pair
                codes = {}
                for entry in codes_text.split(","):
                    code, name = entry.split(":", 1)
                    codes[int(code.strip())] = name.strip()
                if not codes or len(set(codes.values())) != len(codes):
                    raise ValueError("Class codes and names must be unique.")
                rows = [{"Class": name, "Baseline": np.count_nonzero((a == code) & valid)*area, "Comparison": np.count_nonzero((b == code) & valid)*area} for code, name in codes.items()]
                out = landuse_table(pd.DataFrame(rows))
                st.dataframe(out.round(3), hide_index=True, use_container_width=True)
                st.caption("Areas use only pixels valid in both rasters. Prefer an appropriate equal-area CRS.")
                st.download_button("Download classified area CSV", out.to_csv(index=False), "landuse_raster_areas.csv", mime="text/csv")
        except Exception as exc:
            st.error(str(exc))

elif page == "🌲 Forest Change Calculator":
    st.title("Forest Change Calculator")
    mode = st.radio("Input method", ["Manual forest areas", "Upload forest-area CSV", "Upload classified maps"], horizontal=True)
    if mode != "Upload classified maps":
        a, b = 100.0, 90.0
        if mode == "Upload forest-area CSV":
            f = st.file_uploader("CSV columns: baseline_km2, comparison_km2", type=["csv"])
            if f is not None:
                try:
                    df = pd.read_csv(f)
                    a, b = float(df.iloc[0]["baseline_km2"]), float(df.iloc[0]["comparison_km2"])
                except Exception as exc:
                    st.error(f"Invalid CSV: {exc}")
        a = st.number_input("Baseline forest area (km²)", min_value=0.0, value=max(a, 0.0))
        b = st.number_input("Comparison forest area (km²)", min_value=0.0, value=max(b, 0.0))
        net = b-a
        c1, c2, c3 = st.columns(3)
        c1.metric("Net forest change", f"{net:+,.3f} km²")
        c2.metric("Net change (%)", f"{100*net/a:+.2f}%" if a else "Undefined")
        c3.metric("Net area decrease", f"{max(a-b, 0):,.3f} km²")
        st.warning("Net area decrease is not gross deforestation; forest gains elsewhere may offset forest loss.")
        stats = pd.DataFrame([{"Baseline forest (km²)": a, "Comparison forest (km²)": b, "Net change (km²)": net, "Net area decrease (km²)": max(a-b, 0)}])
        st.download_button("Download forest change CSV", stats.to_csv(index=False), "forest_area_change.csv", mime="text/csv")
    else:
        st.info("Upload two aligned categorical land-cover maps to estimate forest → non-forest transitions.")
        code = st.number_input("Forest class code", value=1, step=1)
        try:
            pair = classified_pair("forest_")
            if pair is not None:
                a, b, valid, area, profile = pair
                old, new = (a == code) & valid, (b == code) & valid
                loss, gain = old & ~new, ~old & new
                stats = pd.DataFrame([{"Baseline forest (km²)": old.sum()*area, "Comparison forest (km²)": new.sum()*area, "Gross forest loss (km²)": loss.sum()*area, "Gross forest gain (km²)": gain.sum()*area, "Net forest change (km²)": (new.sum()-old.sum())*area}])
                st.dataframe(stats.round(4), hide_index=True, use_container_width=True)
                st.download_button("Download forest-loss GeoTIFF", geotiff_bytes(np.where(valid, loss.astype(float), np.nan), profile), "forest_loss_mask.tif", mime="image/tiff")
                st.download_button("Download forest statistics CSV", stats.to_csv(index=False), "forest_transitions.csv", mime="text/csv")
                st.warning("Forest-to-nonforest transitions indicate potential loss, not necessarily permanent deforestation.")
        except Exception as exc:
            st.error(str(exc))

elif page == "🔄 Change Detection":
    st.title("Two-Date Spectral Change Detection")
    st.write("Upload precomputed single-band spectral-index GeoTIFFs. Change = later − earlier.")
    f1 = st.file_uploader("Earlier index GeoTIFF", type=["tif", "tiff"], key="change_earlier")
    f2 = st.file_uploader("Later index GeoTIFF", type=["tif", "tiff"], key="change_later")
    if f1 is not None and f2 is not None:
        try:
            a, pa, _ = load_raster(f1)
            b, pb, _ = load_raster(f2)
            if a.shape[0] != 1 or b.shape[0] != 1 or not grid_matches(pa, pb):
                raise ValueError("Both files must be single-band rasters on exactly the same grid and CRS.")
            show_result(as_float(b[0])-as_float(a[0]), pa, "Index change")
            st.warning("Negative NDVI change alone does not establish deforestation. Check seasonality, clouds and classification accuracy.")
        except Exception as exc:
            st.error(str(exc))

else:
    st.title("Methodology & Limitations")
    st.markdown("""**Case study:** The Uttarakhand map compares NDVI > 0.30 vegetation classification for common valid pixels in 2016 and 2025. The displayed areas are imported from the QGIS-produced CSV, not calculated from the PNG. Boundary containment and grid alignment were checked; scene-boundary and cross-year processing consistency reviews remain pending.

**Spectral indices:** Calculated from supplied reflectance values or GeoTIFF bands. NDWI is the McFeeters water index. Sensor-specific calibration and cloud masking are the user's responsibility.

**Land use:** Manual tables or preclassified categorical rasters; the website does not automatically classify raw satellite images.

**Forest change:** Manual area differences show net change; paired categorical rasters estimate gross transitions, which are not definitive evidence of deforestation.

**Area:** Pixel areas use projected grids in metres. A suitable equal-area projection is preferable for authoritative area estimates.

**Limits:** Uploaded rasters are restricted to 45 million samples to protect hosted memory. Large Landsat scenes should be clipped or processed externally before upload.

**QGIS:** Exported GeoTIFFs are QGIS-compatible, but the web app itself does not run QGIS or a trained AI model.""")

st.divider()
st.caption("TerraScope AI • Transparent geospatial calculations • Research preview, not an operational deforestation alert system")
