import requests
import cloudscraper
from bs4 import BeautifulSoup
from newspaper import Article
import time
from urllib.parse import urlparse

def fetch_with_playwright(url: str) -> str:
    """Strategy 1: Use Playwright for JavaScript-rendered content (BEST for MSN, dynamic sites)"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            # Navigate and wait for content
            page.goto(url, wait_until='networkidle', timeout=20000)
            
            # Additional wait for dynamic content
            page.wait_for_timeout(3000)
            
            # Get the fully rendered HTML
            content = page.content()
            browser.close()
            
            soup = BeautifulSoup(content, 'lxml')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
                element.decompose()
            
            text = extract_article_text(soup, url)
            
            if text and len(text.strip()) > 100:
                return text
                
    except ImportError:
        pass  # Playwright not installed, skip
    except Exception as e:
        pass  # Silent fail
    
    return ""

def fetch_with_selenium(url: str) -> str:
    """Strategy 2: Use Selenium for JavaScript-rendered content (Alternative to Playwright)"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Initialize driver with webdriver-manager (auto-downloads chromedriver)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            driver.get(url)
            
            # Wait for article content to load (adjust selector as needed)
            wait = WebDriverWait(driver, 10)
            # Try to wait for common article elements
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
            except:
                pass  # Continue even if specific element not found
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Get page source after JavaScript execution
            content = driver.page_source
            
            soup = BeautifulSoup(content, 'lxml')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
                element.decompose()
            
            text = extract_article_text(soup, url)
            
            if text and len(text.strip()) > 100:
                return text
                
        finally:
            driver.quit()
            
    except ImportError:
        pass  # Selenium not installed, skip
    except Exception as e:
        pass  # Silent fail
    
    return ""

def fetch_with_requests_html(url: str) -> str:
    """Strategy 3: Use requests-html for JavaScript rendering (Lightweight alternative)"""
    try:
        from requests_html import HTMLSession
        
        session = HTMLSession()
        response = session.get(url, timeout=15)
        
        # Render JavaScript (this will download Chromium on first run)
        response.html.render(timeout=20, sleep=3)
        
        soup = BeautifulSoup(response.html.html, 'lxml')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            element.decompose()
        
        text = extract_article_text(soup, url)
        
        if text and len(text.strip()) > 100:
            return text
            
    except ImportError:
        pass  # requests-html not installed, skip
    except Exception as e:
        pass  # Silent fail
    
    return ""

def fetch_with_newspaper(url: str) -> str:
    """Strategy 4: Use newspaper3k with custom headers"""
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
    """Strategy 5: Use cloudscraper for Cloudflare-protected sites"""
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
    """Strategy 6: Use standard requests with comprehensive headers"""
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
    
    # Site-specific selectors (expanded with MSN)
    selectors_map = {
        'msn.com': [
            'article',
            '.article-body',
            'main article',
            '[data-t="article-body"]',
            '.articlebody',
            'main .content',
            'div[role="main"]',
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
    Prioritizes JavaScript rendering for dynamic sites.
    Returns article text or empty string on complete failure.
    """
    
    # Check if this is a known JavaScript-heavy site
    js_heavy_domains = ['msn.com', 'medium.com', 'forbes.com', 'bloomberg.com']
    domain = urlparse(url).netloc.lower()
    is_js_heavy = any(d in domain for d in js_heavy_domains)
    
    if is_js_heavy:
        # Try JavaScript rendering first for known dynamic sites
        strategies = [
            ("playwright", fetch_with_playwright),
            ("selenium", fetch_with_selenium),
            ("requests-html", fetch_with_requests_html),
            ("cloudscraper", fetch_with_cloudscraper),
            ("newspaper3k", fetch_with_newspaper),
            ("requests", fetch_with_requests),
        ]
    else:
        # Try faster methods first for static sites
        strategies = [
            ("requests", fetch_with_requests),
            ("cloudscraper", fetch_with_cloudscraper),
            ("newspaper3k", fetch_with_newspaper),
            ("playwright", fetch_with_playwright),
            ("selenium", fetch_with_selenium),
            ("requests-html", fetch_with_requests_html),
        ]
    
    for strategy_name, strategy_func in strategies:
        try:
            text = strategy_func(url)
            if text:
                print(f"   ✓ Fetched {len(text)} chars ({strategy_name})")
                return text
            else:
                time.sleep(0.5)  # Brief delay between strategies
        except Exception as e:
            print(f"   ⚠️ {strategy_name} error: {str(e)[:50]}")
            time.sleep(0.5)
    
    print(f"   ✗ All strategies failed")
    return ""