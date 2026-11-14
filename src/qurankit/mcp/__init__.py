"""MCP (Model Context Protocol) interface for QuranKit.

Provides a read-only MCP server exposing core research tools
for AI agents and other MCP clients.
"""

from __future__ import annotations

from qurankit.mcp.server import create_server, run_server

__all__ = ["create_server", "run_server"]
