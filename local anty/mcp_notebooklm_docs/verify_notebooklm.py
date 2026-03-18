import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "notebooklm_mcp.server"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        print("Connected to server process")
        async with ClientSession(read, write) as session:
            print("Initializing session...")
            await session.initialize()
            print("Session initialized. Listing resources...")
            resources = await session.list_resources()
            print("Notebooks found:")
            for resource in resources.resources:
                print(f"- {resource.name} ({resource.uri})")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as e:
        import traceback
        traceback.print_exc()
