"""
cargar_desde_drive.py
─────────────────────
Agrega una lista explícita de documentos de Google Drive hacia un Notebook
de NotebookLM usando el servidor MCP local.

El script lee la lista `DOCUMENTOS_A_CARGAR` desde config.py, y añade como
fuente en NotebookLM todos los que aún no estén vinculados, extrayendo el ID
incluso si pegas la URL completa.

Uso:
    python cargar_desde_drive.py

Requisitos previos:
    1. Autenticado con:  python -m notebooklm_mcp.auth_cli
    2. config.py configurado con la lista de documentos
"""

import asyncio
import sys
import os
import json
import datetime
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ── Configuración centralizada ────────────────────────────────
from config import (
    NOTEBOOK_ID,
    RUTA_CARPETA_LOCAL_DRIVE,
    EXTENSION_A_DOCTYPE,
    DRIVE_DOC_TYPE_DEFAULT,
)
import glob
# ─────────────────────────────────────────────────────────────

def extraer_id_drive(url_o_id: str) -> str | None:
    """Intenta extraer el ID de 33 a 44 caracteres válido de un enlace de Drive.
    Si ya parece un ID limpio, lo devuelve tal cual.
    """
    # Si contiene "/d/", extraer el ID
    m = re.search(r"/d/([a-zA-Z0-9_-]{25,})", url_o_id)
    if m:
        return m.group(1)
    # Si contiene "id=", extraer
    m = re.search(r"id=([a-zA-Z0-9_-]{25,})", url_o_id)
    if m:
        return m.group(1)
    # Si es exactamente un ID sin barra ni http
    if re.match(r"^[a-zA-Z0-9_-]{25,}$", url_o_id.strip()):
        return url_o_id.strip()
    return None

def doc_type_para_nombre(nombre: str) -> str | None:
    """Devuelve el doc_type según la extensión en el nombre.
    Tipos válidos: 'doc', 'slides', 'sheets', 'pdf'
    """
    _, ext = os.path.splitext(nombre.lower())
    if ext in EXTENSION_A_DOCTYPE:
        return EXTENSION_A_DOCTYPE[ext]
    return DRIVE_DOC_TYPE_DEFAULT

async def obtener_fuentes_existentes(session: ClientSession) -> tuple[set[str], set[str]]:
    """Devuelve (ids_existentes, nombres_existentes) ya vinculados al notebook."""
    result = await session.call_tool(
        "source_list_drive",
        arguments={"notebook_id": NOTEBOOK_ID}
    )
    raw = result.content[0].text
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}

    ids = set()
    nombres = set()
    for f in data.get("syncable_sources", []):
        doc_id = f.get("document_id") or f.get("id", "")
        titulo = f.get("title", "")
        if doc_id:
            ids.add(doc_id)
        if titulo:
            nombres.add(titulo.strip().lower())
            
    # Extraemos todos los strings del resultado raw de notebook_get para atrapar PDFs subidos
    try:
        get_res = await session.call_tool("notebook_get", arguments={"notebook_id": NOTEBOOK_ID})
        nb_data = json.loads(get_res.content[0].text)
        
        def extract_strings(obj):
            if isinstance(obj, str) and len(obj) > 3:
                nombres.add(obj.strip().lower())
            elif isinstance(obj, list):
                for item in obj: extract_strings(item)
            elif isinstance(obj, dict):
                for val in obj.values(): extract_strings(val)
                
        if "notebook" in nb_data:
            extract_strings(nb_data["notebook"])
            
    except Exception:
        pass

    return ids, nombres

async def agregar_fuente(session: ClientSession, doc_id: str, titulo: str, doc_type: str) -> dict:
    """Agrega un documento de Google Drive al notebook."""
    result = await session.call_tool(
        "notebook_add_drive",
        arguments={
            "notebook_id": NOTEBOOK_ID,
            "document_id": doc_id,
            "title": titulo,
            "doc_type": doc_type,
        }
    )
    raw = result.content[0].text
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}

def _guardar_log(lines: list[str]):
    with open("historial_sincronizaciones.md", "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


async def run():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 60)
    print(f"  Cargador de Drive (Manifiesto Local) → NotebookLM")
    print(f"  Notebook         : {NOTEBOOK_ID}")
    print(f"  Ruta Local       : {RUTA_CARPETA_LOCAL_DRIVE}")
    print(f"  Inicio           : {timestamp}")
    print("=" * 60)

    log_lines = [
        f"\n---",
        f"# Carga desde Manifiesto Local ({timestamp})",
        f"- Notebook: `{NOTEBOOK_ID}`",
        "",
    ]

    # 1. Buscar archivo manifiesto_*.txt en la ruta
    patron = os.path.join(RUTA_CARPETA_LOCAL_DRIVE, "manifiesto_*.txt")
    archivos_manifiesto = glob.glob(patron)
    
    if not archivos_manifiesto:
        msg = f"⚠️ No se encontró ningún archivo que empiece por 'manifiesto_' en la ruta: {RUTA_CARPETA_LOCAL_DRIVE}"
        print(f"\n{msg}\nAsegúrate de que la ruta en config.py sea correcta y exista el archivo .txt.")
        log_lines.append(msg)
        _guardar_log(log_lines)
        return

    # Usaremos el primer archivo que encuentre
    archivo_txt = archivos_manifiesto[0]
    print(f"📎 Leyendo manifiesto: {os.path.basename(archivo_txt)}")
    
    documentos = []
    try:
        with open(archivo_txt, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # Ejecutamos el archivo en un entorno encapsulado para extraer la lista Python
        variables_locales = {}
        exec(contenido, {}, variables_locales)
        documentos = variables_locales.get("DOCUMENTOS_A_CARGAR", [])
        
    except Exception as e:
        msg = f"❌ Error al leer el manifiesto: {e}"
        print(f"\n{msg}")
        log_lines.append(msg)
        _guardar_log(log_lines)
        return

    if not documentos:
        print("\n⚠️ El archivo manifiesto no contiene datos válidos o la lista DOCUMENTOS_A_CARGAR está vacía.")
        log_lines.append("⚠️ Operación cancelada: lista de documentos vacía.")
        _guardar_log(log_lines)
        return

    print(f"  Total a procesar : {len(documentos)} documentos extraídos del txt.")

    # Procesar y limpiar la lista
    procesados = []
    for doc in documentos:
        url_o_id = doc.get("id_o_url", "")
        nombre = doc.get("nombre", "Sin_Nombre")
        
        doc_id = extraer_id_drive(url_o_id)
        if not doc_id:
            msg = f"  🚫 No se pudo extraer el ID de: {url_o_id}"
            print(msg)
            log_lines.append(f"- {msg}")
            continue
            
        doc_type = doc_type_para_nombre(nombre)
        procesados.append({"id": doc_id, "nombre": nombre, "doc_type": doc_type})

    if not procesados:
        print("\n✨ No hay documentos válidos para intentar agregar.")
        _guardar_log(log_lines)
        return

    # ── Conectar al MCP y filtrar duplicados ───────────────
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "notebooklm_mcp.server"],
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("\n✅ Conexión MCP establecida.")

                print("\n📋 Consultando las fuentes ya vinculadas al notebook (por ID y Título)...")
                fuentes_ids, fuentes_nombres = await obtener_fuentes_existentes(session)
                print(f"   → Se detectaron {len(fuentes_nombres)} nombres / {len(fuentes_ids)} IDs únicos ya presentes.")

                # Omitir si el ID exacto ya existe, O si el string nombre (con o sin extensión) coincide
                nuevos = []
                for p in procesados:
                    if p["id"] in fuentes_ids:
                        continue
                    
                    nombre_completo = p["nombre"].strip().lower()
                    nombre_sin_ext = os.path.splitext(nombre_completo)[0]
                    
                    if nombre_completo in fuentes_nombres or nombre_sin_ext in fuentes_nombres:
                        continue
                    
                    nuevos.append(p)
                    
                ya_estan = len(procesados) - len(nuevos)

                print(f"\n   {ya_estan} de tu lista ya estaban vinculados → se omiten.")
                print(f"   {len(nuevos)} archivo(s) nuevo(s) para importar.")

                if not nuevos:
                    print("\n✨ Todos los documentos de tu lista ya están en el notebook.")
                    log_lines.append("✨ Todos los documentos de la lista ya estaban vinculados.")
                    _guardar_log(log_lines)
                    return

                # ── Agregar cada archivo nuevo ─────────────
                print(f"\n⬆️  Agregando {len(nuevos)} archivo(s) a NotebookLM...\n")
                log_lines.append("## Documentos procesados\n")

                exitosos = 0
                fallidos = 0
                for archivo in nuevos:
                    doc_id = archivo["id"]
                    nombre = archivo["nombre"]
                    doc_type = archivo["doc_type"]

                    print(f"  ⬆️  {nombre} [{doc_type}]", end=" ", flush=True)
                    try:
                        resultado = await agregar_fuente(session, doc_id, nombre, doc_type)
                        estado = resultado.get("status", "")
                        
                        # MCP devuelve success/added o simplemente los datos de la fuente originada
                        if estado in ("success", "added", "ok") or resultado.get("source_id"):
                            print("✅")
                            log_lines.append(f"- ✅ **{nombre}** (ID: `{doc_id}` | `{doc_type}`)")
                            exitosos += 1
                        else:
                            err = resultado.get("error", str(resultado))
                            print(f"❌  {err}")
                            log_lines.append(f"- ❌ **{nombre}**: {err}")
                            fallidos += 1
                    except Exception as ex:
                        print(f"❌  {ex}")
                        log_lines.append(f"- ❌ **{nombre}**: {ex}")
                        fallidos += 1

                print(f"\n{'='*60}")
                print(f"  ✅ Importados : {exitosos}")
                print(f"  ❌ Fallidos   : {fallidos}")
                print(f"{'='*60}")
                print(f"\n🚀 Finalizado. Revisa 'historial_sincronizaciones.md'.")

    except Exception:
        print("\n💥 Error inesperado al conectar con el MCP.")
        print("   Asegúrate de estar autenticado (ejecuta 'python -m notebooklm_mcp.auth_cli').")
        import traceback
        traceback.print_exc()

    finally:
        _guardar_log(log_lines)


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print("⚠️ Necesitas Python 3.10 o superior.")
    asyncio.run(run())
