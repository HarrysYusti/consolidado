import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def save_debug():
    server_params = StdioServerParameters(command="python", args=["-m", "notebooklm_mcp.server"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            notebook_id = "8415491e-0767-4276-a934-d4f8f7ce8f80"
            
            print("Fetching source_list_drive...")
            res1 = await session.call_tool("source_list_drive", arguments={"notebook_id": notebook_id})
            with open("debug_drive.json", "w", encoding="utf-8") as f:
                f.write(res1.content[0].text)
            
            print("Fetching notebook_get...")
            res2 = await session.call_tool("notebook_get", arguments={"notebook_id": notebook_id})
            with open("debug_nb.json", "w", encoding="utf-8") as f:
                f.write(res2.content[0].text)
            print("Done.")

if __name__ == "__main__":
    asyncio.run(save_debug())
