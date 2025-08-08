"""Centralized prompt templates stored in a dataclass.

This keeps prompts separate from the code that uses them and avoids
embedding large strings inline in business logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent


@dataclass(frozen=True)
class PromptTemplates:
    """Container for prompt templates with simple placeholder syntax.

    Placeholders use double curly braces, e.g., ``{{name}}``.
    """

    summarize: str
    qa: str
    tool_guidance: str
    plan_gdelt: str


def get_prompts() -> PromptTemplates:
    """Return the default set of prompts used by the application.

    Returns:
        PromptTemplates: Immutable prompt templates.
    """

    summarize = dedent(
        """
        You are a concise news assistant.
        Summarize the following text in up to {{max_words}} words.
        Preserve key facts, numbers, and attributions. Avoid speculation.

        CONTENT START
        {{text}}
        CONTENT END
        """
    ).strip()

    qa = dedent(
        """
        You are a news analyst.
        Answer the user's question using ONLY the context below.
        When available, cite URLs or sources explicitly.
        If the answer is not contained in the context, say you don't know.

        CONTEXT START
        {{context}}
        CONTEXT END

        QUESTION: {{question}}
        """
    ).strip()

    tool_guidance = dedent(
        """
        You can call MCP tools to fetch and analyze news. Follow these rules:
        - Use `gdelt_search(query, start_date?, end_date?, max_records?, languages?)`.
        - Infer parameters from the user's query.
          - If a time window is mentioned, set start/end accordingly (YYYY-MM-DD).
          - If not mentioned, default to a recent window (e.g., last 48h).
          - If languages are mentioned, include them; otherwise omit.
          - Set max_records conservatively (e.g., 20) unless the user requests more.
        - After fetching, summarize via `summarize_articles` if many results.
        - Answer with `answer_question(question, articles)` grounded in fetched articles.
        - Prefer fewer, high-quality results over broad noisy sets.
        - If insufficient context, fetch again with refined parameters.
        """
    ).strip()

    plan_gdelt = dedent(
        """
        You will plan a GDELT Doc API search. Read the user's query and 
        output ONLY JSON with keys:
        - query (a cleaned boolean/news search string)
        - start_date (YYYY-MM-DD or null)
        - end_date (YYYY-MM-DD or null)
        - languages (array of ISO codes or null)
        - max_records (integer)
        Rules: 
        - infer dates if mentioned; otherwise keep them null or use a recent default if required.
        - prefer precise boolean operators, quoted phrases, and key entities in `query`. 
        - do not copy the user text verbatim.
        - keep `max_records` small (e.g., 20) unless the user asks for more.
        """
    ).strip()

    return PromptTemplates(
        summarize=summarize,
        qa=qa,
        tool_guidance=tool_guidance,
        plan_gdelt=plan_gdelt,
    )
