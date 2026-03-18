import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Notebook ID for "Coordinacion TD"
NOTEBOOK_ID = "9ad1d67b-d2f8-45a4-b034-639b08111ad8"

async def run():
    # Server parameters - utilizing the same configuration as verified previously
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "notebooklm_mcp.server"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print(f"Listing sources for notebook {NOTEBOOK_ID}...")
            
            # Call source_list_drive tool
            result = await session.call_tool(
                "source_list_drive",
                arguments={"notebook_id": NOTEBOOK_ID}
            )
            
            data = result.content[0].text
            # The tool returns JSON string in content, we likely need to parse it if it wasn't already a dict
            # However, the SDK might return it as a dict/object if the tool definition specifies it.
            # Let's inspect what we receive. The mcp SDK usually returns CallToolResult.
            
            import json
            try:
                # If the server implementation returns a dict, mcp might preserve it, or it might be in the text field.
                # Based on standard MCP, the content is a list of TextContent or ImageContent.
                # 'data' here is likely the JSON string if the tool returns a JSON object.
                response = json.loads(data)
            except:
                # If it's already a dict (unlikely for text content but possible in some implementations)
                response = data

            if response.get("status") != "success":
                print(f"Error listing sources: {response.get('error')}")
                return

            syncable_sources = response.get("syncable_sources", [])
            stale_sources = [s for s in syncable_sources if s.get("needs_sync")]
            
            print(f"Found {len(stale_sources)} stale sources.")
            
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Generate Report MD
            report_lines = [f"\n---\n# Re-verificación ({timestamp})", "", "## Documentos Desactualizados (Pendientes de Sincronización)", ""]
            
            ids_to_sync = []
            if not stale_sources:
                 report_lines.append("✅ Todo sincronizado. No se encontraron documentos pendientes.")
            else:
                for src in stale_sources:
                    report_lines.append(f"- **{src.get('title')}** (ID: `{src.get('id')}`)")
                    ids_to_sync.append(src.get("id"))

            # Append to Report
            with open("stale_sources_report.md", "a", encoding="utf-8") as f:
                f.write("\n".join(report_lines))
            
            # Sync if needed
            if ids_to_sync:
                print(f"Syncing {len(ids_to_sync)} sources...")
                sync_result = await session.call_tool(
                    "source_sync_drive",
                    arguments={"source_ids": ids_to_sync, "confirm": True}
                )
                
                sync_data_str = sync_result.content[0].text
                sync_response = json.loads(sync_data_str)
                
                with open("stale_sources_report.md", "a", encoding="utf-8") as f:
                    f.write("\n\n## Resultado de Sincronización\n")
                    
                    if sync_response.get("status") == "success" or sync_response.get("status") == "partial":
                        results = sync_response.get("results", [])
                        for res in results:
                            status_icon = "✅" if res.get("status") == "synced" else "❌"
                            f.write(f"- {status_icon} **{res.get('title', 'Unknown')}**: {res.get('status')}\n")
                            if res.get("error"):
                                f.write(f"  - Error: {res.get('error')}\n")
                    else:
                        f.write(f"\nError general en sincronización: {sync_response.get('error')}")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as e:
        import traceback
        traceback.print_exc()
