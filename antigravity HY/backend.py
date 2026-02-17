import paramiko
import pandas as pd
from datetime import datetime, timedelta
import io
import stat
import os

# --- CONFIGURACIÓN PREDEFINIDA ---
SFTP_HOST = "10.212.6.90"
SFTP_PORT = 22
SFTP_USER = "gera_cl21"
# La contraseña se pasa desde la UI

# Rutas Base en el servidor SFTP
PATH_CARTONING = "/EWM/ewm_to_gera/cartoning/02_Old"
PATH_WAVE = "/EWM/ewm_to_gera/waveconfirm/02_Old"
PATH_SHIP = "/EWM/ewm_to_gera/outbounddeliveryconfirm/02_Old"

def create_sftp_client(password):
    """
    Establece una conexión SFTP segura usando Paramiko.
    
    Args:
        password (str): Contraseña del usuario SFTP.
        
    Returns:
        tuple: (cliente_sftp, transporte) para poder cerrarlos después.
        
    Raises:
        ConnectionError: Si falla la conexión.
    """
    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp, transport
    except Exception as e:
        raise ConnectionError(f"Error conectando a SFTP: {e}")

def parse_filename_date(filename, file_type):
    """
    Extrae la fecha del nombre del archivo y ajusta la zona horaria (-2 horas).
    Soporta nombres con variantes como 'SIMULATION' buscando dinámicamente
    el timestamp de 14 dígitos.
    
    Args:
        filename (str): Nombre del archivo.
        file_type (str): Tipo de archivo ('cartoning', 'wave', 'ship').
        
    Returns:
        datetime: Objeto datetime ajustado o None si falla el parsing.
    """
    try:
        parts = filename.split('_')
        date_str = None
        
        # ESTRATEGIA ROBUSTA: Buscar cualquier segmento que sea 100% numérico y de 14 dígitos.
        # Esto cubre:
        # - CARTONING_2025... (Index 1)
        # - CARTONING_SIMULATION_2025... (Index 2)
        # - Wave_2025... (Index 1)
        # - SHP_..._DECENTRAL_2025... (Index 4)
        for part in parts:
            if part.isdigit() and len(part) == 14:
                date_str = part
                break
        
        # Fallback específico para ShipConfirm si la estrategia general falla 
        # (por si el timestamp tiene sufijos pegados no separados por _)
        if not date_str and file_type == 'ship' and len(parts) > 4:
            candidate = parts[4]
            # Si tiene al menos 14 chars y los primeros 14 son dígitos
            if len(candidate) >= 14 and candidate[:14].isdigit():
                date_str = candidate[:14]

        if not date_str:
            return None

        # Parsing del string encontrado
        dt = datetime.strptime(date_str, "%Y%m%d%H%M%S")
        
        # Ajuste de Zona Horaria: Restar 2 horas
        dt = dt - timedelta(hours=2)
        return dt
    except (IndexError, ValueError):
        return None

def filter_files_by_date(sftp, remote_path, file_type, target_date=None, days_back=None, start_time=None, end_time=None):
    """
    Lista archivos y filtra usando la FECHA DE MODIFICACIÓN (st_mtime) del servidor SFTP.
    
    Args:
        sftp: Cliente SFTP.
        remote_path (str): Ruta.
        file_type (str): Tipo para validar prefijo.
        target_date (date): Fecha buscada (Manual).
        days_back (int): Días atrás (Automático).
        start_time (time): Hora inicio filtro.
        end_time (time): Hora fin filtro.
    """
    files_to_process = []
    
    # Fecha de corte para Automático
    cutoff_date = None
    if days_back:
        cutoff_date = datetime.now() - timedelta(days=days_back)

    try:
        # Usamos listdir_attr para obtener metadatos sin descargar
        file_attributes = sftp.listdir_attr(remote_path)
        
        for attr in file_attributes:
            fname = attr.filename
            
            # 1. Filtro por Tipo (Nombre)
            fname_upper = fname.upper()
            if file_type == "cartoning" and not fname_upper.startswith("CARTONING"): continue
            if file_type == "wave" and not fname_upper.startswith("WAVE"): continue
            if file_type == "ship" and not fname_upper.startswith("SHP"): continue

            # 2. Obtener Fecha de Modificación del Servidor
            # st_mtime es timestamp Unix. Lo convertimos a datetime local.
            mtime_dt = datetime.fromtimestamp(attr.st_mtime)
            
            match = False
            
            if target_date:
                # Modo Manual: Coincidencia por fecha de modificación
                if mtime_dt.date() == target_date:
                    match = True
                    # Filtro Horario sobre la hora de modificación
                    if start_time and end_time:
                         if not (start_time <= mtime_dt.time() <= end_time):
                             match = False
            elif cutoff_date:
                # Modo Automático
                if mtime_dt >= cutoff_date:
                    match = True
            
            if match:
                # Para el reporte, intentamos mantener la fecha del nombre si existe, 
                # si no, usamos la de modificación como fallback.
                parsed_date = parse_filename_date(fname, file_type)
                final_date = parsed_date if parsed_date else mtime_dt

                files_to_process.append({
                    "filename": fname,
                    "date": final_date,
                    "path": f"{remote_path}/{fname}",
                    "type": file_type
                })
                
    except IOError as e:
        print(f"Error accediendo a {remote_path}: {e}")
        return []
    
    return files_to_process

def parse_content(content_bytes, file_type, filename, file_date):
    """
    Parsea el contenido del archivo (bytes) y extrae información de pedidos.
    
    Args:
        content_bytes (bytes): Contenido crudo del archivo.
        file_type (str): Tipo de archivo.
        filename (str): Nombre del archivo (para referencia).
        file_date (datetime): Fecha extraída del nombre.
        
    Returns:
        list: Lista de diccionarios con la info extraída.
    """
    records = []
    try:
        # Decodificar bytes a string
        text = content_bytes.decode('utf-8', errors='ignore')
        lines = text.splitlines()

        if file_type == "cartoning":
            # REGLA: Línea contiene "ZSIEWM_CARTONIZACAO_PEDIDO;" -> Split por ';' tomar índice 1
            for line in lines:
                if "ZSIEWM_CARTONIZACAO_PEDIDO;" in line:
                    parts = line.split(';')
                    if len(parts) > 1:
                        order_id = parts[1].strip()
                        records.append({
                            "Pedido": order_id,
                            "Fecha Cartoning": file_date,
                            "Archivo Cartoning": filename
                        })

        elif file_type == "wave":
            # REGLA: CSV separado por ';'. Columna 1 (segunda columna).
            for line in lines:
                parts = line.split(';')
                if len(parts) >= 2:
                    order_id = parts[1].strip()
                    # Ignorar encabezados o líneas vacías
                    if order_id.lower() == "pedido" or order_id == "": continue
                    
                    records.append({
                        "Pedido": order_id,
                        "Fecha Wave": file_date,
                        "Archivo Wave": filename
                    })

        elif file_type == "ship":
            # REGLA: Línea contiene "E1BPOBDLVHDRCON;" -> Split por ';' tomar índice 1
            for line in lines:
                if "E1BPOBDLVHDRCON;" in line:
                    parts = line.split(';')
                    if len(parts) > 1:
                        order_id = parts[1].strip()
                        records.append({
                            "Pedido": order_id,
                            "Fecha SHP": file_date,
                            "Archivo SHP": filename
                        })
                        
    except Exception as e:
        print(f"Error parseando contenido de {filename}: {e}")
        
    return records

def determine_remote_path(filename):
    """
    Determina la ruta remota basada en el prefijo del archivo.
    """
    fname_upper = filename.upper()
    if fname_upper.startswith("CARTONING"):
        return PATH_CARTONING
    elif fname_upper.startswith("WAVE"):
        return PATH_WAVE
    elif fname_upper.startswith("SHP"):
        return PATH_SHIP
    return None

def download_specific_files(sftp, file_names, local_dir):
    """
    GENERADOR: Busca y descarga lista de archivos.
    Yields: (processed_count, total_count, current_file_name, result_dict)
    """
    # 1. Preparar entorno local
    if not os.path.exists(local_dir):
        try: os.makedirs(local_dir)
        except OSError: pass

    three_weeks_ago = datetime.now() - timedelta(weeks=3)
    
    # 2. Análisis de Inputs
    searches_by_path = {PATH_CARTONING: [], PATH_WAVE: [], PATH_SHIP: []}
    path_params = {
        PATH_CARTONING: (39, 'cartoning'),
        PATH_WAVE: (31, 'wave'),
        PATH_SHIP: (46, 'ship')
    }

    # Limpieza y conteo real de tareas
    valid_inputs = [f.strip() for f in file_names if f.strip()]
    total_files = len(valid_inputs)
    processed_count = 0
    
    # Distribuir en grupos
    files_map = {} # Map filename -> original input
    
    for fname in valid_inputs:
        files_map[fname] = fname
        remote_base = determine_remote_path(fname)
        if remote_base:
            searches_by_path[remote_base].append(fname)
        else:
            # Caso inmediato: Tipo desconocido
            processed_count += 1
            yield (processed_count, total_files, fname, {
                "file": fname, "status": "❌ Ignorado", 
                "msg": "No coincide con Cartoning, Wave o Ship"
            })

    # 3. Procesar Grupos
    for remote_path, search_list in searches_by_path.items():
        if not search_list: continue
        
        match_len, file_type = path_params[remote_path]
        
        # Intentar listar directorio
        try:
            # Esto puede tardar, se podría yieldear un status de "Listando..." si fuera necesario,
            # pero el contrato es yield resultado.
            remote_files = sftp.listdir(remote_path)
            
            for target_name in search_list:
                processed_count += 1
                target_prefix = target_name[:match_len]
                found_match = None
                
                # Búsqueda en memoria
                for r_file in remote_files:
                    if r_file.startswith(target_prefix):
                        # Analizar fecha
                        f_date = parse_filename_date(r_file, file_type)
                        if f_date and f_date >= three_weeks_ago:
                            found_match = r_file
                            break 
                
                result = None
                if found_match:
                    try:
                        full_remote = f"{remote_path}/{found_match}"
                        full_local = os.path.join(local_dir, found_match)
                        sftp.get(full_remote, full_local)
                        result = {
                            "file": target_name, "status": "✅ Descargado",
                            "msg": f"Encontrado: {found_match}", "path": full_local
                        }
                    except Exception as e:
                        result = {"file": target_name, "status": "❌ Error Descarga", "msg": str(e)}
                else:
                    result = {
                        "file": target_name, "status": "❌ No Encontrado", 
                        "msg": "No existe o es antiguo (>3 semanas)"
                    }
                
                yield (processed_count, total_files, target_name, result)
                    
        except Exception as e:
            # Fallo masivo en carpeta (ej: desconexión)
            for target_name in search_list:
                processed_count += 1
                yield (processed_count, total_files, target_name, {
                    "file": target_name, "status": "❌ Error Acceso", 
                    "msg": f"Fallo al listar carpeta: {e}"
                })
