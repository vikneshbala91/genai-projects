# 02_tools.py
from langchain.tools import tool
import requests, bs4
from ddgs import DDGS

# -------- Web Search (DuckDuckGo) --------
@tool("web_search", return_direct=False)
def web_search(query: str, k: int = 5):
    """
    Search the web using DuckDuckGo (no API key required).
    Returns a list of {title, url, snippet}.
    Use this to find information about claims, facts, and current events.
    """
    try:
        # Use duckduckgo_search library which is more reliable
        with DDGS() as ddgs:
            results = []
            # Get text results
            for r in ddgs.text(query, max_results=k):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
            return results
    except Exception as e:
        # Fallback to empty results with error info
        return [{"title": "Search Error", "url": "", "snippet": f"Error performing search: {str(e)}"}]


# -------- Read URL Tool --------
@tool("read_url", return_direct=False)
def read_url(url: str) -> str:
    """
    Fetch and clean visible text from a web page.
    """
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
    except Exception as e:
        return f"[Error fetching {url}: {e}]"

    soup = bs4.BeautifulSoup(r.text, "html.parser")
    for s in soup(["script", "style", "noscript"]):
        s.decompose()

    text = " ".join(soup.get_text(" ").split())
    return text[:20000]  # cap length to avoid token overflow