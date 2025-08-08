"""End-to-end pipeline orchestrating two LLM steps and MCP tool use semantics.

Stages:
1) Planning LLM: reads the user's question and produces a cleaned GDELT query and optional params.
2) Retrieval via GDELT client (or MCP tool): fetch articles.
3) Summarizer LLM: summarizes the fetched articles based on the user question.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .clients import GDELTClient, GeminiClient
from .prompt_library import get_prompts


@dataclass(frozen=True)
class PlanResult:
    query: str
    start_date: str | None
    end_date: str | None
    languages: list[str] | None
    max_records: int


def plan_gdelt_search(planner_llm: GeminiClient, user_question: str) -> PlanResult:
    prompts = get_prompts()
    prompt = prompts.plan_gdelt + "\n\nUSER QUESTION:\n" + user_question + "\n"
    raw = planner_llm.model.generate_content(prompt).text or "{}"
    try:
        data = json.loads(raw)
    except Exception:
        data = {}

    query = data.get("query") if isinstance(data, dict) else None
    if not isinstance(query, str) or not query.strip():
        # Fallback: use the user question best-effort
        query = user_question.strip()

    start_date = data.get("start_date") if isinstance(data, dict) else None
    end_date = data.get("end_date") if isinstance(data, dict) else None
    languages = data.get("languages") if isinstance(data, dict) else None
    if not isinstance(languages, list):
        languages = None
    max_records = data.get("max_records") if isinstance(data, dict) else None
    if not isinstance(max_records, int):
        max_records = 20

    return PlanResult(
        query=query,
        start_date=start_date or None,
        end_date=end_date or None,
        languages=languages or None,
        max_records=max_records,
    )


def run_pipeline(
    user_question: str,
    planner_llm: GeminiClient,
    retriever: GDELTClient,
    summarizer_llm: GeminiClient,
) -> str:
    """Run the 2-step LLM + retrieval pipeline and return a summary.

    Args:
        user_question: The user's natural-language question.
        planner_llm: LLM used to plan GDELT search parameters.
        retriever: Client for GDELT.
        summarizer_llm: LLM used to summarize the retrieved articles.

    Returns:
        str: Final summary text.
    """

    plan = plan_gdelt_search(planner_llm, user_question)
    articles = retriever.search_articles(
        query=plan.query,
        start_date=plan.start_date,
        end_date=plan.end_date,
        max_records=plan.max_records,
        languages=plan.languages,
    )
    if not articles:
        return "No relevant articles found."

    passages: list[str] = []
    for a in articles:
        title = a.get("title") or ""
        url = a.get("url") or ""
        snippet = a.get("snippet") or ""
        passages.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}")
    combined = "\n\n".join(passages)
    return summarizer_llm.summarize(combined, max_words=200)
