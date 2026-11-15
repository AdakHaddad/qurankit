# MCP Client Example

QuranKit includes an MCP (Model Context Protocol) server that exposes read-only research tools for AI agents.

## Starting the MCP Server

```bash
# Install with MCP extra
pip install "qurankit-core[mcp]"

# Run server
qurankit-mcp
```

The server runs on stdio by default. For HTTP transport:

```bash
qurankit-mcp --transport http --host 127.0.0.1 --port 8000
```

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `get_surah` | Get surah metadata and ayahs |
| `get_ayah` | Get specific ayah with text and metadata |
| `search_text` | Search Qur'anic text with normalization |
| `get_word_tokens` | Get word tokens for an ayah |
| `lookup_root` | Look up Qur'anic occurrences by Arabic root |
| `lookup_lemma` | Look up occurrences by lemma |
| `lookup_surface` | Look up exact surface form occurrences |
| `get_vocabulary_stats` | Get frequency/distribution stats for root/lemma |
| `get_concordance` | Get KWIC concordance lines |
| `find_mutashabihat` | Find repeated phrases and textual relationships |
| `get_comparison_report` | Generate detailed comparison report |
| `get_corpus_statistics` | Get corpus-wide statistics |

## Python MCP Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Connect to QuranKit MCP server
    server_params = StdioServerParameters(
        command="qurankit-mcp",
        args=[]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"{tool.name}: {tool.description}")
            
            # Call a tool
            result = await session.call_tool(
                "get_surah",
                {"surah_number": 1}
            )
            print(result.content[0].text)
            
            # Search
            result = await session.call_tool(
                "search_text",
                {"query": "بسم الله", "mode": "broad", "limit": 10}
            )
            print(result.content[0].text)
            
            # Root lookup
            result = await session.call_tool(
                "lookup_root",
                {"root_form": "ر ح م", "limit": 20}
            )
            print(result.content[0].text)

asyncio.run(main())
```

## Example: AI Agent Research Workflow

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def research_workflow():
    server_params = StdioServerParameters(command="qurankit-mcp")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. Get surah overview
            surah = await session.call_tool("get_surah", {"surah_number": 1})
            print("=== Surah Al-Fatihah ===")
            print(surah.content[0].text)
            
            # 2. Search for key phrase
            search = await session.call_tool(
                "search_text",
                {"query": "الرحمن الرحيم", "mode": "broad", "limit": 20}
            )
            print("\n=== Search: الرحمن الرحيم ===")
            print(search.content[0].text)
            
            # 3. Root analysis
            root = await session.call_tool(
                "lookup_root",
                {"root_form": "ر ح م", "limit": 30}
            )
            print("\n=== Root: ر ح م ===")
            print(root.content[0].text)
            
            # 4. Vocabulary statistics
            stats = await session.call_tool(
                "get_vocabulary_stats",
                {"root_form": "ر ح م"}
            )
            print("\n=== Statistics ===")
            print(stats.content[0].text)
            
            # 5. Concordance
            concord = await session.call_tool(
                "get_concordance",
                {"root_form": "ر ح م", "context": 2}
            )
            print("\n=== Concordance ===")
            print(concord.content[0].text)
            
            # 6. Mutashabihat analysis
            mutashabihat = await session.call_tool(
                "find_mutashabihat",
                {"reference": "2:255", "analysis_type": "openings", "max_distance": 2}
            )
            print("\n=== Similar to Ayat al-Kursi ===")
            print(mutashabihat.content[0].text)
            
            # 7. Full comparison report
            report = await session.call_tool(
                "get_comparison_report",
                {"reference": "2:255", "include_mutashabihat": True}
            )
            print("\n=== Comparison Report ===")
            print(report.content[0].text[:2000] + "...")

asyncio.run(research_workflow())
```

## Tool Parameters Reference

### get_surah
```json
{
  "surah_number": 1
}
```

### get_ayah
```json
{
  "surah_number": 1,
  "ayah_number": 1
}
```

### search_text
```json
{
  "query": "بسم الله",
  "mode": "broad",
  "limit": 50,
  "surah": null
}
```

### get_word_tokens
```json
{
  "surah_number": 1,
  "ayah_number": 1
}
```

### lookup_root
```json
{
  "root_form": "ر ح م",
  "limit": 100,
  "surah": null
}
```

### lookup_lemma
```json
{
  "lemma_form": "رَحْمَان",
  "limit": 100
}
```

### lookup_surface
```json
{
  "surface_form": "الرَّحْمَٰنِ",
  "limit": 100
}
```

### get_vocabulary_stats
```json
{
  "root_form": "ر ح م"
}
```

### get_concordance
```json
{
  "root_form": "ر ح م",
  "context": 2,
  "limit": 50
}
```

### find_mutashabihat
```json
{
  "reference": "2:255",
  "analysis_type": "openings",
  "max_distance": 2,
  "min_length": 2
}
```

Analysis types: `phrases`, `openings`, `endings`, `recurring`, `shared_roots`, `shared_lemmas`, `word_order`

### get_comparison_report
```json
{
  "reference": "2:255",
  "include_mutashabihat": true,
  "include_shared_roots": true,
  "include_shared_lemmas": true,
  "include_near_duplicates": true
}
```

### get_corpus_statistics
```json
{}
```

## Error Handling

```python
async def safe_call(session, tool_name, params):
    try:
        result = await session.call_tool(tool_name, params)
        return result.content[0].text
    except Exception as e:
        return f"Error calling {tool_name}: {e}"

# Usage
result = await safe_call(session, "get_ayah", {"surah_number": 999, "ayah_number": 1})
print(result)  # Error: Invalid surah number
```

## Configuration

The MCP server uses the same configuration as the Python library:

```bash
# Custom data directory
export QURANKIT_DATA_DIR=/path/to/data
qurankit-mcp

# Or in Python before starting server
from qurankit import QuranKitConfig
config = QuranKitConfig(data_dir="/path/to/data")
# Server will use this config
```
