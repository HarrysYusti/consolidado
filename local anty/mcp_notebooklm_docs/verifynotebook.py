import asyncio
import sys
import os

# Add user site-packages to sys.path just in case
sys.path.append(os.path.expandvars(r"C:\Users\harry\AppData\Roaming\Python\Python313\site-packages"))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    print("Starting verification script...")
    
    # Path to the executable
    executable = r"C:\Users\harry\AppData\Roaming\Python\Python313\Scripts\notebooklm-mcp.exe"
    config_path = r"C:\Users\harry\.gemini\antigravity\notebooklm-config.json"
    
    print(f"Using executable: {executable}")
    print(f"Using config: {config_path}")

    server_params = StdioServerParameters(
        command=executable,
        args=["--config", config_path, "server"],
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            print("Connected to server process. Waiting for initialization...")
            async with ClientSession(read, write) as session:
                print("Initializing session...")
                await session.initialize()
                print("Session initialized. Listing resources...")
                resources = await session.list_resources()
                print("Notebooks found:")
                for resource in resources.resources:
                    print(f"- {resource.name} ({resource.uri})")
    except Exception as e:
        print(f"\nCaught exception during execution:")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except Exception as e:
        print(f"Top level error: {e}")
