import requests
import cloudscraper
from bs4 import BeautifulSoup
from newspaper import Article
import time
from urllib.parse import urlparse

def fetch_with_newspaper(url: str) -> str:
    """Strategy 1: Use newspaper3k with custom headers"""
    try:
        article = Article(url)
        article.config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        article.config.request_timeout = 15
        
        article.download()
        article.parse()
        
        if article.text and len(article.text.strip()) > 100:
            return article.text
    except Exception as e:
        pass  # Silent fail, will try next strategy
    
    return ""

def fetch_with_cloudscraper(url: str) -> str:
    """Strategy 2: Use cloudscraper for Cloudflare-protected sites"""
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        response = scraper.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            element.decompose()
        
        text = extract_article_text(soup, url)
        
        if text and len(text.strip()) > 100:
            return text
            
    except Exception as e:
        pass  # Silent fail
    
    return ""

def fetch_with_requests(url: str) -> str:
    """Strategy 3: Use standard requests with comprehensive headers"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/'
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            element.decompose()
        
        text = extract_article_text(soup, url)
        
        if text and len(text.strip()) > 100:
            return text
            
    except Exception as e:
        pass  # Silent fail
    
    return ""

def extract_article_text(soup: BeautifulSoup, url: str) -> str:
    """Extract text using multiple strategies"""
    
    domain = urlparse(url).netloc.lower()
    
    # Site-specific selectors
    selectors_map = {
        'msn.com': [
            'article',
            'div[class*="article"]',
            'div[class*="story"]',
            'div[class*="content"]',
            'main article',
            'main div[class*="article"]',
            '[data-t="article-body"]',
            '.article-body',
            '.articlebody',
            'main .content',
            'div[role="main"]',
            'div[id*="article"]',
            'div[id*="content"]',
        ],
        'abc.net.au': [
            'article div[data-component="ArticleBody"]',
            'article .article-content',
            'article #body',
            '.article__body',
            'div[data-component="BodyText"]'
        ],
        'smh.com.au': ['article .article-body', '#article-body', 'article'],
        'theage.com.au': ['article .article-body', 'article'],
        'afr.com': ['article .article-content', 'article'],
        'news.com.au': ['.story-primary', '.story-block', 'article'],
        'theguardian.com': ['.article-body-commercial-selector', 'article'],
        'bbc.com': ['.article__body-content', 'article'],
        'reuters.com': ['.article-body__content', 'article'],
        '9news.com.au': ['.article__body', 'article', '.story__body'],
        '7news.com.au': ['.article-body', 'article'],
    }
    
    # Try domain-specific selectors
    for domain_key, selectors in selectors_map.items():
        if domain_key in domain:
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    text = '\n\n'.join([el.get_text(strip=True, separator=' ') for el in elements])
                    if len(text) > 200:
                        return clean_text(text)
    
    # Generic strategies
    strategies = [
        # Strategy 1: article tag
        lambda: soup.find_all('article'),
        # Strategy 2: main tag
        lambda: soup.find_all('main'),
        # Strategy 3: Content divs
        lambda: soup.find_all(['div', 'section'], class_=lambda x: x and any(
            kw in str(x).lower() for kw in ['content', 'article', 'story', 'body', 'text', 'post']
        )),
        # Strategy 4: Role-based
        lambda: soup.find_all(['div', 'section'], attrs={'role': 'main'}),
    ]
    
    for strategy in strategies:
        try:
            elements = strategy()
            if elements:
                # Try to find the element with most paragraphs
                best_element = None
                max_paragraphs = 0
                
                for el in elements:
                    p_count = len(el.find_all('p'))
                    if p_count > max_paragraphs:
                        max_paragraphs = p_count
                        best_element = el
                
                if best_element and max_paragraphs >= 3:
                    paragraphs = best_element.find_all('p')
                    text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
                    if len(text) > 200:
                        return clean_text(text)
        except:
            continue
    
    # Last resort: all paragraphs
    paragraphs = soup.find_all('p')
    if len(paragraphs) >= 5:
        text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
        if len(text) > 200:
            return clean_text(text)
    
    return ""

def clean_text(text: str) -> str:
    """Clean up extracted text"""
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n\n'.join(lines)
    
    # Remove very short paragraphs (likely navigation/metadata)
    paragraphs = text.split('\n\n')
    paragraphs = [p for p in paragraphs if len(p) > 30]
    
    return '\n\n'.join(paragraphs)

def fetch_article_text(url: str) -> str:
    """
    Fetch article text using multiple strategies with fallbacks.
    Returns article text or empty string on complete failure.
    """
    
    print(f"   🔗 URL: {url[:80]}...")
    
    # Try different strategies in order
    strategies = [
        ("cloudscraper", fetch_with_cloudscraper),
        ("requests", fetch_with_requests),
        ("newspaper3k", fetch_with_newspaper),
    ]
    
    for strategy_name, strategy_func in strategies:
        try:
            print(f"   🔄 Trying {strategy_name}...")
            text = strategy_func(url)
            if text:
                print(f"   ✅ SUCCESS with {strategy_name}: Fetched {len(text)} chars")
                return text
            else:
                print(f"   ⚠️ {strategy_name}: No content extracted")
                time.sleep(0.5)  # Brief delay between strategies
        except Exception as e:
            print(f"   ❌ {strategy_name} error: {str(e)[:80]}")
            time.sleep(0.5)
    
    print(f"   ❌ All {len(strategies)} strategies failed for this URL")
    return ""