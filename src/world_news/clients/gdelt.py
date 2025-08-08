from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any

from gdeltdoc import Filters, GdeltDoc


@dataclass(frozen=True)
class Article:
    title: str = ""
    url: str = ""
    socialimage: str | None = None
    language: str | None = None
    sourcecountry: str | None = None
    domain: str | None = None
    seendate: str | None = None
    isduplicate: int | None = None
    sourceurl: str | None = None
    snippet: str | None = None


def article_to_dict(article: Article) -> dict[str, Any]:
    return asdict(article)


def articles_to_dicts(articles: list[Article]) -> list[dict[str, Any]]:
    return [article_to_dict(a) for a in articles]


def article_from_row(row: Any) -> Article:
    return Article(
        title=str(row.get("title", "")),
        url=str(row.get("url", "")),
        socialimage=(str(si) if (si := row.get("socialimage")) else None),
        language=(str(lang) if (lang := row.get("language")) else None),
        sourcecountry=(str(sc) if (sc := row.get("sourcecountry")) else None),
        domain=(str(dom) if (dom := row.get("domain")) else None),
        seendate=(str(sd) if (sd := row.get("seendate")) else None),
        isduplicate=int(row.get("isduplicate")) if row.get("isduplicate") is not None else None,
        sourceurl=(str(su) if (su := row.get("sourceurl")) else None),
        snippet=(str(sn) if (sn := row.get("snippet")) else None),
    )


def articles_from_dicts(items: list[dict[str, Any]]) -> list[Article]:
    articles: list[Article] = []
    for d in items:
        if not isinstance(d, dict):
            continue
        articles.append(
            Article(
                title=str(d.get("title", "")),
                url=str(d.get("url", "")),
                socialimage=d.get("socialimage"),
                language=d.get("language"),
                sourcecountry=d.get("sourcecountry"),
                domain=d.get("domain"),
                seendate=d.get("seendate"),
                isduplicate=d.get("isduplicate"),
                sourceurl=d.get("sourceurl"),
                snippet=d.get("snippet"),
            )
        )
    return articles


@dataclass
class GDELTClient:
    gdelt: GdeltDoc

    @classmethod
    def create_default(cls) -> GDELTClient:
        return cls(gdelt=GdeltDoc())

    def search_articles(
        self,
        query: str,
        start_date: str | None = None,
        end_date: str | None = None,
        max_records: int = 20,
        sort_by: str = "date",
        languages: Iterable[str] | None = None,
    ) -> list[Article]:
        filters = Filters(
            keyword=query,
            start_date=start_date,
            end_date=end_date,
            num_records=max_records,
            sortby=sort_by,
            language=list(languages) if languages else None,
        )
        df = self.gdelt.article_search(filters)
        return [article_from_row(row) for _, row in df.iterrows()]
