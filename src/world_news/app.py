"""FastAPI app exposing a `/chat` endpoint for Q&A over news.

The endpoint fetches relevant articles from GDELT and answers the user's
question using Gemini, grounded in the fetched articles.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .config import get_settings
from .pipeline import run_pipeline
from .service import NewsService


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    query: str = Field(..., description="User's question or topic")


class ChatResponse(BaseModel):
    """Response body for the chat endpoint."""

    answer: str
    num_articles: int


def build_service() -> NewsService:
    settings = get_settings()
    return NewsService.create_default(
        gemini_api_key=settings.gemini_api_key, gemini_model=settings.gemini_model
    )


app = FastAPI(title="World News Chat API", version="0.1.0")
service = build_service()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Answer a news-related question based on fresh GDELT data.

    This endpoint fetches relevant articles then answers grounded in those
    articles. It returns the answer and the number of articles used.
    """

    # Two-LLM pipeline:
    # 1) Planner LLM creates a clean query and optional params
    # 2) Retrieve via GDELT
    # 3) Summarizer LLM produces the final answer
    summary = run_pipeline(
        user_question=req.query,
        planner_llm=service.gemini_client,
        retriever=service.gdelt_client,
        summarizer_llm=service.gemini_client,
    )
    # We do not return article count here since retrieval is encapsulated in pipeline.
    return ChatResponse(answer=summary, num_articles=0)


def main() -> None:
    import uvicorn

    uvicorn.run("world_news.app:app", reload=True, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()


