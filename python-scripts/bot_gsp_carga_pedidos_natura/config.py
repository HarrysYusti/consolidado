# Archivo: config.py
import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Credenciales y URLs ---
LOGIN_URL = "https://gsp.natura.com/login?Country=CL"
USUARIO = os.getenv("REAL_NATURA_USER", "default_user")
PASSWORD = os.getenv("REAL_NATURA_PASS", "default_pass")

# --- Rutas de Carpetas ---
BASE_PEDIDOS_PATH = Path(r"Y:\Publico\RPA\Bot Carga Pedidos\Pedidos\PedidosB")

# --- Configuración de Reporte (SECCIÓN ACTUALIZADA) ---
RUTA_REPORTE_PRINCIPAL = Path(r"Y:\Publico\RPA\Bot Carga Pedidos")
RUTA_REPORTE_COPIA = Path(r"E:\Proyectos\EnvioCorreoPreventa\Insumos")

# --- Parámetros de Búsqueda y Ejecución ---
FILTRA_FECHA = False
# Si FILTRA_FECHA es True, el bot buscará archivos con la fecha del día
TIMEZONE_TZ = "America/Santiago"
PAUSA_ENTRE_PEDIDOS = 3

# --- NUEVA VARIABLE ---
# Si FILTRA_FECHA es True, el bot buscará archivos con este código de fecha específico.
CODIGO_FECHA_ESPECIFICO = "202516" 

# --- Expresión Regular para Nombres de Archivo ---
FILENAME_REGEX = re.compile(
    r"""(?ix)
    \bBotAten
    [\s._-]*
    (?P<id>\d{4,12})
    \s*[_\-\s]\s*
    (?P<date>\d{6})
    \.xlsx\b
    """
)

# --- Configuración del Ciclo Objetivo ---
CICLO_OBJETIVO = "Ciclo 2025/16"