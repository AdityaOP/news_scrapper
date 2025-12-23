import requests
import feedparser
from datetime import datetime, timedelta
from config import SEARCH_QUERIES, MAX_RESULTS_PER_QUERY, TIME_FILTER
from urllib.parse import urlparse

# Australian news domains and keywords
AUSTRALIAN_DOMAINS = [
    'abc.net.au', 'smh.com.au', 'theage.com.au', 'afr.com', 
    'news.com.au', '9news.com.au', '7news.com.au', 'theaustralian.com.au',
    'crikey.com.au', 'theconversation.com', 'healthtimes.com.au',
    'ausdoc.com.au', 'medicalrepublic.com.au', 'healthcareit.com.au',
    'digitalhealth.gov.au', 'pulseitmagazine.com.au', 'governmentnews.com.au',
    'innovationaus.com', 'itnews.com.au', 'zdnet.com', 'delimiter.com.au'
]

AUSTRALIAN_KEYWORDS = [
    'australia', 'australian', 'sydney', 'melbourne', 'brisbane', 
    'perth', 'adelaide', 'canberra', 'hobart', 'darwin',
    'nsw', 'vic', 'qld', 'wa', 'sa', 'act', 'nt', 'tas',
    'new south wales', 'victoria', 'queensland', 'western australia',
    'south australia', 'northern territory', 'tasmania',
    'commonwealth', 'federal', 'state government'
]

def is_australian_news(item: dict) -> bool:
    """
    Strictly check if news item is Australian.
    Returns True only if it's clearly Australian content.
    """
    url = item.get("link", "").lower()
    title = item.get("title", "").lower()
    source = item.get("source", "").lower()
    
    # Check 1: Is it from an Australian domain?
    domain = urlparse(url).netloc.lower()
    if any(aus_domain in domain for aus_domain in AUSTRALIAN_DOMAINS):
        return True
    
    # Check 2: Does the title or source mention Australia explicitly?
    text_to_check = f"{title} {source}"
    if any(keyword in text_to_check for keyword in AUSTRALIAN_KEYWORDS):
        return True
    
    # If neither check passes, it's not Australian news
    return False

def search_google_news_rss(query: str, max_results: int = 10) -> list:
    """Search Google News via RSS feed with AU region"""
    try:
        # Force Australian region in the query
        au_query = f"{query} Australia"
        
        base_url = "https://news.google.com/rss/search"
        url = f"{base_url}?q={requests.utils.quote(au_query)}&hl=en-AU&gl=AU&ceid=AU:en"
        
        response = requests.get(url, timeout=10)
        feed = feedparser.parse(response.content)
        
        results = []
        for entry in feed.entries[:max_results * 2]:  # Fetch more to account for filtering
            item = {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "date": entry.get("published", ""),
                "source": entry.get("source", {}).get("title", "Unknown")
            }
            
            # Only include if it's Australian news
            if is_australian_news(item):
                results.append(item)
                if len(results) >= max_results:
                    break
        
        return results
    
    except Exception as e:
        print(f"      ⚠️ Google News RSS error: {e}")
        return []

def search_duckduckgo_news(query: str, max_results: int = 10, timelimit: str = "w") -> list:
    """Search DuckDuckGo news with Australian filter"""
    try:
        from duckduckgo_search import DDGS
        
        # Force Australian context in query
        au_query = f"{query} Australia"
        
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news(
                keywords=au_query,
                region="au-en",
                safesearch="moderate",
                timelimit=timelimit,
                max_results=max_results * 2,  # Fetch more to account for filtering
            ):
                item = {
                    "title": r.get("title"),
                    "link": r.get("url"),
                    "date": r.get("date"),
                    "source": r.get("source", "Unknown")
                }
                
                # Only include if it's Australian news
                if is_australian_news(item):
                    results.append(item)
                    if len(results) >= max_results:
                        break
        
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
            date_str = item.get("date", "")
            if date_str:
                for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%d"]:
                    try:
                        article_date = datetime.strptime(date_str.split('+')[0].strip(), fmt.replace("%z", ""))
                        if article_date >= cutoff_date:
                            filtered.append(item)
                        break
                    except:
                        continue
        except:
            filtered.append(item)
    
    return filtered

def search_news():
    """
    Search for Australian news using multiple sources and queries.
    Returns deduplicated results that are strictly Australian.
    """
    all_results = []
    seen_urls = set()
    
    print(f"🔎 Running {len(SEARCH_QUERIES)} search queries for AUSTRALIAN news only...")
    
    for query_num, query in enumerate(SEARCH_QUERIES, 1):
        print(f"\n   Query {query_num}/{len(SEARCH_QUERIES)}: '{query}'")
        
        # Try Google News RSS first
        print(f"      Trying Google News RSS (AU region)...")
        google_results = search_google_news_rss(query, MAX_RESULTS_PER_QUERY)
        
        # Try DuckDuckGo as fallback
        print(f"      Trying DuckDuckGo (AU region)...")
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
        
        print(f"      → Found {len(combined)} Australian results ({new_results} new)")
    
    # Filter by date if needed
    days_filter = {"d": 1, "w": 7, "m": 30}.get(TIME_FILTER, None)
    if days_filter:
        before_filter = len(all_results)
        all_results = filter_by_date(all_results, days_filter)
        print(f"\n🗓️ Filtered to last {days_filter} days: {before_filter} → {len(all_results)} articles")
    
    print(f"\n✅ Total unique Australian results: {len(all_results)}")
    
    # Sort by date (most recent first)
    all_results.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    return all_results