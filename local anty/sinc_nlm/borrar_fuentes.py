"""
borrar_fuentes.py
─────────────────
Este script elimina masivamente de NotebookLM TODAS las fuentes (documentos) 
vinculadas al notebook configurado en config.py, dejándolo 100% limpio.

Uso:
    python borrar_fuentes.py
"""

import asyncio
import sys
import json
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Usa el config centralizado
from config import NOTEBOOK_ID

async def run():
    print("=" * 60)
    print(f"  Borrador Masivo de Fuentes → NotebookLM")
    print(f"  Notebook         : {NOTEBOOK_ID}")
    print("=" * 60)

    # Confirmación del usuario
    respuesta = input("\n⚠️  ¿ESTÁS SEGURO QUE QUIERES BORRAR TODAS LAS FUENTES DEL NOTEBOOK? (s/n): ")
    if respuesta.lower() != "s":
        print("Operación cancelada.")
        return

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "notebooklm_mcp.server"],
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("\n✅ Conexión MCP establecida.\n")

                print("📋 Extrayendo de la API todos los rastros de fuentes en el Notebook...")
                
                posibles_source_ids = set()
                
                # 1. Sacamos las fuentes vistas como de Google Drive
                try:
                    res_drive = await session.call_tool("source_list_drive", arguments={"notebook_id": NOTEBOOK_ID})
                    data_drive = json.loads(res_drive.content[0].text)
                    for f in data_drive.get("syncable_sources", []):
                        if f.get("id"):
                            posibles_source_ids.add(f["id"])
                except Exception:
                    pass

                # 2. Extracción recursiva de TODOS los UUIDs dentro del Notebook crudo para cazar PDFs
                try:
                    res_nb = await session.call_tool("notebook_get", arguments={"notebook_id": NOTEBOOK_ID})
                    data_nb = json.loads(res_nb.content[0].text)
                    
                    # Buscamos cuerdas que parezcan un UUID de 36 caracteres típico de NotebookLM
                    uuid_regex = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
                    
                    def extraer_uuids(obj):
                        if isinstance(obj, str) and uuid_regex.match(obj):
                            posibles_source_ids.add(obj)
                        elif isinstance(obj, list):
                            for item in obj: extraer_uuids(item)
                        elif isinstance(obj, dict):
                            for val in obj.values(): extraer_uuids(val)
                            
                    if "notebook" in data_nb:
                        extraer_uuids(data_nb["notebook"])
                except Exception:
                    pass
                
                # Para evitar borrar el propio notebook
                if NOTEBOOK_ID in posibles_source_ids:
                    posibles_source_ids.remove(NOTEBOOK_ID)

                if not posibles_source_ids:
                    print("✨ El NotebookLM responde que ya está vacío. (No hay documentos).")
                    return

                print(f"\n⚠️  Se detectaron {len(posibles_source_ids)} elementos que parecen ser fuentes.")
                print("Iniciando eliminación destructiva...")
                print("-" * 60)
                
                borrados = 0
                for source_id in list(posibles_source_ids):
                    try:
                        res_del = await session.call_tool(
                            "source_delete", 
                            arguments={"source_id": source_id, "confirm": True}
                        )
                        msg = res_del.content[0].text.lower()
                        # Si devuelve {"status": "success", "deleted": true}
                        if "true" in msg or "success" in msg or "deleted" in msg:
                            print(f"🗑️  ID Eliminado: {source_id[:8]}...")
                            borrados += 1
                        else:
                            # Era otro tipo de ID en el sistema que no es una fuente borrable
                            pass
                    except Exception:
                        pass
                
                print("-" * 60)
                print(f"✅ ¡Proceso finalizado! Documentos borrados con éxito: {borrados}")
                print("Nota: Si borraste {0}, intenta refrescar la web, ya es un lienzo en blanco.")

    except Exception as e:
        print(f"💥 Error inesperado al conectar: {e}")

if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print("⚠️ Necesitas Python 3.10 o superior.")
    asyncio.run(run())
