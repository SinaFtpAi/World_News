"""MCP server exposing GDELT + Gemini tools over stdio.

This server provides tools that allow an MCP-enabled client/LLM to:
 - Search GDELT for news articles
 - Summarize retrieved articles
 - Answer questions grounded in the fetched articles

Run via: `python -m world_news.mcp_server`
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .clients import Article
from .config import get_settings
from .service import NewsService


def build_service() -> NewsService:
    """Construct and return a `NewsService` using environment configuration."""

    settings = get_settings()
    return NewsService.create_default(
        gemini_api_key=settings.gemini_api_key, gemini_model=settings.gemini_model
    )


mcp = FastMCP(name="gdelt-gemini")
service: NewsService | None = None


@mcp.tool()
def gdelt_search(
    query: str,
    start_date: str | None = None,
    end_date: str | None = None,
    max_records: int = 20,
    languages: list[str] | None = None,
) -> list[Article]:
    """Search news articles using the GDELT Doc API.

    Args:
        query: Keywords or boolean query.
        start_date: Optional start date YYYY-MM-DD.
        end_date: Optional end date YYYY-MM-DD.
        max_records: Maximum number of articles to return.
        languages: Optional list of language codes.

    Returns:
        List[Article]: A list of article records.
    """

    global service
    if service is None:
        service = build_service()
    return service.search(
        query=query,
        start_date=start_date,
        end_date=end_date,
        max_records=max_records,
        languages=languages or None,
    )


@mcp.tool()
def summarize_articles(articles: list[Article], max_words: int = 200) -> str:
    """Summarize a collection of articles into a concise digest.

    Args:
        articles: Article records to summarize.
        max_words: Soft cap for summary length.

    Returns:
        str: Digest summary.
    """

    global service
    if service is None:
        service = build_service()
    return service.summarize_articles(articles, max_words=max_words)


@mcp.tool()
def answer_question(question: str, articles: list[Article]) -> str:
    """Answer a question using only the provided articles as context.

    Args:
        question: User's question to answer.
        articles: Articles used to ground the answer.

    Returns:
        str: Grounded answer.
    """

    global service
    if service is None:
        service = build_service()
    return service.answer_question(question, articles=articles)


def main() -> None:
    """Entrypoint to run the MCP server over stdio."""

    mcp.run()


if __name__ == "__main__":
    main()


