from __future__ import annotations

import argparse
import sys
from typing import Optional

import httpx


def call_chat(api_base: str, query: str, timeout: float = 60.0) -> dict:
    url = f"{api_base.rstrip('/')}/chat"
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json={"query": query})
        resp.raise_for_status()
        return resp.json()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Test /chat endpoint with a query")
    parser.add_argument("query", nargs="?", help="User query to send")
    parser.add_argument(
        "--api-base", default="http://127.0.0.1:8000", help="API base URL (default: http://127.0.0.1:8000)",
    )
    args = parser.parse_args(argv)

    if args.query:
        data = call_chat(args.api_base, args.query)
        print(f"Answer:\n{data.get('answer','')}")
        print(f"num_articles: {data.get('num_articles')}")
        return 0

    # Interactive mode
    print("Enter queries (Ctrl+C to exit):")
    try:
        while True:
            q = input("> ").strip()
            if not q:
                continue
            data = call_chat(args.api_base, q)
            print(f"\nAnswer:\n{data.get('answer','')}")
            print(f"num_articles: {data.get('num_articles')}\n")
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())


