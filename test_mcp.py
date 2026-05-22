import asyncio
from mcp_server import mcp

async def test():
    tools = await mcp.list_tools()
    print(f"Found {len(tools)} tools")
    for t in tools:
        print(f"  - {t.name}: {t.description[:50]}...")

    # Try calling get_students
    result = await mcp.call_tool("get_students", {})
    print(f"\nResult type: {type(result)}")
    print(f"Result: {result}")

asyncio.run(test())
