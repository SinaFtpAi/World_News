## World News pipeline (simple overview)

### Inputs and configuration
- `.env`: secrets
  - `GEMINI_API_KEY` (required)
  - `GDELT_API_KEY` (optional)
- `configs/world_news.yaml`: static config
  - `gemini.model` (e.g., `gemini-2.5-flash`)

### Building blocks
- `world_news/config`:
  - `settings.get_settings()` reads `.env` + YAML and returns typed `Settings`.
- `world_news/clients`:
  - `gdelt.GDELTClient.search_articles(...)` fetches articles from GDELT Doc API.
  - `gemini.GeminiClient` calls Gemini for summarization and Q&A.
- `world_news/prompt_library.py`: centralized prompt templates (dataclass).
- `world_news/service.py`: orchestration (`NewsService`).

### HTTP /chat endpoint flow
File: `world_news/app.py`
1) Load settings via `get_settings()` (model name from YAML, API keys from `.env`).
2) Build `NewsService` with `GeminiClient` and `GDELTClient`.
3) Receive `POST /chat` with `query` (and optional dates/languages).
4) `NewsService.search(...)` queries GDELT for relevant articles.
5) `NewsService.answer_question(...)`:
   - Formats short passages (title/url/snippet)
   - Uses Gemini with the QA prompt to answer grounded in those passages
6) Return `{ answer, num_articles }` to the caller.

### MCP server tools flow
File: `world_news/mcp_server.py`
- `gdelt_search(...)` → `NewsService.search(...)` → returns article list
- `summarize_articles(articles, ...)` → `GeminiClient.summarize(...)`
- `answer_question(question, articles)` → `GeminiClient.answer_based_on_context(...)`

This allows MCP-capable LLMs/clients to:
1) Call `gdelt_search` to fetch fresh context
2) Optionally call `summarize_articles` to condense
3) Call `answer_question` for grounded responses

### Data shape used across steps
`Article` (subset of GDELT fields):
- `title`, `url`, `snippet`, `language?`, `sourcecountry?`, `domain?`, `seendate?`, `socialimage?`, `isduplicate?`, `sourceurl?`

### Error handling (essentials)
- If no articles are found, `/chat` returns 404.
- Model/API failures bubble as standard HTTP errors (FastAPI) or MCP errors (tools).

### Where to adjust behavior
- Model choice: `configs/world_news.yaml` → `gemini.model`.
- Query shaping: `world_news/clients/gdelt.py` (`Filters` construction).
- Prompts: `world_news/prompt_library.py`.
- Orchestration: `world_news/service.py`.


