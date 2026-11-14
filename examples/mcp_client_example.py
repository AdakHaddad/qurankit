"""Example MCP client for QuranKit.

This shows how an AI agent would use the QuranKit MCP tools.
Run the MCP server first: `qurankit-mcp`
Then connect with an MCP client.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Connect to QuranKit MCP server and call tools."""
    # Server parameters - runs the qurankit-mcp command
    server_params = StdioServerParameters(
        command="qurankit-mcp",
        args=[],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Search for text
            print("\n=== Search for 'بِسْمِ' ===")
            result = await session.call_tool("search_quran", {
                "query": "بِسْمِ",
                "edition": "tanzil-uthmani-v1",
                "mode": "diacritic-insensitive",
                "limit": 5
            })
            print(result.content[0].text)

            # Get ayah
            print("\n=== Get Ayah 2:255 (Ayah al-Kursi) ===")
            result = await session.call_tool("get_ayah", {
                "reference": "2:255",
                "edition": "tanzil-uthmani-v1"
            })
            print(result.content[0].text)

            # Get surah
            print("\n=== Get Surah 1 ===")
            result = await session.call_tool("get_surah", {
                "surah_number": 1
            })
            print(result.content[0].text)

            # List all surahs
            print("\n=== List All Surahs ===")
            result = await session.call_tool("list_surahs", {})
            # Just print first 5
            import json
            surahs = json.loads(result.content[0].text)
            for s in surahs[:5]:
                print(f"  {s['surah_number']}: {s['name_arabic']} ({s['ayah_count']} ayahs)")

            # Find mutashabihat
            print("\n=== Find Mutashabihat for 1:1 ===")
            result = await session.call_tool("find_mutashabihat", {
                "reference": "1:1",
                "edition": "tanzil-uthmani-v1",
                "min_length": 2
            })
            print(result.content[0].text[:500] + "...")

            # Normalize text
            print("\n=== Normalize Text ===")
            result = await session.call_tool("normalize_text", {
                "text": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                "profile": "diacritics-insensitive-v1"
            })
            print(result.content[0].text)

            # List normalization profiles
            print("\n=== Normalization Profiles ===")
            result = await session.call_tool("list_normalization_profiles", {})
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
