"""CLI entrypoints.

Usage:
  python -m world_news            # starts FastAPI app
  python -m world_news.mcp_server # starts MCP server (stdio)
"""

from __future__ import annotations

from .app import main as run_app

if __name__ == "__main__":
    run_app()
