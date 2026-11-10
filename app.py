            if f is None: st.stop()
            try: df=pd.read_csv(f)
            except Exception as exc: st.error(str(exc)); st.stop()
        else:
            df=pd.DataFrame({"Class":["Forest","Agriculture","Built-up","Water","Barren"],"Baseline":[0.0]*5,"Comparison":[0.0]*5})
        if not {"Class","Baseline","Comparison"}.issubset(df.columns): st.error("CSV must contain Class, Baseline, Comparison."); st.stop()
        edited=st.data_editor(df[["Class","Baseline","Comparison"]],num_rows="dynamic",use_container_width=True)
        try:
            out=landuse_table(edited,"Baseline","Comparison")
            st.dataframe(out.round(3),hide_index=True,use_container_width=True)
            st.plotly_chart(px.bar(out,x="Class",y=["Baseline","Comparison"],barmode="group",labels={"value":"Area (km²)"}),use_container_width=True)
            st.metric("Total baseline area",f"{out['Baseline'].sum():,.3f} km²")
            st.metric("Total comparison area",f"{out['Comparison'].sum():,.3f} km²")
            st.download_button("Download analysis CSV",out.to_csv(index=False),"landuse_analysis.csv","text/csv")
        except Exception as exc: st.error(str(exc))
    else:
        st.info("Upload two aligned, single-band categorical GeoTIFF maps with matching class codes. This does not classify raw satellite imagery.")
        first=st.file_uploader("Baseline classified GeoTIFF",type=["tif","tiff"],key="class1")
        second=st.file_uploader("Comparison classified GeoTIFF",type=["tif","tiff"],key="class2")
        classes=st.text_input("Class codes and names (e.g. 1:Forest,2:Agriculture,3:Built-up)","1:Forest,2:Agriculture,3:Built-up,4:Water,5:Barren")
        if first and second and st.button("Analyse classified maps"):
            try:
                a,ma,_=load_raster(first); b,mb,_=load_raster(second)
                if a.shape[0]!=1 or b.shape[0]!=1: raise ValueError("Each classification map must have exactly one band.")
                if (ma["width"],ma["height"],ma["transform"],ma["crs"])!=(mb["width"],mb["height"],mb["transform"],mb["crs"]): raise ValueError("Classification maps must be on the same pixel grid and CRS.")
                if ma["crs"] is None or not ma["crs"].is_projected: raise ValueError("Use a suitable projected CRS with metre units for area calculations.")
                if ma["crs"].linear_units.lower() not in ("metre","meter","metres","meters","m"): raise ValueError("Projected CRS must use metres.")
                area=abs(ma["transform"].a*ma["transform"].e-ma["transform"].b*ma["transform"].d)/1e6
                codes=dict((int(p.split(":",1)[0].strip()),p.split(":",1)[1].strip()) for p in classes.split(","))
                aa=a[0].filled(np.nan); bb=b[0].filled(np.nan); valid=np.isfinite(aa)&np.isfinite(bb)
                rows=[{"Class":name,"Baseline":float(((aa==code)&valid).sum()*area),"Comparison":float(((bb==code)&valid).sum()*area)} for code,name in codes.items()]
                out=landuse_table(pd.DataFrame(rows),"Baseline","Comparison")
                st.dataframe(out.round(3),hide_index=True,use_container_width=True)
                st.caption(f"Area computed from pixel grid: {area:.8f} km²/pixel; only pixels valid in both maps counted. Suitable projected CRS assumed.")
                st.download_button("Download classification area CSV",out.to_csv(index=False),"landuse_raster_areas.csv","text/csv")
            except Exception as exc: st.error(str(exc))

elif page=="🌲 Deforestation Calculator":
    st.header("Forest-area change calculator")
    mode=st.radio("Input method",["✍️ Enter forest areas","📄 Upload forest-area CSV","🗺️ Upload classified maps"],horizontal=True)
    if mode.startswith("✍️") or "CSV" in mode:
        if "CSV" in mode:
            f=st.file_uploader("CSV columns: baseline_km2, comparison_km2 (first row)",type="csv")
            if f is None: st.stop()
            try:
                df=pd.read_csv(f)
                a=float(df.loc[0,"baseline_km2"]); b=float(df.loc[0,"comparison_km2"])
                st.caption("CSV values loaded. You can edit them before calculating.")
                a=st.number_input("Baseline forest area (km²)",min_value=0.0,value=a,key="csv_forest_a")
                b=st.number_input("Comparison forest area (km²)",min_value=0.0,value=b,key="csv_forest_b")
            except Exception as exc: st.error(f"Invalid CSV: {exc}"); st.stop()
        else:
            a=st.number_input("Baseline forest area (km²)",min_value=0.0,value=100.0,step=1.0)
            b=st.number_input("Comparison forest area (km²)",min_value=0.0,value=90.0,step=1.0)
        try:
            data=forest_math(a,b)
            c1,c2,c3=st.columns(3)
            c1.metric("Net change",f"{data['Net change (km²)']:+,.3f} km²")
            c2.metric("Net change (%)", "Undefined" if np.isnan(data["Net change (%)"]) else f"{data['Net change (%)']:+.2f}%")
            c3.metric("Net area decrease",f"{data['Net decrease (km²)']:,.3f} km²")
            st.warning("This is NET forest-area change, not gross deforestation. Forest gains can offset losses. Inputs are user-provided.")
            st.download_button("Download results CSV",pd.DataFrame([data]).to_csv(index=False),"forest_area_change.csv","text/csv")
        except Exception as exc: st.error(str(exc))
    else:
        st.info("Upload aligned single-band classified maps. Forest pixels transitioning to any other valid class are counted as gross forest loss.")
        a_file=st.file_uploader("Baseline classification",type=["tif","tiff"],key="forest_a")
        b_file=st.file_uploader("Comparison classification",type=["tif","tiff"],key="forest_b")
        forest_code=st.number_input("Forest class code",value=1,step=1)
        if a_file and b_file and st.button("Calculate forest transitions",type="primary"):
            try:
                a,ma,_=load_raster(a_file); b,mb,_=load_raster(b_file)
                if a.shape[0]!=1 or b.shape[0]!=1: raise ValueError("Use single-band categorical rasters.")
                if (ma["width"],ma["height"],ma["transform"],ma["crs"])!=(mb["width"],mb["height"],mb["transform"],mb["crs"]): raise ValueError("Raster grids and CRS must match.")
                if ma["crs"] is None or not ma["crs"].is_projected or ma["crs"].linear_units.lower() not in ("metre","meter","metres","meters","m"): raise ValueError("Use a suitable projected CRS in metres.")
                area=abs(ma["transform"].a*ma["transform"].e-ma["transform"].b*ma["transform"].d)/1e6
                aa=a[0].filled(np.nan); bb=b[0].filled(np.nan); valid=np.isfinite(aa)&np.isfinite(bb)
                forest_a=(aa==forest_code)&valid; forest_b=(bb==forest_code)&valid
                loss=forest_a&~forest_b; gain=~forest_a&forest_b
                stats={"Baseline forest (km²)":forest_a.sum()*area,"Comparison forest (km²)":forest_b.sum()*area,
                       "Gross forest loss (km²)":loss.sum()*area,"Gross forest gain (km²)":gain.sum()*area,
                       "Net forest change (km²)":(forest_b.sum()-forest_a.sum())*area}
                st.dataframe(pd.DataFrame([stats]).round(4),hide_index=True,use_container_width=True)
                st.download_button("Download forest-loss mask GeoTIFF",geotiff_bytes(np.where(valid,loss.astype(float),np.nan),ma),"forest_loss_mask.tif","image/tiff")
                st.download_button("Download statistics CSV",pd.DataFrame([stats]).to_csv(index=False),"forest_transitions.csv","text/csv")
                st.warning("Forest → non-forest transitions indicate potential forest loss, not necessarily permanent deforestation. Classification quality and temporal comparability matter.")
            except Exception as exc: st.error(str(exc))

elif page=="🔄 Change Detection":
    st.header("Two-date spectral index change")
    st.write("Upload precomputed, aligned single-band index GeoTIFFs for two dates. Difference = later − earlier.")
    f1=st.file_uploader("Earlier index raster",type=["tif","tiff"],key="change_a")
    f2=st.file_uploader("Later index raster",type=["tif","tiff"],key="change_b")
    if f1 and f2 and st.button("Calculate index change",type="primary"):
        try:
            a,ma,_=load_raster(f1); b,mb,_=load_raster(f2)
            if a.shape[0]!=1 or b.shape[0]!=1: raise ValueError("Upload single-band index rasters.")
            if (ma["width"],ma["height"],ma["transform"],ma["crs"])!=(mb["width"],mb["height"],mb["transform"],mb["crs"]): raise ValueError("Rasters must share a pixel grid and CRS.")
            result_display(b[0].filled(np.nan)-a[0].filled(np.nan),ma,"index_change.tif")
            st.warning("Negative NDVI change alone does not prove deforestation; account for seasonality, clouds, and land-cover transitions.")
        except Exception as exc: st.error(str(exc))

else:
    st.header("Methodology and limitations")
    st.markdown("""**Spectral indices:** Calculated per pixel from user-assigned spectral bands. NDWI here means McFeeters water index (Green−NIR)/(Green+NIR). EVI and SAVI need correctly scaled reflectance. Invalid/masked pixels are excluded. Cloud masking is **not** automated.\n\n**Land-use analysis:** Accepts user-supplied class areas or existing categorical land-cover maps. It does **not** classify raw imagery, train Random Forest, or produce accuracy metrics.\n\n**Deforestation:** Manual forest areas yield net change only. Two categorical maps allow gross Forest→Non-forest and Non-forest→Forest transitions. These transitions are not proof of permanent deforestation.\n\n**Area calculation:** Uses projected raster pixel area and requires metre units. Use an appropriate equal-area projection for defensible regional area estimates.\n\n**QGIS:** Exported GeoTIFFs can be opened in QGIS later. No Google Earth Engine dependencies are used.\n\n**Next improvements:** Sensor-aware scale/offset handling, cloud/shadow masking, band recognition, raster alignment, training-data-backed land-cover classification, and validation against reference imagery.""")

st.divider()
st.caption("TerraScope AI · Raster calculations are data-derived; manual calculations are user-supplied · Research use requires independent validation")
