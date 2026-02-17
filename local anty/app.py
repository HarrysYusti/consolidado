import streamlit as st
import pandas as pd
import backend
from io import BytesIO
import os
from datetime import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Gestión Logística SFTP",
    layout="wide",
    page_icon="📦"
)

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 60px;
        font-size: 20px;
        font-weight: bold;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- ESTADO DE SESIÓN ---
if "data_master" not in st.session_state:
    st.session_state.data_master = None

# --- BARRA LATERAL (CONFIG COMÚN) ---
with st.sidebar:
    st.title("🔧 Configuración SFTP")
    user = st.text_input("Usuario", value=backend.SFTP_USER, disabled=True)
    password = st.text_input("Contraseña", type="password")
    
    st.info("ℹ️ La contraseña es necesaria para conectar en cualquiera de las pestañas.")

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(["📊 Proceso General", "📥 Búsqueda por Archivo", "📂 Cargar Histórico"])

# ==========================================
# TAB 1: PROCESO GENERAL (Lógica original)
# ==========================================
with tab1:
    st.header("Consolidación por Fecha")
    
    col_conf1, col_conf2 = st.columns(2)
    with col_conf1:
        # Selector de Filtros
        st.subheader("Criterio de Búsqueda")
        filter_mode = st.radio(
            "Modo de Selección:",
            ["Automático (Últimos 3 días)", "Manual (Fecha Específica)"]
        )
    
    target_date = None
    days_back = None
    start_time_filter = None
    end_time_filter = None
    
    with col_conf2:
        if "Manual" in filter_mode:
            target_date = st.date_input("Selecciona Fecha")
            st.caption("Filtro Horario (HHMM) - Opcional")
            
            c_h1, c_h2 = st.columns(2)
            # Dejamos vacíos por defecto para indicar opcionalidad
            start_str = c_h1.text_input("Hora Inicio", value="", placeholder="Ej: 0800")
            end_str = c_h2.text_input("Hora Fin", value="", placeholder="Ej: 1800")
            
            # Parsing HHMM
            def parse_time_input(time_str):
                if not time_str or not time_str.strip():
                    return None
                try:
                    t = time_str.strip()
                    if len(t) == 3: t = "0" + t
                    if len(t) == 4 and t.isdigit():
                        h, m = int(t[:2]), int(t[2:])
                        if 0 <= h <= 23 and 0 <= m <= 59: return time(h, m)
                except: pass
                return "INVALID" # Marcador de error

            start_time_filter = parse_time_input(start_str)
            end_time_filter = parse_time_input(end_str)
            
            # Validaciones visuales solo si escribió algo mal
            if start_time_filter == "INVALID":
                st.warning("⚠️ Hora Inicio inválida (Use HHMM). Se ignorará filtro.")
                start_time_filter = None
            
            if end_time_filter == "INVALID":
                st.warning("⚠️ Hora Fin inválida (Use HHMM). Se ignorará filtro.")
                end_time_filter = None
        else:
            days_back = 3
            st.info("Se analizarán archivos de los últimos 3 días.")

    st.markdown("---")
    run_btn = st.button("EJECUTAR PROCESO GENERAL")

    if run_btn:
        if not password:
            st.error("⚠️ Falta contraseña.")
        else:
            status = st.status("Procesando...", expanded=True)
            prog = status.progress(0)
            try:
                status.write("🔑 Conectando...")
                sftp, transport = backend.create_sftp_client(password)
                
                # ... (Lógica de filtrado y parsing original) ...
                all_records = []
                process_groups = [
                    ("Cartoning", backend.PATH_CARTONING, "cartoning"),
                    ("Wave", backend.PATH_WAVE, "wave"),
                    ("ShipConfirm", backend.PATH_SHIP, "ship")
                ]
                
                files_to_read = []
                # Fase 1
                status.write("📂 Filtrando archivos...")
                for name, path, ftype in process_groups:
                    found = backend.filter_files_by_date(
                        sftp, path, ftype, target_date, days_back, 
                        start_time_filter, end_time_filter
                    )
                    status.write(f"   - {name}: {len(found)}")
                    files_to_read.extend(found)
                
                # Fase 2
                total = len(files_to_read)
                status.write(f"📥 Leyendo {total} archivos...")
                if total > 0:
                    for i, f_meta in enumerate(files_to_read):
                        status.write(f"   Leyendo: **{f_meta['filename']}**...")
                        prog.progress((i+1)/total)
                        try:
                            with sftp.open(f_meta['path'], 'r') as rf:
                                content = rf.read()
                                recs = backend.parse_content(content, f_meta['type'], f_meta['filename'], f_meta['date'])
                                all_records.extend(recs)
                        except: pass
                
                sftp.close()
                transport.close()
                status.update(label="✅ Listo", state="complete", expanded=False)
                
                # Consolidation
                if all_records:
                    df_raw = pd.DataFrame(all_records)
                    # Pivot Logic
                    dfs = []
                    for cols in [['Pedido', 'Fecha Cartoning', 'Archivo Cartoning'], 
                                 ['Pedido', 'Fecha Wave', 'Archivo Wave'],
                                 ['Pedido', 'Fecha SHP', 'Archivo SHP']]:
                        if set(cols).issubset(df_raw.columns):
                            # Clean Column Name Logic for filtering
                            date_col = cols[1] 
                            dfs.append(df_raw[df_raw[date_col].notnull()][cols].drop_duplicates('Pedido'))
                        else:
                            dfs.append(pd.DataFrame(columns=['Pedido']))
                    
                    df_m = pd.merge(dfs[0], dfs[1], on='Pedido', how='outer')
                    df_m = pd.merge(df_m, dfs[2], on='Pedido', how='outer')
                    
                    st.session_state.data_master = df_m
                    st.success(f"Cargados {len(df_m)} registros.")
                else:
                    st.warning("No se encontraron datos.")
                    
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# TAB 2: BÚSQUEDA POR ARCHIVO
# ==========================================
with tab2:
    st.header("Búsqueda y Descarga Masiva")
    st.markdown("Pega aquí los nombres de archivo (uno por línea). El sistema buscará en la carpeta correspondiente según el nombre.")
    st.info("💡 Se buscarán coincidencias parciales (primeros 31-46 caracteres) y archivos de las últimas 3 semanas.")
    
    files_text = st.text_area("Lista de Archivos", height=150, placeholder="CARTONING_2025...\nWave_Confirm_...\nSHP_OBDLV...")
    local_path_input = st.text_input("Carpeta de descarga local", value=os.path.join(os.getcwd(), "descargas"))
    
    btn_download = st.button("BUSCAR Y DESCARGAR ARCHIVOS")
    
    if btn_download:
        if not password:
            st.error("⚠️ Ingresa la contraseña en la barra lateral.")
        elif not files_text.strip():
            st.warning("⚠️ La lista está vacía.")
        else:
            file_list = files_text.splitlines()
            
            # Contenedores de Feedback
            status_container = st.status("Iniciando Búsqueda Masiva...", expanded=True)
            prog_bar = status_container.progress(0)
            log_text = status_container.empty()
            
            try:
                sftp, transport = backend.create_sftp_client(password)
                
                results = []
                generator = backend.download_specific_files(sftp, file_list, local_path_input)
                
                for processed, total, current_file, res_dict in generator:
                    # Actualizar UI
                    pct = processed / total
                    prog_bar.progress(pct)
                    log_text.markdown(f"🔎 Analizando **{processed}/{total}**: `{current_file}`")
                    
                    status_type = "✅" if "✅" in res_dict.get('status','') else "❌"
                    status_container.write(f"{status_type} {res_dict['file']}: {res_dict['status']}")
                    
                    results.append(res_dict)
                
                sftp.close()
                transport.close()
                
                status_container.update(label="✅ Proceso Finalizado", state="complete", expanded=False)
                
                if results:
                    # Mostrar tabla de resultados visual
                    res_df = pd.DataFrame(results)
                    
                    def color_status(val):
                        color = '#d4edda' if '✅' in str(val) else '#f8d7da'
                        return f'background-color: {color}'
                    
                    st.dataframe(res_df.style.applymap(color_status, subset=['status']), use_container_width=True)
                
            except Exception as e:
                status_container.update(label="❌ Error Crítico", state="error")
                st.error(f"Error: {e}")

# ==========================================
# TAB 3: CARGAR HISTÓRICO
# ==========================================
with tab3:
    st.header("Fusionar Datos Externos")
    st.markdown("Sube archivos Excel/CSV previos para unirlos a la tabla de resultados actual.")
    
    uploaded_files = st.file_uploader("Selecciona archivos", accept_multiple_files=True, type=['xlsx', 'csv'])
    
    if uploaded_files:
        if st.button("Procesar y Unir"):
            processed_dfs = []
            
            # Si ya hay data en sesión, empezamos con ella
            if st.session_state.data_master is not None:
                processed_dfs.append(st.session_state.data_master)
            
            for up_file in uploaded_files:
                try:
                    if up_file.name.endswith('.csv'):
                        df_temp = pd.read_csv(up_file)
                    else:
                        df_temp = pd.read_excel(up_file)
                    
                    # Validación simple: Debe tener columna 'Pedido'
                    if 'Pedido' in df_temp.columns:
                        # Asegurar tipo string para merge correcto
                        df_temp['Pedido'] = df_temp['Pedido'].astype(str)
                        processed_dfs.append(df_temp)
                        st.write(f"✅ {up_file.name}: {len(df_temp)} filas cargadas.")
                    else:
                        st.error(f"❌ {up_file.name}: No tiene columna 'Pedido'.")
                except Exception as e:
                    st.error(f"Error en {up_file.name}: {e}")
            
            if processed_dfs:
                # Concatenar y dedupo
                full_df = pd.concat(processed_dfs, ignore_index=True)
                # Opcional: drop_duplicates si se quiere evitar repetición exacta
                # full_df = full_df.drop_duplicates(subset=['Pedido']) 
                
                st.session_state.data_master = full_df
                st.success(f"Fusión completa. Total actual: {len(full_df)} registros.")

# ==========================================
# SECCIÓN COMÚN: RESULTADOS Y EXPORTACIÓN
# ==========================================
st.divider()

if st.session_state.data_master is not None:
    df = st.session_state.data_master
    
    # KPIs Rápidos
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Pedidos en Vista", len(df))
    
    # Filtro Global
    st.subheader("🔍 Buscador Global")
    search_term = st.text_input("Filtrar por Pedido (en toda la data cargada)", placeholder="ID...")
    
    if search_term:
        df_display = df[df['Pedido'].astype(str).str.contains(search_term, case=False, na=False)]
    else:
        df_display = df
        
    st.dataframe(df_display, use_container_width=True)
    
    # Descarga
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    
    st.download_button(
        "💾 Descargar Resultado Actual (.xlsx)", 
        data=output.getvalue(), 
        file_name="Resultado_Logistica.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
