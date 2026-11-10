import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import rasterio
from rasterio.io import MemoryFile

st.set_page_config(page_title='TerraScope AI', page_icon='🌍', layout='wide')
st.markdown('''<style>.block-container{max-width:1250px;padding-top:1.6rem}h1,h2,h3{letter-spacing:-.03em}</style>''', unsafe_allow_html=True)

BANDS = ['Blue', 'Green', 'Red', 'NIR', 'SWIR1', 'SWIR2']
REQUIRED = {
    'NDVI': ['NIR', 'Red'], 'NDWI': ['Green', 'NIR'],
    'NDMI': ['NIR', 'SWIR1'], 'NBR': ['NIR', 'SWIR2'],
    'NDBI': ['SWIR1', 'NIR'], 'EVI': ['NIR', 'Red', 'Blue'],
    'SAVI': ['NIR', 'Red'], 'GNDVI': ['NIR', 'Green'],
    'BSI': ['SWIR1', 'Red', 'NIR', 'Blue']
}

def divide(a, b):
    a, b = np.broadcast_arrays(np.asarray(a, dtype=float), np.asarray(b, dtype=float))
    result = np.full(a.shape, np.nan, dtype=float)
    np.divide(a, b, out=result, where=np.isfinite(a) & np.isfinite(b) & (np.abs(b) > 1e-12))
    return result

def calculate(index, b):
    if index == 'NDVI': return divide(b['NIR']-b['Red'], b['NIR']+b['Red'])
    if index == 'NDWI': return divide(b['Green']-b['NIR'], b['Green']+b['NIR'])
    if index == 'NDMI': return divide(b['NIR']-b['SWIR1'], b['NIR']+b['SWIR1'])
    if index == 'NBR': return divide(b['NIR']-b['SWIR2'], b['NIR']+b['SWIR2'])
    if index == 'NDBI': return divide(b['SWIR1']-b['NIR'], b['SWIR1']+b['NIR'])
    if index == 'EVI': return divide(2.5*(b['NIR']-b['Red']), b['NIR']+6*b['Red']-7.5*b['Blue']+1)
    if index == 'SAVI': return divide(1.5*(b['NIR']-b['Red']), b['NIR']+b['Red']+0.5)
    if index == 'GNDVI': return divide(b['NIR']-b['Green'], b['NIR']+b['Green'])
    if index == 'BSI': return divide((b['SWIR1']+b['Red'])-(b['NIR']+b['Blue']), (b['SWIR1']+b['Red'])+(b['NIR']+b['Blue']))
    raise ValueError('Unknown index')

def load_raster(upload):
    with MemoryFile(upload.getvalue()) as mem:
        with mem.open() as src:
            if src.width*src.height*src.count > 45_000_000:
                raise ValueError('Raster too large for this hosted version (45 million samples maximum).')
            return src.read(masked=True), src.profile.copy(), src.descriptions

def grid_matches(a, b):
    return all(a[k] == b[k] for k in ('width', 'height', 'transform', 'crs'))

def pixel_area_km2(profile):
    crs = profile['crs']
    if crs is None or not crs.is_projected:
        raise ValueError('Area analysis requires a projected CRS with metre units; reproject to an appropriate equal-area CRS first.')
    unit = (crs.linear_units or '').lower()
    if unit not in ('metre', 'meter', 'metres', 'meters', 'm'):
        raise ValueError('Area analysis requires projected coordinates in metres.')
    t = profile['transform']
    return abs(t.a*t.e-t.b*t.d)/1_000_000

def as_float(masked):
    return np.asarray(masked.filled(np.nan), dtype=float)

def geotiff_bytes(array, profile):
    arr = np.asarray(array, dtype='float32')
    meta = profile.copy()
    meta.update(driver='GTiff', count=1, height=arr.shape[0], width=arr.shape[1], dtype='float32', nodata=-9999.0)
    with MemoryFile() as mem:
        with mem.open(**meta) as ds:
            ds.write(np.where(np.isfinite(arr), arr, -9999.0).astype('float32'), 1)
        return mem.read()

def show_result(array, profile, name):
    valid = np.asarray(array)[np.isfinite(array)]
    if valid.size == 0:
        st.warning('No valid output pixels. Check band assignments, scaling, and no-data masks.')
        return
    cols = st.columns(4)
    for col, label, value in zip(cols, ('Mean', 'Median', 'Minimum', 'Maximum'), (valid.mean(), np.median(valid), valid.min(), valid.max())):
        col.metric(label, f'{value:.4f}')
    st.caption(f'{valid.size:,} valid pixels. Previews are not georeferenced maps; download the GeoTIFF for GIS viewing.')
    preview = np.asarray(array)
    stride = max(1, int(np.ceil(max(preview.shape)/700)))
    st.image(np.ma.masked_invalid(preview[::stride, ::stride]), caption=f'{name} raster preview', clamp=True)
    st.plotly_chart(px.histogram(x=valid[::max(1, len(valid)//150000)], nbins=60, labels={'x':name}, title=f'{name} distribution'), use_container_width=True)
    st.download_button('Download result GeoTIFF', geotiff_bytes(array, profile), f'{name.lower().replace(" ", "_")}.tif', mime='image/tiff')
    stats = pd.DataFrame([{'metric':'mean','value':valid.mean()}, {'metric':'median','value':np.median(valid)}, {'metric':'min','value':valid.min()}, {'metric':'max','value':valid.max()}, {'metric':'valid_pixels','value':valid.size}])
    st.download_button('Download statistics CSV', stats.to_csv(index=False), f'{name.lower().replace(" ", "_")}_stats.csv', mime='text/csv')

def forest_math(a, b):
    if not np.isfinite(a) or not np.isfinite(b) or min(a,b) < 0:
        raise ValueError('Forest areas must be nonnegative finite values.')
    return {'Baseline forest (km²)':a, 'Comparison forest (km²)':b,
            'Net change (km²)':b-a, 'Net change (%)':100*(b-a)/a if a else np.nan,
            'Net area decrease (km²)':max(a-b, 0)}

def landuse_table(df):
    data = df.copy()
    for col in ('Baseline', 'Comparison'):
        data[col] = pd.to_numeric(data[col], errors='coerce')
    if data[['Baseline','Comparison']].isna().any().any() or (data[['Baseline','Comparison']] < 0).any().any():
        raise ValueError('All areas must be nonnegative numbers.')
    if data['Class'].astype(str).str.strip().eq('').any() or data['Class'].duplicated().any():
        raise ValueError('Each land-use class needs a unique, nonempty name.')
    data['Change (km²)'] = data['Comparison']-data['Baseline']
    data['Change (%)'] = np.where(data['Baseline']>0, 100*data['Change (km²)']/data['Baseline'], np.nan)
    return data

def classified_pair(prefix):
    a_file = st.file_uploader('Baseline classified GeoTIFF', type=['tif','tiff'], key=prefix+'a')
    b_file = st.file_uploader('Comparison classified GeoTIFF', type=['tif','tiff'], key=prefix+'b')
    if a_file is None or b_file is None: return None
    a, pa, _ = load_raster(a_file)
    b, pb, _ = load_raster(b_file)
    if a.shape[0] != 1 or b.shape[0] != 1 or not grid_matches(pa, pb):
        raise ValueError('Both rasters must be single-band categorical maps on exactly the same grid and CRS.')
    area = pixel_area_km2(pa)
    aa, bb = as_float(a[0]), as_float(b[0])
    valid = np.isfinite(aa) & np.isfinite(bb)
    if not valid.any(): raise ValueError('No overlapping valid pixels.')
    return aa, bb, valid, area, pa

st.sidebar.title('🌍 TerraScope AI')
st.sidebar.caption('Environmental analytics · QGIS-ready')
page = st.sidebar.radio('Navigation', ['🏠 Dashboard', '🌿 Spectral Index Calculator', '🗺️ Land-Use Calculator', '🌲 Deforestation Calculator', '🔄 Change Detection', '📘 Methodology'])
st.sidebar.divider()
st.sidebar.info('No Google Earth Engine or QGIS installation required. File processing uses Rasterio and NumPy.')

if page == '🏠 Dashboard':
    st.title('TerraScope AI 2.0')
    st.write('Analyse satellite rasters and land-cover change with transparent, reproducible calculations.')
    c1,c2,c3 = st.columns(3)
    c1.metric('Spectral indices', '9')
    c2.metric('Input options', 'Manual + Upload')
    c3.metric('GEE dependency', 'None')
    st.subheader('Start an analysis')
    st.markdown('**Spectral indices:** Enter reflectance values or upload GeoTIFF bands.\n\n**Land use:** Edit area tables or analyse already-classified maps.\n\n**Deforestation:** Calculate net forest-area changes or gross raster transitions.\n\n**Change detection:** Compare two aligned index rasters.')
    st.warning('No satellite scene is loaded by default. No land-cover classification or AI model is claimed to have run.')

elif page == '🌿 Spectral Index Calculator':
    st.title('Spectral Index Calculator')
    index = st.selectbox('Choose index', list(REQUIRED))
    st.caption('NDWI means McFeeters surface-water index. For Sentinel-2, use B02=Blue, B03=Green, B04=Red, B08=NIR, B11=SWIR1, B12=SWIR2.')
    mode = st.radio('Input method', ['✍️ Manual reflectance', '🗂️ Multiband GeoTIFF', '📂 Individual band GeoTIFFs'], horizontal=True)
    if mode.startswith('✍️'):
        cols = st.columns(min(3, len(REQUIRED[index])))
        b = {name: cols[i%len(cols)].number_input(f'{name} reflectance', min_value=0.0, max_value=1.0, value=0.2 if name != 'NIR' else 0.6, step=0.01, format='%.4f', key='manual_'+name) for i,name in enumerate(REQUIRED[index])}
        value = float(calculate(index, b))
        st.metric(index, 'Undefined (zero denominator)' if not np.isfinite(value) else f'{value:.5f}')
        st.caption('Manual mode uses reflectance values, not raw digital numbers. No imagery is analysed.')
    else:
        try:
            if mode.startswith('🗂️'):
                f = st.file_uploader('Upload multiband GeoTIFF', type=['tif','tiff'], key='multi')
                if f is not None:
                    data, profile, descriptions = load_raster(f)
                    st.caption(f'{data.shape[0]} bands detected. Select the correct band number for each wavelength.')
                    mapping = {name: st.selectbox(f'{name} band', list(range(1, data.shape[0]+1)), index=min(i,data.shape[0]-1), key='map_'+name) for i,name in enumerate(REQUIRED[index])}
                    if len(set(mapping.values())) != len(mapping): st.warning('Different wavelengths should map to different bands.')
                    bands = {name: as_float(data[band-1]) for name,band in mapping.items()}
                else: bands = None; profile = None
            else:
                bands = {}; profile = None
                for name in REQUIRED[index]:
                    f = st.file_uploader(f'{name} GeoTIFF', type=['tif','tiff'], key='single_'+name)
                    if f is None: bands = None; break
                    data, p, _ = load_raster(f)
                    if data.shape[0] != 1: raise ValueError(f'{name} file must contain one band.')
                    if profile is not None and not grid_matches(profile, p): raise ValueError('Input bands must have identical grids and CRS.')
                    profile = p
                    bands[name] = as_float(data[0])
            if bands is not None:
                scale = st.number_input('Reflectance multiplier', min_value=0.000001, max_value=10.0, value=1.0, format='%.6f', help='For many unoffset reflectance rasters stored as integers, use 0.0001. Sentinel-2 products with processing offsets need sensor-specific preprocessing.')
                offset = st.number_input('Reflectance additive offset', value=0.0, format='%.6f')
                st.warning('Cloud/shadow masking is not automatic. Apply sensor-specific offsets and cloud masks before research use. All bands must be coregistered.')
                if st.button('Calculate raster index', type='primary'):
                    result = calculate(index, {k: v*scale+offset for k,v in bands.items()})
                    show_result(result, profile, index)
        except Exception as exc:
            st.error(f'Cannot analyse raster: {exc}')

elif page == '🗺️ Land-Use Calculator':
    st.title('Land-Use Analysis')
    mode = st.radio('Input method', ['✍️ Manual area table', '📄 Upload area CSV', '🗺️ Upload classified maps'], horizontal=True)
    if mode != '🗺️ Upload classified maps':
        default = pd.DataFrame({'Class':['Forest','Agriculture','Built-up','Water','Barren'], 'Baseline':[0.0]*5, 'Comparison':[0.0]*5})
        if mode.startswith('📄'):
            f = st.file_uploader('CSV columns: Class, Baseline, Comparison (areas in km²)', type=['csv'])
            if f is not None:
                try: default = pd.read_csv(f)
                except Exception as exc: st.error(str(exc))
        if not {'Class','Baseline','Comparison'}.issubset(default.columns):
            st.error('CSV must contain Class, Baseline, Comparison.')
        else:
            edited = st.data_editor(default[['Class','Baseline','Comparison']], num_rows='dynamic', use_container_width=True)
            try:
                out = landuse_table(edited)
                st.dataframe(out.round(3), hide_index=True, use_container_width=True)
                st.plotly_chart(px.bar(out, x='Class', y=['Baseline','Comparison'], barmode='group', labels={'value':'Area (km²)'}), use_container_width=True)
                st.download_button('Download area analysis CSV', out.to_csv(index=False), 'landuse_analysis.csv', mime='text/csv')
            except Exception as exc: st.error(str(exc))
    else:
        st.info('Upload two already-classified categorical maps. This does not classify raw satellite imagery.')
        classes = st.text_input('Class codes and names', '1:Forest,2:Agriculture,3:Built-up,4:Water,5:Barren')
        try:
            pair = classified_pair('land_')
            if pair is not None:
                a,b,valid,area,_ = pair
                codes = {}
                for entry in classes.split(','):
                    code,name = entry.split(':',1)
                    codes[int(code.strip())] = name.strip()
                if len(set(codes.values())) != len(codes): raise ValueError('Class names must be unique.')
                rows = [{'Class':name, 'Baseline':float(np.count_nonzero((a==code)&valid)*area), 'Comparison':float(np.count_nonzero((b==code)&valid)*area)} for code,name in codes.items()]
                out = landuse_table(pd.DataFrame(rows))
                st.dataframe(out.round(3), use_container_width=True, hide_index=True)
                st.caption(f'Pixel area: {area:.8f} km²; only pixels valid at both dates are counted. Use a suitable equal-area CRS.')
                st.download_button('Download classified area CSV', out.to_csv(index=False), 'landuse_raster_areas.csv', mime='text/csv')
        except Exception as exc: st.error(str(exc))

elif page == '🌲 Deforestation Calculator':
    st.title('Forest Change & Deforestation Calculator')
    mode = st.radio('Input method', ['✍️ Manual forest areas', '📄 Upload forest-area CSV', '🗺️ Upload classified maps'], horizontal=True)
    if mode != '🗺️ Upload classified maps':
        a,b = 100.0,90.0
        if mode.startswith('📄'):
            f = st.file_uploader('CSV columns: baseline_km2, comparison_km2', type=['csv'])
            if f is not None:
                try:
                    df = pd.read_csv(f)
                    a,b = float(df.iloc[0]['baseline_km2']), float(df.iloc[0]['comparison_km2'])
                except Exception as exc: st.error(f'Invalid CSV: {exc}')
        a = st.number_input('Baseline forest area (km²)', min_value=0.0, value=max(a,0.0))
        b = st.number_input('Comparison forest area (km²)', min_value=0.0, value=max(b,0.0))
        data = forest_math(a,b)
        c1,c2,c3 = st.columns(3)
        c1.metric('Net forest change', f"{data['Net change (km²)']:+,.3f} km²")
        c2.metric('Net change (%)', 'Undefined' if np.isnan(data['Net change (%)']) else f"{data['Net change (%)']:+.2f}%")
        c3.metric('Net area decrease', f"{data['Net area decrease (km²)']:,.3f} km²")
        st.warning('Net area decrease is not gross deforestation. Forest gain elsewhere may offset forest loss.')
        st.download_button('Download forest-area CSV', pd.DataFrame([data]).to_csv(index=False), 'forest_area_change.csv', mime='text/csv')
    else:
        st.info('Upload two aligned categorical land-cover maps to identify forest → non-forest transitions.')
        code = st.number_input('Forest class code', value=1, step=1)
        try:
            pair = classified_pair('forest_')
            if pair is not None:
                a,b,valid,area,profile = pair
                forest_a,forest_b = (a==code)&valid,(b==code)&valid
                loss,gain = forest_a&~forest_b,~forest_a&forest_b
                stats = {'Baseline forest (km²)':forest_a.sum()*area, 'Comparison forest (km²)':forest_b.sum()*area,
                         'Gross forest loss (km²)':loss.sum()*area, 'Gross forest gain (km²)':gain.sum()*area,
                         'Net forest change (km²)':(forest_b.sum()-forest_a.sum())*area}
                st.dataframe(pd.DataFrame([stats]).round(4), hide_index=True, use_container_width=True)
                st.download_button('Download forest-loss mask GeoTIFF', geotiff_bytes(np.where(valid,loss.astype(float),np.nan),profile), 'forest_loss_mask.tif', mime='image/tiff')
                st.download_button('Download forest statistics CSV', pd.DataFrame([stats]).to_csv(index=False), 'forest_transitions.csv', mime='text/csv')
                st.warning('Forest-to-non-forest transitions suggest potential forest loss, not necessarily permanent deforestation.')
        except Exception as exc: st.error(str(exc))

elif page == '🔄 Change Detection':
    st.title('Two-Date Spectral Index Change')
    st.write('Upload precomputed single-band index GeoTIFFs. Change = later minus earlier.')
    f1 = st.file_uploader('Earlier index GeoTIFF', type=['tif','tiff'], key='change_earlier')
    f2 = st.file_uploader('Later index GeoTIFF', type=['tif','tiff'], key='change_later')
    if f1 is not None and f2 is not None:
        try:
            a,pa,_ = load_raster(f1)
            b,pb,_ = load_raster(f2)
            if a.shape[0]!=1 or b.shape[0]!=1 or not grid_matches(pa,pb):
                raise ValueError('Both files must be single-band rasters on the same grid and CRS.')
            show_result(as_float(b[0])-as_float(a[0]), pa, 'Index change')
            st.warning('Negative NDVI change alone is not proof of deforestation. Consider seasonality and cloud contamination.')
        except Exception as exc: st.error(str(exc))

else:
    st.title('Methodology & Limitations')
    st.markdown('''**Spectral indices:** Calculated from user-provided reflectance values or raster bands. NDWI is the McFeeters water index. EVI and SAVI require correctly scaled reflectance. No automatic cloud/shadow masking or sensor-specific offset handling is provided.\n\n**Land use:** Uses user-provided areas or existing categorical classification rasters. Raw imagery is not automatically classified.\n\n**Forest change:** Manual areas yield net change only; paired categorical maps yield gross forest transitions. Forest transitions are not proof of permanent deforestation.\n\n**Area estimates:** Pixel areas are derived from projected raster grids in metres; an appropriate equal-area CRS is recommended.\n\n**QGIS:** Exported GeoTIFFs can be opened in QGIS. QGIS is not required to run this application.\n\n**Research validation:** Independently validate imagery preprocessing, classification accuracy, and change detection before publishing conclusions.''')

st.divider()
st.caption('TerraScope AI · Calculations are derived from user inputs · No fabricated satellite or AI results')
