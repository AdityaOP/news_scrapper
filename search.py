import requests
import feedparser
from datetime import datetime, timedelta
from config import SEARCH_QUERIES, MAX_RESULTS_PER_QUERY, TIME_FILTER

def search_google_news_rss(query: str, max_results: int = 10) -> list:
    """Search Google News via RSS feed"""
    try:
        # Google News RSS URL
        base_url = "https://news.google.com/rss/search"
        params = {
            "q": query,
            "hl": "en-AU",
            "gl": "AU",
            "ceid": "AU:en"
        }
        
        url = f"{base_url}?q={requests.utils.quote(query)}&hl=en-AU&gl=AU&ceid=AU:en"
        
        response = requests.get(url, timeout=10)
        feed = feedparser.parse(response.content)
        
        results = []
        for entry in feed.entries[:max_results]:
            results.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "date": entry.get("published", ""),
                "source": entry.get("source", {}).get("title", "Unknown")
            })
        
        return results
    
    except Exception as e:
        print(f"      ⚠️ Google News RSS error: {e}")
        return []

def search_duckduckgo_news(query: str, max_results: int = 10, timelimit: str = "w") -> list:
    """Search DuckDuckGo news"""
    try:
        from duckduckgo_search import DDGS
        
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news(
                keywords=query,
                region="au-en",
                safesearch="moderate",
                timelimit=timelimit,
                max_results=max_results,
            ):
                results.append({
                    "title": r.get("title"),
                    "link": r.get("url"),
                    "date": r.get("date"),
                    "source": r.get("source", "Unknown")
                })
        
        return results
    
    except Exception as e:
        print(f"      ⚠️ DuckDuckGo error: {e}")
        return []

def filter_by_date(results: list, days: int = 7) -> list:
    """Filter results to only include recent articles"""
    if not days:
        return results
    
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered = []
    
    for item in results:
        try:
            # Try to parse the date
            date_str = item.get("date", "")
            if date_str:
                # Handle various date formats
                for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%d"]:
                    try:
                        article_date = datetime.strptime(date_str.split('+')[0].strip(), fmt.replace("%z", ""))
                        if article_date >= cutoff_date:
                            filtered.append(item)
                        break
                    except:
                        continue
        except:
            # If date parsing fails, include it anyway
            filtered.append(item)
    
    return filtered

def search_news():
    """
    Search for news using multiple sources and queries.
    Returns deduplicated results.
    """
    all_results = []
    seen_urls = set()
    
    print(f"🔎 Running {len(SEARCH_QUERIES)} search queries across multiple sources...")
    
    for query_num, query in enumerate(SEARCH_QUERIES, 1):
        print(f"\n   Query {query_num}/{len(SEARCH_QUERIES)}: '{query}'")
        
        # Try Google News RSS first
        print(f"      Trying Google News RSS...")
        google_results = search_google_news_rss(query, MAX_RESULTS_PER_QUERY)
        
        # Try DuckDuckGo as fallback
        print(f"      Trying DuckDuckGo...")
        ddg_results = search_duckduckgo_news(query, MAX_RESULTS_PER_QUERY, TIME_FILTER)
        
        # Combine results
        combined = google_results + ddg_results
        
        # Deduplicate by URL
        new_results = 0
        for item in combined:
            url = item.get("link")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append(item)
                new_results += 1
        
        print(f"      → Found {len(combined)} results ({new_results} new)")
    
    # Filter by date if needed
    days_filter = {"d": 1, "w": 7, "m": 30}.get(TIME_FILTER, None)
    if days_filter:
        before_filter = len(all_results)
        all_results = filter_by_date(all_results, days_filter)
        print(f"\n🗓️ Filtered to last {days_filter} days: {before_filter} → {len(all_results)} articles")
    
    print(f"\n✅ Total unique results: {len(all_results)}")
    
    # Sort by date (most recent first)
    all_results.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    return all_results