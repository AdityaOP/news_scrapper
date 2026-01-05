import requests
import feedparser
from datetime import datetime, timedelta
from config import SEARCH_QUERIES, MAX_RESULTS_PER_QUERY, TIME_FILTER
from urllib.parse import urlparse, quote
import xml.etree.ElementTree as ET
import time
from ddgs import DDGS
from difflib import SequenceMatcher

# Import keywords, domains, and scoring function from separate file
from keywords import calculate_relevance_score


def normalize_url(url: str) -> str:
    """Normalize URL for comparison (remove query params, fragments, trailing slashes)"""
    try:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        # Remove query params and fragments, normalize path
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip('/'),
            '', '', ''
        ))
        return normalized
    except:
        return url.lower().strip()


def are_titles_similar(title1: str, title2: str, threshold: float = 0.90) -> bool:
    """Check if two titles are similar using sequence matching"""
    if not title1 or not title2:
        return False
    
    # Normalize titles
    t1 = title1.lower().strip()
    t2 = title2.lower().strip()
    
    # Calculate similarity ratio
    ratio = SequenceMatcher(None, t1, t2).ratio()
    return ratio >= threshold


def is_duplicate(new_item: dict, existing_items: list) -> bool:
    """
    Check if an article is a duplicate based on:
    1. Exact URL match (after normalization)
    2. Very similar title (>85% match)
    """
    new_url = normalize_url(new_item.get('link', ''))
    new_title = new_item.get('title', '')
    
    for existing in existing_items:
        existing_url = normalize_url(existing.get('link', ''))
        existing_title = existing.get('title', '')
        
        # Check URL match
        if new_url and existing_url and new_url == existing_url:
            return True
        
        # Check title similarity
        if are_titles_similar(new_title, existing_title):
            return True
    
    return False


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


def search_duckduckgo_news(query, max_results=20, timelimit="w", retries=2):
    

    for attempt in range(retries):
        try:
            results = []
            with DDGS(timeout=20) as ddgs:
                for r in ddgs.news(
                    query,
                    region="au-en",
                    timelimit=timelimit,
                    max_results=max_results
                ):
                    results.append({
                        "title": r.get("title"),
                        "link": r.get("url"),
                        "date": r.get("date"),
                        "source": "DuckDuckGo"
                    })
            return results

        except Exception as e:
            print(f"      ⚠️ DuckDuckGo timeout (attempt {attempt+1}/{retries})")
            time.sleep(2)

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
    Search for Australian news and return ALL unique matches sorted by relevance score.
    Removes duplicates based on URL normalization and title similarity.
    """
    all_results = []
    duplicates_removed = 0
    
    print(f"🔎 Running {len(SEARCH_QUERIES)} search queries for news...")
    print(f"🎯 Will return ALL unique articles sorted by relevance score\n")
    
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
        
        # Deduplicate using enhanced method
        new_results = 0
        for item in combined:
            if not is_duplicate(item, all_results):
                all_results.append(item)
                new_results += 1
            else:
                duplicates_removed += 1
        
        print(f"      → Found {len(combined)} results ({new_results} new, {len(combined)-new_results} duplicates)")
    
    # Filter by date if needed
    days_filter = {"d": 1, "w": 7, "m": 30}.get(TIME_FILTER, None)
    if days_filter:
        before_filter = len(all_results)
        all_results = filter_by_date(all_results, days_filter)
        print(f"\n✂️ Filtered to last {days_filter} days: {before_filter} → {len(all_results)} articles")
    
    print(f"\n📊 Total unique articles found: {len(all_results)}")
    print(f"🗑️ Duplicates removed: {duplicates_removed}")
    
    # Calculate relevance scores for all articles using proprietary algorithm
    print(f"🔢 Calculating relevance scores...")
    for item in all_results:
        item['relevance_score'] = calculate_relevance_score(item)
    
    # Sort by relevance score (highest first)
    all_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

    all_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

    # Keep only articles with relevance score > 1
    MIN_RELEVANCE_SCORE = 1
    all_results = [
        item for item in all_results
        if item.get('relevance_score', 0) > MIN_RELEVANCE_SCORE
    ]
    
    # Display scoring results
    print(f"\n{'='*80}")
    print(f"🏆 ALL ARTICLES SORTED BY RELEVANCE SCORE:")
    print(f"{'='*80}\n")
    
    for i, item in enumerate(all_results, 1):
        score = item.get('relevance_score', 0)
        title = item.get('title', 'Untitled')[:70]
        print(f"  {i}. [{score:.1f} pts] {title}...")
    
    print(f"\n{'='*80}")
    print(f"\n📊 Articles with relevance score > {MIN_RELEVANCE_SCORE}: {len(all_results)}")
    print(f"{'='*80}\n")
    
    return all_results