"""
sincronizar_notebook.py
────────────────────────
Revisa las fuentes de Google Drive ya vinculadas al Notebook de NotebookLM
y actualiza las que estén desactualizadas ("needs_sync").

El Notebook de destino se configura en config.py (NOTEBOOK_ID).

Uso:
    python sincronizar_notebook.py
"""

import asyncio
import sys
import json
import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ── Configuración centralizada ────────────────────────────────
from config import NOTEBOOK_ID
# ─────────────────────────────────────────────────────────────


async def run():
    print(f"Iniciando sincronización del Notebook: {NOTEBOOK_ID} ...")

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "notebooklm_mcp.server"],
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("\n✅ Conexión establecida con el servidor MCP.")
                print("Consultando documentos vinculados (Google Drive) en la libreta...")

                # 1. Listar fuentes y detectar cuáles necesitan sincronización
                result = await session.call_tool(
                    "source_list_drive",
                    arguments={"notebook_id": NOTEBOOK_ID}
                )

                data = result.content[0].text
                try:
                    response = json.loads(data)
                except json.JSONDecodeError:
                    response = data

                if response.get("status") != "success":
                    print(f"\n❌ Error al listar los orígenes: {response.get('error')}")
                    print("Verifica que NOTEBOOK_ID en config.py es correcto y estás autenticado.")
                    return

                syncable_sources = response.get("syncable_sources", [])
                stale_sources = [s for s in syncable_sources if s.get("needs_sync")]

                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"🔍 Revisión completa: {len(stale_sources)} documento(s) desactualizado(s).")

                # Bitácora Markdown
                report_lines = [
                    f"\n---",
                    f"# Registro de Sincronización ({timestamp})",
                    f"## Estado Inicial de Documentos (Notebook: `{NOTEBOOK_ID}`)",
                    "",
                ]

                ids_to_sync = []
                if not stale_sources:
                    mensaje = "✨ Todo al día. Las fuentes coinciden exactamente con Google Drive."
                    print(mensaje)
                    report_lines.append(mensaje)
                else:
                    print("\nDocumentos en cola para actualizarse:")
                    for src in stale_sources:
                        print(f"  - {src.get('title')}")
                        report_lines.append(f"- **{src.get('title')}** (ID: `{src.get('id')}`)")
                        ids_to_sync.append(src.get("id"))

                with open("historial_sincronizaciones.md", "a", encoding="utf-8") as f:
                    f.write("\n".join(report_lines) + "\n")

                # 2. Ejecutar sincronización
                if ids_to_sync:
                    print(f"\n⏳ Sincronizando {len(ids_to_sync)} documento(s)...")
                    print("Esto puede tardar según el volumen de texto en Google Drive.")

                    sync_result = await session.call_tool(
                        "source_sync_drive",
                        arguments={"source_ids": ids_to_sync, "confirm": True}
                    )

                    sync_response = json.loads(sync_result.content[0].text)

                    with open("historial_sincronizaciones.md", "a", encoding="utf-8") as f:
                        f.write("\n### Resultados de la Operación\n")

                        if sync_response.get("status") in ["success", "partial"]:
                            for res in sync_response.get("results", []):
                                icon = "✅" if res.get("status") == "synced" else "❌"
                                line = f"- {icon} **{res.get('title', 'Unknown')}**: {res.get('status')}"
                                print(line)
                                f.write(line + "\n")
                                if res.get("error"):
                                    err = f"  - Error: {res.get('error')}"
                                    print(err)
                                    f.write(err + "\n")
                        else:
                            error_msg = f"\n❌ Error crítico: {sync_response.get('error')}"
                            print(error_msg)
                            f.write(error_msg + "\n")

                    print(f"\n🚀 Sincronización finalizada. Revisa 'historial_sincronizaciones.md'.")

    except Exception:
        print("\n💥 Error inesperado al conectar con el MCP.")
        print("   Asegúrate de estar autenticado (ejecuta 'notebooklm-mcp-auth' una vez).")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print("⚠️ Advertencia: Necesitas Python 3.10 o superior.")
    asyncio.run(run())
