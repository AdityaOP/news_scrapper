"""
Test script to debug MSN article scraping
Run this to see what's happening with MSN pages
"""

import sys

def test_playwright():
    """Test if Playwright is installed and working"""
    print("\n" + "="*60)
    print("Testing Playwright...")
    print("="*60)
    try:
        from playwright.sync_api import sync_playwright
        
        test_url = "https://www.msn.com/en-au/news/australia/test"
        
        with sync_playwright() as p:
            print("✓ Playwright imported successfully")
            browser = p.chromium.launch(headless=True)
            print("✓ Browser launched")
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            print("✓ Page created")
            
            # Try loading MSN homepage
            page.goto("https://www.msn.com/en-au", wait_until='networkidle', timeout=30000)
            print("✓ Page loaded")
            
            # Wait for content
            page.wait_for_timeout(3000)
            print("✓ Wait completed")
            
            content = page.content()
            browser.close()
            
            print(f"✓ Got {len(content)} characters of HTML")
            print(f"✓ Playwright is WORKING!")
            return True
            
    except ImportError:
        print("✗ Playwright is NOT installed")
        print("  Install with: pip install playwright")
        print("  Then run: playwright install chromium")
        return False
    except Exception as e:
        print(f"✗ Playwright error: {e}")
        return False

def test_selenium():
    """Test if Selenium is installed and working"""
    print("\n" + "="*60)
    print("Testing Selenium...")
    print("="*60)
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("✓ Selenium imported successfully")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        print("✓ ChromeDriver ready")
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✓ Browser launched")
        
        driver.get("https://www.msn.com/en-au")
        print("✓ Page loaded")
        
        import time
        time.sleep(3)
        
        content = driver.page_source
        driver.quit()
        
        print(f"✓ Got {len(content)} characters of HTML")
        print(f"✓ Selenium is WORKING!")
        return True
        
    except ImportError:
        print("✗ Selenium is NOT installed")
        print("  Install with: pip install selenium webdriver-manager")
        return False
    except Exception as e:
        print(f"✗ Selenium error: {e}")
        return False

def test_msn_scrape_with_playwright(url):
    """Test scraping a specific MSN URL with detailed output"""
    print("\n" + "="*60)
    print(f"Testing MSN URL: {url[:80]}...")
    print("="*60)
    
    try:
        from playwright.sync_api import sync_playwright
        from bs4 import BeautifulSoup
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            print("⏳ Loading page...")
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            print("⏳ Waiting for dynamic content (5 seconds)...")
            page.wait_for_timeout(5000)
            
            content = page.content()
            browser.close()
            
            print(f"✓ Got {len(content)} characters of HTML")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'lxml')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
                element.decompose()
            
            # Try to find article content
            print("\n🔍 Looking for article content...")
            
            # Check for article tag
            articles = soup.find_all('article')
            print(f"  Found {len(articles)} <article> tags")
            
            # Check for common MSN selectors
            selectors = [
                'article',
                '.article-body',
                'main article',
                '[data-t="article-body"]',
                '.articlebody',
                'main .content',
                'div[role="main"]',
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"  ✓ Found content with selector: {selector}")
                    text = '\n\n'.join([el.get_text(strip=True, separator=' ') for el in elements])
                    print(f"  📝 Text length: {len(text)} characters")
                    
                    if len(text) > 200:
                        print(f"\n✅ SUCCESS! Found article content!")
                        print(f"\nFirst 500 characters:")
                        print("-" * 60)
                        print(text[:500])
                        print("-" * 60)
                        return True
            
            # If no specific selector worked, try all paragraphs
            paragraphs = soup.find_all('p')
            print(f"\n  Found {len(paragraphs)} <p> tags total")
            
            if paragraphs:
                all_text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
                print(f"  📝 Combined paragraph text: {len(all_text)} characters")
                
                if len(all_text) > 200:
                    print(f"\n✅ SUCCESS! Found content from paragraphs!")
                    print(f"\nFirst 500 characters:")
                    print("-" * 60)
                    print(all_text[:500])
                    print("-" * 60)
                    return True
            
            print("\n❌ Could not find substantial article content")
            print("\nPage title:")
            title = soup.find('title')
            if title:
                print(f"  {title.get_text()}")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("MSN SCRAPER DIAGNOSTIC TOOL")
    print("="*60)
    
    # Test if tools are installed
    playwright_ok = test_playwright()
    selenium_ok = test_selenium()
    
    if not playwright_ok and not selenium_ok:
        print("\n❌ PROBLEM: Neither Playwright nor Selenium is working!")
        print("\nTo fix, run:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)
    
    # Test with a real MSN article URL
    print("\n" + "="*60)
    print("Now test with a real MSN article URL")
    print("="*60)
    
    test_url = input("\nPaste an MSN article URL (or press Enter to skip): ").strip()
    
    if test_url:
        if playwright_ok:
            test_msn_scrape_with_playwright(test_url)
        else:
            print("\nPlaywright not available, skipping URL test")
    
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)
    
    if playwright_ok or selenium_ok:
        print("\n✅ At least one scraping tool is working!")
        print("   Your main.py should be able to scrape MSN articles.")
        print("\nIf MSN scraping still fails in main.py:")
        print("  1. Check if the MSN URLs are valid")
        print("  2. Try increasing wait time in article_fetcher.py")
        print("  3. Run this test with a specific failing URL")
    else:
        print("\n❌ No scraping tools are working!")
        print("   Install Playwright or Selenium first.")

if __name__ == "__main__":
    main()