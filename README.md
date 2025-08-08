## World News: MCP + Gemini + GDELT

Modular Python 3.12 codebase that:
- Exposes an MCP server with tools to search GDELT and summarize/analyze via Gemini 2.5 Flash.
- Provides a FastAPI `/chat` endpoint that fetches fresh news and answers user questions grounded in retrieved articles.

### Setup

1) Python 3.12 recommended. Create a virtual environment and install deps:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

2) Create `.env` in repo root:

```
GEMINI_API_KEY=YOUR_KEY
# Optional
GDELT_API_KEY=
```

3) Configure YAML (optional; defaults included): `world_news.yaml`

```
gemini:
  model: gemini-2.5-flash
gdelt:
  endpoint: null
```

### Run the HTTP API

```bash
python -m world_news.app
# -> http://127.0.0.1:8000/docs for Swagger UI
```

Example request (minimal input):

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'content-type: application/json' \
  -d '{"query": "What is the latest on climate policy in the EU?"}'
```

### Run the MCP Server (stdio)

```bash
python -m world_news.mcp_server
```

Tools available:
- `gdelt_search(query, start_date?, end_date?, max_records?, languages?) -> List[Article]`
- `summarize_articles(articles, max_words?) -> str`
- `answer_question(question, articles) -> str`

The server communicates over stdio using the MCP protocol and can be attached by MCP-capable clients.

### Project Structure

```
src/world_news/
  app.py            # FastAPI app exposing /chat
  mcp_server.py     # MCP server exposing tools over stdio
  service.py        # Orchestration of clients + prompts
  clients/          # External service clients
    gemini.py       # Gemini wrapper
    gdelt.py        # GDELT Doc API wrapper
    __init__.py
  config/           # Configuration system
    __init__.py
    schemas.py      # Dataclasses for YAML config
    manager.py      # YAML loader + search
    settings.py     # Env + typed settings
  prompt_library.py # Centralized prompt templates (dataclass)
configs/
  world_news.yaml   # Default YAML config
```

### Notes

- GDELT Doc API often needs no API key; field is optional.
- Ensure billing/enabling access for Gemini 2.5 Flash in your Google account.


