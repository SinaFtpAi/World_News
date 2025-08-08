from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import google.generativeai as genai

from ..prompt_library import get_prompts


@dataclass
class GeminiClient:
    model: genai.GenerativeModel

    @classmethod
    def create(cls, api_key: str, model_name: str) -> GeminiClient:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        return cls(model=model)

    def summarize(self, text: str, max_words: int = 160) -> str:
        template = get_prompts().summarize
        prompt = template.replace("{{max_words}}", str(max_words)).replace("{{text}}", text)
        response = self.model.generate_content(prompt)
        return getattr(response, "text", "") or ""

    def answer_based_on_context(self, question: str, passages: Iterable[str]) -> str:
        context_blob = "\n\n".join(passages)
        template = get_prompts().qa
        prompt = template.replace("{{context}}", context_blob).replace("{{question}}", question)
        response = self.model.generate_content(prompt)
        return getattr(response, "text", "") or ""
