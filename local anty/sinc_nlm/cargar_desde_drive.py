"""
cargar_desde_drive.py
─────────────────────
Lista archivos en una carpeta de Google Drive (usando las cookies de sesión
del MCP de NotebookLM) y agrega los nuevos como fuentes en NotebookLM.

Uso:
    python cargar_desde_drive.py

Requisitos previos:
    1. Autenticado con:  python -m notebooklm_mcp.auth_cli
    2. IDs configurados en config.py
"""

import asyncio
import sys
import os
import json
import datetime
import hashlib
import hmac
import time
import requests
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ── Configuración centralizada ────────────────────────────────
from config import (
    NOTEBOOK_ID,
    DRIVE_FOLDER_ID,
    EXTENSION_A_DOCTYPE,
    DRIVE_DOC_TYPE_DEFAULT,
)
# ─────────────────────────────────────────────────────────────


# ── Tipos de MIME de Google Drive → doc_type NotebookLM ──────
MIME_A_DOCTYPE: dict[str, str] = {
    "application/vnd.google-apps.document":         "doc",
    "application/vnd.google-apps.presentation":     "slides",
    "application/vnd.google-apps.spreadsheet":      "sheets",
    "application/pdf":                               "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "doc",
    "application/msword":                            "doc",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "slides",
    "application/vnd.ms-powerpoint":                "slides",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "sheets",
    "application/vnd.ms-excel":                     "sheets",
    "text/csv":                                      "sheets",
}

# MIMEs que notebook_add_drive NO soporta (imágenes, audio, video, etc.)
MIME_NO_SOPORTADOS: set[str] = {
    "application/vnd.google-apps.folder",
    "application/vnd.google-apps.shortcut",
    "image/jpeg", "image/png", "image/gif", "image/bmp",
    "image/webp", "image/tiff", "image/heic",
    "video/mp4", "video/avi", "video/quicktime", "video/x-matroska",
    "audio/mpeg", "audio/wav", "audio/x-m4a",
    "text/plain",  # .txt → sube por otro método
}


def doc_type_para_mime(mime_type: str, titulo: str) -> str | None:
    """
    Devuelve el doc_type para notebook_add_drive o None si el archivo
    no puede agregarse por esa vía.
    """
    if mime_type in MIME_NO_SOPORTADOS:
        return None
    if mime_type in MIME_A_DOCTYPE:
        return MIME_A_DOCTYPE[mime_type]
    # Fallback: intentar por extensión del nombre
    _, ext = os.path.splitext(titulo.lower())
    return EXTENSION_A_DOCTYPE.get(ext, None)


def _generar_sapisid_hash(sapisid: str, origin: str = "https://notebooklm.google.com") -> str:
    """Genera el header Authorization: SAPISIDHASH requerido por APIs de Google."""
    ts = str(int(time.time()))
    token = f"{ts} {sapisid} {origin}"
    h = hmac.new(sapisid.encode(), token.encode(), hashlib.sha1).hexdigest()
    return f"SAPISIDHASH {ts}_{h}"


def listar_archivos_en_carpeta(folder_id: str, cookies: dict) -> list[dict]:
    """
    Llama a la Google Drive API v3 para listar los archivos de una carpeta,
    usando las cookies de sesión de Google (sin OAuth adicional).

    Devuelve una lista de dicts con: id, name, mimeType.
    """
    archivos = []
    page_token = None
    sapisid = cookies.get("SAPISID", "")

    headers = {
        "Authorization": _generar_sapisid_hash(sapisid),
        "X-Origin": "https://drive.google.com",
        "X-Referer": "https://drive.google.com",
        "Referer": "https://drive.google.com/",
    }

    session_req = requests.Session()
    # Pasar las cookies de Google al request
    for name, value in cookies.items():
        session_req.cookies.set(name, value, domain=".google.com")

    campos = "files(id,name,mimeType,size),nextPageToken"
    query = f"'{folder_id}' in parents and trashed=false"

    while True:
        params: dict = {
            "q": query,
            "fields": campos,
            "pageSize": 100,
            "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true",
        }
        if page_token:
            params["pageToken"] = page_token

        resp = session_req.get(
            "https://www.googleapis.com/drive/v3/files",
            params=params,
            headers=headers,
            timeout=30,
        )

        if resp.status_code != 200:
            print(f"\n⚠️  Drive API respondió {resp.status_code}: {resp.text[:300]}")
            break

        data = resp.json()
        archivos.extend(data.get("files", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return archivos


async def obtener_fuentes_existentes(session: ClientSession) -> set[str]:
    """Devuelve los document_id de Drive ya vinculados al notebook."""
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
    for f in data.get("syncable_sources", []):
        doc_id = f.get("document_id") or f.get("id", "")
        ids.add(doc_id)
    return ids


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
    print(f"  Cargador de Drive → NotebookLM")
    print(f"  Notebook  : {NOTEBOOK_ID}")
    print(f"  Carpeta   : {DRIVE_FOLDER_ID}")
    print(f"  Inicio    : {timestamp}")
    print("=" * 60)

    log_lines = [
        f"\n---",
        f"# Carga desde Drive ({timestamp})",
        f"- Notebook: `{NOTEBOOK_ID}`",
        f"- Carpeta Drive: `{DRIVE_FOLDER_ID}`",
        "",
    ]

    # ── 1. Cargar cookies de sesión almacenadas por el MCP ────
    try:
        import notebooklm_mcp.auth as nlm_auth
        tokens = nlm_auth.load_cached_tokens()
        if not tokens or not tokens.cookies:
            print("\n❌ No hay tokens en cache. Ejecuta primero:")
            print("   python -m notebooklm_mcp.auth_cli")
            return
        cookies = tokens.cookies if isinstance(tokens.cookies, dict) else {}
        print(f"\n🔑 Cookies de sesión cargadas ({len(cookies)} cookies).")
    except Exception as e:
        print(f"\n❌ No se pudieron cargar las cookies: {e}")
        return

    # ── 2. Listar archivos en la carpeta de Drive ─────────────
    print(f"\n🔍 Listando archivos en carpeta Drive: {DRIVE_FOLDER_ID} ...")
    todos_archivos = listar_archivos_en_carpeta(DRIVE_FOLDER_ID, cookies)

    if not todos_archivos:
        print("\n⚠️  No se encontraron archivos.")
        print("   Posibles causas:")
        print("   • El DRIVE_FOLDER_ID en config.py no es correcto")
        print("   • La sesión expiró → ejecuta: python -m notebooklm_mcp.auth_cli")
        print("   • La carpeta está en 'Shared Drive' (requiere acceso especial)")
        log_lines.append("⚠️ No se encontraron archivos en la carpeta.")
        _guardar_log(log_lines)
        return

    print(f"   → {len(todos_archivos)} archivo(s) encontrado(s) en Drive.")

    # ── 3. Filtrar por tipo soportado ─────────────────────────
    soportados = []
    omitidos = []
    for archivo in todos_archivos:
        mime = archivo.get("mimeType", "")
        nombre = archivo.get("name", "")
        doc_type = doc_type_para_mime(mime, nombre)
        if doc_type:
            soportados.append({**archivo, "doc_type": doc_type})
        else:
            omitidos.append(archivo)

    print(f"   → {len(soportados)} soportados por NotebookLM / {len(omitidos)} omitidos (imágenes, vídeos, etc.)")
    if omitidos:
        print("   Omitidos:")
        for o in omitidos:
            print(f"     🚫 {o.get('name')} ({o.get('mimeType', '?')})")

    if not soportados:
        print("\n✨ Ningún archivo en la carpeta es compatible con notebook_add_drive.")
        log_lines.append("✨ Ningún archivo compatible encontrado.")
        _guardar_log(log_lines)
        return

    # ── 4. Conectar al MCP y filtrar duplicados ───────────────
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

                print("\n📋 Obteniendo fuentes ya vinculadas al notebook...")
                fuentes_existentes = await obtener_fuentes_existentes(session)
                print(f"   → {len(fuentes_existentes)} ya presentes.")

                nuevos = [a for a in soportados if a["id"] not in fuentes_existentes]
                ya_estan = len(soportados) - len(nuevos)

                print(f"\n   {ya_estan} ya estaban vinculados → se omiten.")
                print(f"   {len(nuevos)} archivo(s) nuevo(s) para importar.")

                if not nuevos:
                    print("\n✨ Todos los archivos compatibles ya están en el notebook.")
                    log_lines.append("✨ Todos los archivos ya estaban vinculados.")
                    _guardar_log(log_lines)
                    return

                # ── 5. Agregar cada archivo nuevo ─────────────
                print(f"\n⬆️  Agregando {len(nuevos)} archivo(s) a NotebookLM...\n")
                log_lines.append("## Documentos importados\n")

                exitosos = 0
                fallidos = 0
                for archivo in nuevos:
                    nombre = archivo["name"]
                    doc_id = archivo["id"]
                    doc_type = archivo["doc_type"]
                    mime = archivo.get("mimeType", "")

                    print(f"  ⬆️  {nombre}  [{doc_type}]", end=" ", flush=True)
                    try:
                        resultado = await agregar_fuente(session, doc_id, nombre, doc_type)
                        estado = resultado.get("status", "")
                        if estado in ("success", "added", "ok") or resultado.get("source_id"):
                            print("✅")
                            log_lines.append(f"- ✅ **{nombre}** (`{doc_type}`)")
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
        import traceback
        traceback.print_exc()

    finally:
        _guardar_log(log_lines)


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print("⚠️ Necesitas Python 3.10 o superior.")
    asyncio.run(run())
