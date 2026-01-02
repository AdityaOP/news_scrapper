import requests
import feedparser
from datetime import datetime, timedelta
from config import SEARCH_QUERIES, MAX_RESULTS_PER_QUERY, TIME_FILTER
from urllib.parse import urlparse, quote
import xml.etree.ElementTree as ET
import time

# Import keywords, domains, and scoring function from separate file
from keywords import calculate_relevance_score


def search_google_news_rss(query: str, max_results: int = 10) -> list:
    """Search Google News via RSS feed with AU region"""
    try:
        au_query = f"{query}"
        base_url = "https://news.google.com/rss/search"
        url = f"{base_url}?q={requests.utils.quote(au_query)}&hl=en-AU"
        
        response = requests.get(url, timeout=20)
        feed = feedparser.parse(response.content)
        
        results = []
        for entry in feed.entries[:max_results * 2]:
            item = {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "date": entry.get("published", ""),
                "source": entry.get("source", {}).get("title", "Unknown")
            }
            
            results.append(item)
        
        return results
    
    except Exception as e:
        print(f"      ⚠️ Google News RSS error: {e}")
        return []


def search_duckduckgo_news(query: str, max_results: int = 20, timelimit: str = "w") -> list:
    """Search DuckDuckGo news with Australian filter"""
    try:
        from duckduckgo_search import DDGS
        
        au_query = f"{query}"
        
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
    
    print(f"🔎 Running {len(SEARCH_QUERIES)} search queries for news...")
    print(f"🎯 Will select TOP 20 BEST matches based on keyword relevance\n")
    
    for query_num, query in enumerate(SEARCH_QUERIES, 1):
        print(f"   Query {query_num}/{len(SEARCH_QUERIES)}: '{query}'")
        
        # Try Google News RSS first
        print(f"      Trying Google News RSS ...")
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
        print(f"\n✂️ Filtered to last {days_filter} days: {before_filter} → {len(all_results)} articles")
    
    print(f"\n📊 Total unique articles found: {len(all_results)}")
    
    # Calculate relevance scores for all articles using proprietary algorithm
    print(f"🔢 Calculating relevance scores...")
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
    print(f"✅ Returning TOP 20 articles for processing")
    print(f"{'='*80}\n")
    
    return top_20