# 02_tools.py
from langchain.tools import tool
import requests, bs4

# -------- Web Search (DuckDuckGo) --------
@tool("web_search", return_direct=False)
def web_search(query: str, k: int = 5):
    """
    Search the web using DuckDuckGo (no API key required).
    Returns a list of {title, url, snippet}.
    """
    url = "https://duckduckgo.com/html/"
    params = {"q": query}
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.post(url, data=params, headers=headers, timeout=10)
    soup = bs4.BeautifulSoup(res.text, "html.parser")

    results = []
    for a in soup.select(".result__a")[:k]:
        link = a.get("href")
        title = a.text
        snippet_tag = a.find_parent("div", class_="result__body").select_one(".result__snippet")
        snippet = snippet_tag.text if snippet_tag else ""
        results.append({"title": title, "url": link, "snippet": snippet})
    return results


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