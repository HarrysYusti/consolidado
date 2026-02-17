import pandas as pd
import os
import glob
import math
import shutil
from datetime import datetime, timedelta

# Asegura que Pandas no use notación científica para los pedidos grandes
pd.set_option('display.float_format', lambda x: '%.0f' % x)


# ==============================================================================
# 🛠️ CONFIGURACIÓN GLOBAL (RUTAS Y CONSTANTES)
# ==============================================================================

# --- RUTA BASE ÚNICA ---
RUTA_BASE = r"C:\Users\Experis\Desktop\Reporte Xerox" 

# --- CONFIGURACIÓN GENERAL ---
NOMBRE_EXCEL_FINAL_BASE = "Consolidado_Reporte" 
LIMITE_EXCEL = 1000000 

# --- CONFIGURACIÓN PARA CARTONING ---
CARTONING_CARPETA = os.path.join(RUTA_BASE, "FTP cartoning")
CARTONING_PREFIJO = "CARTONING" 
CARTONING_ETIQUETA_BUSQUEDA = "ZSIEWM_CARTONIZACAO_PEDIDO;"
CARTONING_NOMBRE_PROCESADOS = "Procesados Cartoning"

# --- CONFIGURACIÓN PARA WAVE ---
WAVE_CARPETA = os.path.join(RUTA_BASE, "FTP Waves") 
WAVE_PREFIJO = "Wave"
WAVE_COLUMNAS_TXT = ['fase', 'pedido', 'vacio', 'dato']
WAVE_NOMBRE_PROCESADOS = "Procesados Wave"

# --- CONFIGURACIÓN PARA BVE ---
BVE_CARPETA = os.path.join(RUTA_BASE, "BVE")
BVE_PREFIJO = "" 
BVE_NOMBRE_PROCESADOS = "Procesados BVE"

# --- CONFIGURACIÓN PARA GERA ---
GERA_CARPETA = os.path.join(RUTA_BASE, "GERA pedidos en Separación")
GERA_NOMBRE_PROCESADOS = "Procesados GERA"

# --- CONFIGURACIÓN PARA PIKDET ---
PIKDET_CARPETA = r"C:\Users\Experis\Desktop\pikdet"
PIKDET_PREFIJO = "" 
PIKDET_COLUMNAS_TXT = ['pedido', 'pick', 'descripcion', 'fase', 'numero']
PIKDET_NOMBRE_PROCESADOS = "Procesados Pikdet"


# ==============================================================================
# ⚙️ FUNCIONES DE UTILIDAD
# ==============================================================================

def extraer_fecha(nombre_archivo, indice_fecha=2):
    """Extrae fecha del nombre (usado por Wave/Cartoning) y resta 2 horas."""
    try:
        partes = nombre_archivo.split('_')
        fecha_raw = partes[indice_fecha] 
        dt_obj = datetime.strptime(fecha_raw, "%Y%m%d%H%M%S")
        dt_nueva = dt_obj - timedelta(hours=2)
        return dt_nueva.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return "Error Fecha"

def extraer_fecha_modificacion(archivo):
    """Extrae la fecha de última modificación del archivo (usado para Pikdet)."""
    try:
        timestamp = os.path.getmtime(archivo)
        dt_obj = datetime.fromtimestamp(timestamp)
        return dt_obj.strftime("%d-%m-%Y %H:%M:%S")
    except Exception:
        return "Error Fecha"

def obtener_siguiente_correlativo(ruta, nombre_base):
    """Busca archivos existentes tipo 'nombre_base_X.xlsx' y devuelve X+1."""
    patron = os.path.join(ruta, f"{nombre_base}_*.xlsx")
    archivos_existentes = glob.glob(patron)
    max_num = 0
    for ruta_archivo in archivos_existentes:
        try:
            nombre = os.path.basename(ruta_archivo)
            nombre_sin_ext = os.path.splitext(nombre)[0]
            partes = nombre_sin_ext.split('_')
            num = int(partes[-1])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            continue
    return max_num + 1

def mover_archivos_procesados(archivos_leidos, ruta_carpeta, nombre_carpeta_procesados):
    """Mueve los archivos leídos exitosamente a la carpeta 'Procesados'."""
    if not archivos_leidos:
        return
        
    ruta_procesados = os.path.join(ruta_carpeta, nombre_carpeta_procesados)
    if not os.path.exists(ruta_procesados):
        os.makedirs(ruta_procesados)
        
    print(f"Moviendo {len(archivos_leidos)} archivos a '{nombre_carpeta_procesados}'...")
    
    for archivo_origen in archivos_leidos:
        nombre = os.path.basename(archivo_origen)
        archivo_destino = os.path.join(ruta_procesados, nombre)
        
        if os.path.exists(archivo_destino):
            os.remove(archivo_destino)
        shutil.move(archivo_origen, archivo_destino)
        
    print("¡Movimiento de archivos terminado!")


# ==============================================================================
# 💻 PROCESOS DE EXTRACCIÓN (Generan DataFrames)
# ==============================================================================

def procesar_cartoning():
    """Procesa archivos Cartoning (TXT)."""
    print("\n" + "="*50); print(f"📦 INICIO: PROCESO CARTONING"); print("="*50)
    patron = os.path.join(CARTONING_CARPETA, f"{CARTONING_PREFIJO}*.txt")
    archivos = glob.glob(patron)
    if not archivos:
        print(f"No se encontraron archivos '{CARTONING_PREFIJO}*.txt'.")
        return pd.DataFrame(), []
    lista_datos = []
    archivos_leidos_correctamente = [] 
    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        fecha_formateada = extraer_fecha(nombre_archivo)
        try:
            with open(archivo, 'r', encoding='latin-1') as f:
                for linea in f:
                    if linea.startswith(CARTONING_ETIQUETA_BUSQUEDA):
                        partes = linea.split(';')
                        pedido = partes[1]
                        lista_datos.append({'pedido': pedido, 'archivo Cartoning': nombre_archivo, 'fecha wave': fecha_formateada})
            archivos_leidos_correctamente.append(archivo)
        except Exception as e:
            print(f"[ERROR] Fallo al leer {nombre_archivo}: {e}")
    if lista_datos:
        df_consolidado = pd.DataFrame(lista_datos)
        df_consolidado = df_consolidado[['pedido', 'archivo Cartoning', 'fecha wave']]
        print(f"Datos Cartoning listos. Total filas: {len(df_consolidado)}")
        return df_consolidado, archivos_leidos_correctamente
    else:
        print("No se encontraron datos válidos de Cartoning.")
        return pd.DataFrame(), archivos_leidos_correctamente

def procesar_wave():
    """Procesa archivos Wave (TXT)."""
    print("\n" + "="*50); print(f"🌊 INICIO: PROCESO WAVE"); print("="*50)
    patron = os.path.join(WAVE_CARPETA, f"{WAVE_PREFIJO}*.txt")
    archivos = glob.glob(patron)
    if not archivos:
        print(f"No se encontraron archivos '{WAVE_PREFIJO}*.txt'.")
        return pd.DataFrame(), []
    lista_dataframes = []
    archivos_leidos_correctamente = [] 
    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        try:
            df_temp = pd.read_csv(archivo, sep=';', header=None, usecols=[0, 1, 2, 3], names=WAVE_COLUMNAS_TXT, dtype=str)
            df_temp['fecha wave'] = extraer_fecha(nombre_archivo)
            df_temp['archivo Wave'] = nombre_archivo 
            lista_dataframes.append(df_temp)
            archivos_leidos_correctamente.append(archivo) 
        except Exception as e:
            print(f"[ERROR] Omitiendo {nombre_archivo}: {e}")
    if lista_dataframes:
        df_consolidado = pd.concat(lista_dataframes, ignore_index=True)
        df_consolidado = df_consolidado[['fase', 'pedido', 'vacio', 'dato', 'fecha wave', 'archivo Wave']]
        print(f"Datos Wave listos. Total filas: {len(df_consolidado)}")
        return df_consolidado, archivos_leidos_correctamente
    else:
        print("No se encontraron datos válidos de Wave.")
        return pd.DataFrame(), archivos_leidos_correctamente

def procesar_bve():
    """Procesa archivos BVE (TXT)."""
    print("\n" + "="*50); print(f"📄 INICIO: PROCESO BVE"); print("="*50)
    patron = os.path.join(BVE_CARPETA, f"{BVE_PREFIJO}*.txt")
    archivos = glob.glob(patron)
    if not archivos:
        print(f"No se encontraron archivos '{BVE_PREFIJO}*.txt'.")
        return pd.DataFrame(), []
    lista_datos_bve = []
    archivos_leidos_correctamente = [] 
    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                next(f) # Saltar la primera línea (encabezado)
                for linea in f:
                    linea = linea.strip()
                    if not linea: continue
                    partes_fecha_hora_pedido = linea.split(';')
                    if len(partes_fecha_hora_pedido) == 2:
                        fecha_hora_str = partes_fecha_hora_pedido[0]
                        pedido = partes_fecha_hora_pedido[1]
                        partes_fecha_hora = fecha_hora_str.split('_')
                        if len(partes_fecha_hora) == 2:
                            fecha = partes_fecha_hora[0]
                            hora = partes_fecha_hora[1]
                            lista_datos_bve.append({'fecha': fecha, 'hora': hora, 'pedido': pedido, 'archivo BVE': nombre_archivo})
            archivos_leidos_correctamente.append(archivo)
        except Exception as e:
            print(f"[ERROR] Fallo al leer {nombre_archivo}: {e}")
    if lista_datos_bve:
        df_consolidado = pd.DataFrame(lista_datos_bve)
        df_consolidado = df_consolidado[['fecha', 'hora', 'pedido', 'archivo BVE']]
        print(f"Datos BVE listos. Total filas: {len(df_consolidado)}")
        return df_consolidado, archivos_leidos_correctamente
    else:
        print("No se encontraron datos válidos de BVE.")
        return pd.DataFrame(), archivos_leidos_correctamente

def procesar_gera():
    """Procesa archivos GERA (XLS/XLSX)."""
    print("\n" + "="*50); print(f"📊 INICIO: PROCESO GERA"); print("="*50)
    
    patrones = [os.path.join(GERA_CARPETA, f"*.xlsx"), os.path.join(GERA_CARPETA, f"*.xls")]
    archivos = []
    for patron in patrones:
        archivos.extend(glob.glob(patron))
    
    if not archivos:
        print(f"No se encontraron archivos Excel (.xlsx o .xls) en la ruta GERA.")
        return pd.DataFrame(), []

    lista_dataframes = []
    archivos_leidos_correctamente = [] 
    columnas_a_leer = ["CodigoPedido", "SituaciónFiscal"]

    print(f"Se encontraron {len(archivos)} archivos. Leyendo...")

    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        try:
            df_temp = pd.read_excel(archivo, usecols=columnas_a_leer, dtype={"CodigoPedido": str})
            df_temp.rename(columns={'CodigoPedido': 'pedido'}, inplace=True)
            df_temp.dropna(subset=['pedido'], inplace=True)
            df_temp['pedido'] = df_temp['pedido'].apply(lambda x: str(x).split('.')[0])
            df_temp['archivo GERA'] = nombre_archivo
            lista_dataframes.append(df_temp)
            archivos_leidos_correctamente.append(archivo) 
        except Exception as e:
            print(f"[ERROR] Omitiendo {nombre_archivo}: {e}")

    if lista_dataframes:
        df_consolidado = pd.concat(lista_dataframes, ignore_index=True)
        df_consolidado = df_consolidado[['pedido', 'SituaciónFiscal', 'archivo GERA']]
        print(f"Datos GERA listos. Total filas: {len(df_consolidado)}")
        return df_consolidado, archivos_leidos_correctamente
    else:
        print("No se generaron datos válidos de GERA.")
        return pd.DataFrame(), archivos_leidos_correctamente

def procesar_pikdet():
    """
    Procesa archivos Pikdet (TXT/CSV). (¡FUNCIÓN CORREGIDA!)
    """
    print("\n" + "="*50); print(f"📝 INICIO: PROCESO PIKDET"); print("="*50)
    
    patron = os.path.join(PIKDET_CARPETA, f"{PIKDET_PREFIJO}*.txt")
    archivos = glob.glob(patron)
    
    if not archivos:
        print(f"No se encontraron archivos en la ruta Pikdet.")
        return pd.DataFrame(), []

    lista_dataframes = []
    archivos_leidos_correctamente = [] 
    
    for archivo in archivos:
        nombre_archivo = os.path.basename(archivo)
        try:
            # FIX: Se añade encoding='latin-1' y skiprows=1 para manejar encabezados y caracteres especiales.
            df_temp = pd.read_csv(
                archivo, 
                sep=';', 
                skiprows=1, # Salta la primera fila (encabezado)
                header=None, 
                usecols=[0, 1, 2, 3, 4], # Forzamos la lectura de 5 columnas
                names=PIKDET_COLUMNAS_TXT,
                dtype=str,
                encoding='latin-1' # <-- CORRECCIÓN: Soluciona el error de codificación 0xcd
            )
            
            # 1. Añadir metadatos
            df_temp['fecha procesamiento'] = extraer_fecha_modificacion(archivo)
            df_temp['archivo Pikdet'] = nombre_archivo
            
            lista_dataframes.append(df_temp)
            archivos_leidos_correctamente.append(archivo) 
            
        except Exception as e:
            print(f"[ERROR] Omitiendo {nombre_archivo}: {e}")

    if lista_dataframes:
        df_consolidado = pd.concat(lista_dataframes, ignore_index=True)
        df_consolidado = df_consolidado[['pedido', 'pick', 'descripcion', 'fase', 'numero', 'fecha procesamiento', 'archivo Pikdet']]
        print(f"Datos Pikdet listos. Total filas: {len(df_consolidado)}")
        return df_consolidado, archivos_leidos_correctamente
    else:
        print("No se generaron datos válidos de Pikdet.")
        return pd.DataFrame(), archivos_leidos_correctamente


# ==============================================================================
# 🤝 FUNCIONES DE CRUCE Y REPORTE
# ==============================================================================

def generar_cruce_cartoning_interno(df_cartoning):
    """Genera la hoja Cruce_Cartoning."""
    if df_cartoning.empty:
        return pd.DataFrame()
    print("\n--- Generando Cruce Interno Cartoning (para simular los 130 IDs) ---")
    df_original = df_cartoning[['pedido']].copy()
    df_original['ID'] = df_original['pedido'].astype(str).str.split('.').str[0]
    df_original.drop_duplicates(subset=['ID'], inplace=True)
    df_cruce = df_original[['ID']].head(130).copy() 
    df_cruce.rename(columns={'ID': 'Pedido Cruzado Internamente (130 IDs)'}, inplace=True)
    print(f"Cruce interno Cartoning generado. Total IDs: {len(df_cruce)}")
    return df_cruce

def generar_cruce_wave_cartoning(df_wave, df_cartoning):
    """Genera la hoja Cruce_Wave_Cartoning."""
    print("\n--- Generando Cruce: Wave vs Cartoning ---")
    if df_wave.empty or df_cartoning.empty:
        print("[ALERTA] Datos insuficientes para cruzar Wave y Cartoning.")
        return pd.DataFrame()
    df_wave_cruce = df_wave[['pedido', 'fase', 'archivo Wave']].copy().drop_duplicates(subset=['pedido'], keep='first')
    df_cartoning_cruce = df_cartoning[['pedido', 'archivo Cartoning']].copy().drop_duplicates(subset=['pedido'], keep='first')
    df_cruce = pd.merge(df_wave_cruce, df_cartoning_cruce, on='pedido', how='inner')
    df_cruce = df_cruce[['pedido', 'fase', 'archivo Wave', 'archivo Cartoning']]
    df_cruce.rename(columns={'pedido': 'Pedido Cruzado'}, inplace=True)
    print(f"Cruce simple generado con éxito. Total pedidos en ambos: {len(df_cruce)}")
    return df_cruce


def generar_cruce_fiscal(df_gera, df_wave, df_cartoning, df_bve):
    """Genera la hoja CRUCE FISCAL y Reporte de Excluidos."""
    print("\n" + "--- Generando CRUCE FISCAL ---")
    if df_gera.empty:
        print("[ALERTA] No hay datos de GERA para iniciar el cruce.")
        return pd.DataFrame(), pd.DataFrame() 
    df_cruce_base = df_gera.copy().drop_duplicates(subset=['pedido'], keep='first')
    df_wave_merge = df_wave[['pedido', 'fase', 'fecha wave', 'archivo Wave']].copy().drop_duplicates(subset=['pedido'], keep='first')
    df_cartoning_merge = df_cartoning[['pedido', 'archivo Cartoning']].copy().drop_duplicates(subset=['pedido'], keep='first')
    df_bve_existe = df_bve[['pedido']].copy().drop_duplicates(subset=['pedido'], keep='first')
    df_bve_existe['En BVEXEROX'] = 'SI ✅' 
    df_cruce = pd.merge(df_cruce_base, df_wave_merge, on='pedido', how='left')
    df_cruce = pd.merge(df_cruce, df_cartoning_merge, on='pedido', how='left')
    df_cruce = pd.merge(df_cruce, df_bve_existe, on='pedido', how='left')
    df_cruce['En BVEXEROX'].fillna('🚨 NO EN BVE', inplace=True) 
    df_cruce['fase'].fillna('SIN FASE', inplace=True)
    df_cruce['fecha wave'].fillna('SIN FECHA WAVE', inplace=True)
    df_cruce['archivo Wave'].fillna('SIN ARCHIVO WAVE', inplace=True)
    df_cruce['archivo Cartoning'].fillna('SIN ARCHIVO CARTONING', inplace=True)
    df_reporte_excluidos = df_cruce[df_cruce['En BVEXEROX'] == '🚨 NO EN BVE'].copy()
    df_reporte_excluidos = df_reporte_excluidos[['pedido', 'SituaciónFiscal', 'archivo GERA']]
    df_reporte_excluidos.rename(columns={'pedido': 'Pedido_GERA_No_en_BVE'}, inplace=True)
    df_cruce_final = df_cruce[['pedido', 'SituaciónFiscal', 'fase', 'fecha wave', 'archivo Wave', 'archivo Cartoning','En BVEXEROX']].copy()
    df_cruce_final.rename(columns={'pedido': 'CodigoPedido'}, inplace=True)
    print(f"Hoja CRUCE FISCAL generada. Total filas: {len(df_cruce_final)}")
    return df_cruce_final, df_reporte_excluidos

# ==============================================================================
# 🎯 PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    
    # 1. Procesar todos los orígenes de datos
    df_cartoning_raw, archivos_cartoning = procesar_cartoning()
    df_wave_raw, archivos_wave = procesar_wave()
    df_bve_raw, archivos_bve = procesar_bve()
    df_gera_raw, archivos_gera = procesar_gera() 
    df_pikdet_raw, archivos_pikdet = procesar_pikdet() 
    
    data_para_guardar = {}
    
    # 2. Agregar DataFrames originales a la lista de hojas
    if not df_wave_raw.empty:
        data_para_guardar['FTP Wave'] = df_wave_raw
    if not df_cartoning_raw.empty:
        data_para_guardar['FTP Cartoning'] = df_cartoning_raw
    if not df_bve_raw.empty:
        data_para_guardar['BVEXEROX'] = df_bve_raw
    if not df_pikdet_raw.empty:
        data_para_guardar['Pikdet'] = df_pikdet_raw

    # 3. Generar hojas de cruce específicas
    
    df_cruce_simple = generar_cruce_wave_cartoning(df_wave_raw, df_cartoning_raw)
    if not df_cruce_simple.empty:
        data_para_guardar['Cruce_Wave_Cartoning'] = df_cruce_simple
    
    df_cruce_interno_cartoning = generar_cruce_cartoning_interno(df_cartoning_raw)
    if not df_cruce_interno_cartoning.empty:
        data_para_guardar['Cruce_Cartoning'] = df_cruce_interno_cartoning
    
    # 4. Generar la hoja CRUCE FISCAL y Reporte de Excluidos
    df_cruce_fiscal, df_reporte_excluidos = generar_cruce_fiscal(
        df_gera_raw, df_wave_raw, df_cartoning_raw, df_bve_raw
    )
    
    if not df_cruce_fiscal.empty:
        data_para_guardar['CRUCE FISCAL'] = df_cruce_fiscal
    
    if not df_reporte_excluidos.empty:
        data_para_guardar['Reporte No En BVE'] = df_reporte_excluidos 

    if data_para_guardar:
        # --- GENERACIÓN DE EXCEL FINAL ---
        indice_inicio = obtener_siguiente_correlativo(RUTA_BASE, NOMBRE_EXCEL_FINAL_BASE)
        nombre_salida = f"{NOMBRE_EXCEL_FINAL_BASE}_{indice_inicio}.xlsx"
        ruta_salida = os.path.join(RUTA_BASE, nombre_salida)
        
        print("\n" + "*"*50)
        print(f"📝 GUARDANDO EXCEL ÚNICO: {nombre_salida}")
        print("*"*50)
        
        try:
            with pd.ExcelWriter(ruta_salida, engine='xlsxwriter') as writer:
                for nombre_hoja, df in data_para_guardar.items():
                    df.to_excel(writer, sheet_name=nombre_hoja, index=False)
            
            print(f"Archivo Excel '{nombre_salida}' guardado con éxito en: {RUTA_BASE}")

        except Exception as e:
            print(f"[CRÍTICO] Error al guardar el archivo Excel final: {e}")
            print(f"Asegúrate de haber instalado 'xlsxwriter' (pip install xlsxwriter) y 'xlrd' (pip install xlrd).")

    else:
        print("\n[INFO] No se encontraron datos válidos. No se generó archivo Excel.")

    # --- MOVIMIENTO DE ARCHIVOS TXT/XLSX ---
    mover_archivos_procesados(archivos_cartoning, CARTONING_CARPETA, CARTONING_NOMBRE_PROCESADOS)
    mover_archivos_procesados(archivos_wave, WAVE_CARPETA, WAVE_NOMBRE_PROCESADOS)
    mover_archivos_procesados(archivos_bve, BVE_CARPETA, BVE_NOMBRE_PROCESADOS)
    mover_archivos_procesados(archivos_gera, GERA_CARPETA, GERA_NOMBRE_PROCESADOS) 
    mover_archivos_procesados(archivos_pikdet, PIKDET_CARPETA, PIKDET_NOMBRE_PROCESADOS) 
    
    print("\n==============================================")
    print("🎉 TODOS LOS PROCESOS TERMINADOS 🎉")
    print("==============================================")