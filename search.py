from duckduckgo_search import DDGS
from config import QUERY, MAX_RESULTS

def search_news():
    results = []

    with DDGS() as ddgs:
        for r in ddgs.news(
            keywords=QUERY,
            region="au-en",
            safesearch="moderate",
            timelimit="d",   # 🔹 last 24 hours
            max_results=MAX_RESULTS,
        ):
            results.append({
                "title": r.get("title"),
                "link": r.get("url"),
                "date": r.get("date")
            })

    print(f"🔎 Found {len(results)} news results")
    return results