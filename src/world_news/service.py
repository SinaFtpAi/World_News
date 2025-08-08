"""Service orchestration combining GDELT and Gemini.

Exposes a high-level `NewsService` used by both the HTTP app and the MCP tools.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .clients import Article, GDELTClient, GeminiClient


@dataclass
class NewsService:
    """High-level orchestration for fetching and analyzing news.

    Attributes:
        gdelt_client: Client to query GDELT Doc API.
        gemini_client: Client to call Gemini model.
    """

    gdelt_client: GDELTClient
    gemini_client: GeminiClient

    @classmethod
    def create_default(cls, gemini_api_key: str, gemini_model: str) -> NewsService:
        """Create a default service with default clients.

        Args:
            gemini_api_key: API key for Gemini.
            gemini_model: Model name.

        Returns:
            NewsService: Configured service instance.
        """

        return cls(
            gdelt_client=GDELTClient.create_default(),
            gemini_client=GeminiClient.create(api_key=gemini_api_key, model_name=gemini_model),
        )

    def search(
        self,
        query: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        max_records: int = 20,
        languages: Sequence[str] | None = None,
    ) -> list[Article]:
        """Search news articles on GDELT.

        Args:
            query: User query or keywords.
            start_date: Optional start date.
            end_date: Optional end date.
            max_records: Record cap.
            languages: Optional language filters.

        Returns:
            list[Article]: Articles.
        """

        return self.gdelt_client.search_articles(
            query=query,
            start_date=start_date,
            end_date=end_date,
            max_records=max_records,
            languages=languages,
        )

    def summarize_articles(self, articles: Iterable[Article], *, max_words: int = 160) -> str:
        """Summarize multiple articles into a single digest.

        Args:
            articles: Article records.
            max_words: Soft word cap.

        Returns:
            str: Digest summary.
        """

        passages: list[str] = []
        for a in articles:
            title = a.get("title") or ""
            url = a.get("url") or ""
            snippet = a.get("snippet") or ""
            passages.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}")
        combined = "\n\n".join(passages)
        return self.gemini_client.summarize(combined, max_words=max_words)

    def answer_question(self, question: str, *, articles: Iterable[Article]) -> str:
        """Answer a question grounded in provided articles.

        Args:
            question: User question.
            articles: Article records used as context.

        Returns:
            str: Grounded answer.
        """

        passages: list[str] = []
        for a in articles:
            title = a.get("title") or ""
            url = a.get("url") or ""
            snippet = a.get("snippet") or ""
            passages.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}")
        return self.gemini_client.answer_based_on_context(question, passages)
