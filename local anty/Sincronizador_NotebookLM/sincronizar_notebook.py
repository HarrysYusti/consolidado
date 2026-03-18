import asyncio
import sys
import json
import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ==========================================
# CONFIGURACIÓN PRINCIPAL DEL USUARIO
# ==========================================
# Inserta aquí el ID de la libreta (Notebook) que deseas actualizar.
# 
# ¿Cómo obtener el ID?
# 1. Ve a https://notebooklm.google.com/ y abre tu libreta.
# 2. Revisa la URL en la barra de direcciones de tu navegador.
#    Ejemplo: https://notebooklm.google.com/notebook/9ad1d67b-d2f8-45a4-b034-639b08111ad8
# 3. El ID es únicamente la secuencia alfanumérica del final.
NOTEBOOK_ID = "9ad1d67b-d2f8-45a4-b034-639b08111ad8"
# ==========================================

async def run():
    print(f"Iniciando conexión con el MCP de NotebookLM para el Notebook: {NOTEBOOK_ID}...")

    # Parámetros para iniciar el servidor MCP local en modo STDIO
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "notebooklm_mcp.server"],
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("\n✅ Conexión establecida con éxito al servidor MCP.")
                print("Consultando el estado de los documentos vinculados (Google Drive) dentro de la libreta...")
                
                # 1. Pedirle a NotebookLM que revise si los archivos de Drive han cambiado
                result = await session.call_tool(
                    "source_list_drive",
                    arguments={"notebook_id": NOTEBOOK_ID}
                )
                
                # Extraemos el JSON devuelto por MCP
                data = result.content[0].text
                try:
                    response = json.loads(data)
                except:
                    response = data

                if response.get("status") != "success":
                    print(f"\n❌ Error al listar los orígenes: {response.get('error')}")
                    print("Por favor verifica que el NOTEBOOK_ID existe y que estás autenticado en Google.")
                    return

                # Filtramos sólo los que dicen "needs_sync" = True
                syncable_sources = response.get("syncable_sources", [])
                stale_sources = [s for s in syncable_sources if s.get("needs_sync")]
                
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"🔍 Revisió completa: Se encontraron {len(stale_sources)} documentos desactualizados.")
                
                # Vamos guardando un log en Markdown
                report_lines = [
                    f"\n---", 
                    f"# Registro de Sincronización ({timestamp})", 
                    f"## Estado Inicial de Documentos (ID Notebook: {NOTEBOOK_ID})", 
                    ""
                ]
                
                ids_to_sync = []
                if not stale_sources:
                    mensaje = "✨ Todo al día. Las fuentes de la libreta coinciden exactamente con sus versiones en Google Drive."
                    print(mensaje)
                    report_lines.append(mensaje)
                else:
                    print("\nDocumentos en cola para actualizarse en NotebookLM:")
                    for src in stale_sources:
                        print(f" - {src.get('title')}")
                        report_lines.append(f"- **{src.get('title')}** (ID interno: `{src.get('id')}`)")
                        ids_to_sync.append(src.get("id"))

                with open("historial_sincronizaciones.md", "a", encoding="utf-8") as f:
                    f.write("\n".join(report_lines) + "\n")
                
                # 2. Ejecutar la sincronización real en NotebookLM
                if ids_to_sync:
                    print(f"\n⏳ Ejecutando sincronización de {len(ids_to_sync)} documentos en NotebookLM...")
                    print("Esto puede tardar dependiendo del volumen de texto de cada documento de Google Drive.")
                    
                    sync_result = await session.call_tool(
                        "source_sync_drive",
                        arguments={"source_ids": ids_to_sync, "confirm": True}
                    )
                    
                    sync_data_str = sync_result.content[0].text
                    sync_response = json.loads(sync_data_str)
                    
                    with open("historial_sincronizaciones.md", "a", encoding="utf-8") as f:
                        f.write("\n### Resultados de la Operación\n")
                        
                        if sync_response.get("status") in ["success", "partial"]:
                            results = sync_response.get("results", [])
                            for res in results:
                                status_icon = "✅" if res.get("status") == "synced" else "❌"
                                line = f"- {status_icon} **{res.get('title', 'Unknown')}**: {res.get('status')}"
                                print(line)
                                f.write(line + "\n")
                                if res.get("error"):
                                    err_msg = f"  - Error Devuelto: {res.get('error')}"
                                    print(err_msg)
                                    f.write(err_msg + "\n")
                        else:
                            error_msg = f"\nError general crítico durante sincronización: {sync_response.get('error')}"
                            print(error_msg)
                            f.write(error_msg + "\n")
                            
                    print(f"\n🚀 Sincronización finalizada. Revisa 'historial_sincronizaciones.md' para más detalles.")

    except Exception as e:
        print("\n💥 Ocurrió un error inesperado al conectar o comunicarse con el MCP.")
        print("Asegúrate de tener instalada la librería y de estar ya autenticado usando login.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print("⚠️ Advertencia: Necesitas Python 3.10 o superior para ejecutar async con MCP.")
        
    asyncio.run(run())
