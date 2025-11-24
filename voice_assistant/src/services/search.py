from typing import List, Optional

try:
    from duckduckgo_search import DDGS
except Exception:  # pragma: no cover - fallback for environments without the lib
    DDGS = None


def search_web(query: str, max_results: int = 3) -> List[str]:
    if not query:
        return []
    if DDGS is None:
        return ["Search library unavailable; install duckduckgo-search."]

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            summaries = []
            for item in results:
                title = item.get("title") or "Result"
                href = item.get("href") or ""
                body = item.get("body") or ""
                summaries.append(f"{title} — {body} ({href})".strip())
            return summaries
    except Exception as exc:  # pragma: no cover - network/dependency failures
        return [f"Search failed: {exc}"]
