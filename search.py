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
    'digitalhealth.gov.au/newsroom', 'pulseitmagazine.com.au', 'governmentnews.com.au',
    'innovationaus.com', 'itnews.com.au', 'zdnet.com', 'delimiter.com.au'
]

AUSTRALIAN_KEYWORDS = [
    'australia', 'australian'
]

# High-value keywords for digital health + AI

def calculate_relevance_score(item: dict) -> float:
    """
    Calculate relevance score for an article based on keywords.
    Higher score = more relevant to digital health + AI in Australia.
    """
    title = item.get("title", "").lower()
    source = item.get("source", "").lower()
    url = item.get("link", "").lower()
    
    score = 0.0
    
    # 1. Source quality bonus (trusted Australian health/tech sources)
    trusted_sources = [
        'abc.net.au', 'smh.com.au', 'afr.com', 'theage.com.au',
        'healthcareit.com.au', 'ausdoc.com.au', 'medicalrepublic.com.au',
        'innovationaus.com', 'digitalhealth.gov.au/newsroom', 'pulseitmagazine.com.au'
    ]
    
    domain = urlparse(url).netloc.lower()
    if any(trusted in domain for trusted in trusted_sources):
        score += 5.0
    elif any(aus_domain in domain for aus_domain in AUSTRALIAN_DOMAINS):
        score += 2.0
    
    
    # 3. Australian context (must have this)
    if any(keyword in title for keyword in AUSTRALIAN_KEYWORDS):
        score += 2.0
    
    return score

def is_australian_news(item: dict) -> bool:
    """Check if news item is Australian"""
    url = item.get("link", "").lower()
    title = item.get("title", "").lower()
    source = item.get("source", "").lower()
    
    domain = urlparse(url).netloc.lower()
    if any(aus_domain in domain for aus_domain in AUSTRALIAN_DOMAINS):
        return True
    
    text_to_check = f"{title} {source}"
    if any(keyword in text_to_check for keyword in AUSTRALIAN_KEYWORDS):
        return True
    
    return False

def search_google_news_rss(query: str, max_results: int = 10) -> list:
    """Search Google News via RSS feed with AU region"""
    try:
        au_query = f"{query} Australia"
        base_url = "https://news.google.com/rss/search"
        url = f"{base_url}?q={requests.utils.quote(au_query)}&hl=en-AU&gl=AU&ceid=AU:en"
        
        response = requests.get(url, timeout=10)
        feed = feedparser.parse(response.content)
        
        results = []
        for entry in feed.entries[:max_results * 2]:
            item = {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "date": entry.get("published", ""),
                "source": entry.get("source", {}).get("title", "Unknown")
            }
            
            if is_australian_news(item):
                results.append(item)
        
        return results
    
    except Exception as e:
        print(f"      ⚠️ Google News RSS error: {e}")
        return []

def search_duckduckgo_news(query: str, max_results: int = 20, timelimit: str = "w") -> list:
    """Search DuckDuckGo news with Australian filter"""
    try:
        from duckduckgo_search import DDGS
        
        au_query = f"{query} Australia"
        
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news(
                keywords=au_query,
                region="au-en",
                safesearch="moderate",
                timelimit=timelimit,
                max_results=max_results * 2,
            ):
                item = {
                    "title": r.get("title"),
                    "link": r.get("url"),
                    "date": r.get("date"),
                    "source": r.get("source", "Unknown")
                }
                
                if is_australian_news(item):
                    results.append(item)
        
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
    Search for Australian news and return TOP 20 BEST matches based on relevance scoring.
    """
    all_results = []
    seen_urls = set()
    
    print(f"🔎 Running {len(SEARCH_QUERIES)} search queries for AUSTRALIAN news...")
    print(f"🎯 Will select TOP 20 BEST matches based on keyword relevance\n")
    
    for query_num, query in enumerate(SEARCH_QUERIES, 1):
        print(f"   Query {query_num}/{len(SEARCH_QUERIES)}: '{query}'")
        
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
        print(f"\n Filtered to last {days_filter} days: {before_filter} → {len(all_results)} articles")
    
    print(f"\n Total unique Australian articles found: {len(all_results)}")
    
    # Calculate relevance scores for all articles
    print(f" Calculating relevance scores...")
    for item in all_results:
        item['relevance_score'] = calculate_relevance_score(item)
    
    # Sort by relevance score (highest first)
    all_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    # Take only top 20
    top_20 = all_results[:20]
    
    # Display scoring results
    print(f"\n{'='*80}")
    print(f"🏆 TOP 20 BEST MATCHES (by relevance score):")
    print(f"{'='*80}\n")
    
    for i, item in enumerate(top_20, 1):
        score = item.get('relevance_score', 0)
        title = item.get('title', 'Untitled')[:70]
        print(f"  {i}. [{score:.1f} pts] {title}...")
    
    print(f"\n{'='*80}")
    print(f" Returning TOP 10 articles for processing")
    print(f"{'='*80}\n")
    
    return top_20