
from search import search_news
from article_fetcher import fetch_article_text
from summarizer import summarize
from storage import save_doc
import time

def main():
    print("=" * 60)
    print("🔍 Digital Health News Aggregator")
    print("=" * 60)
    
    print("\n🔎 Searching for digital health news in Australia...")
    results = search_news()
    
    if not results:
        print("❌ No results found. Exiting.")
        return

    print(f"\n📰 Processing {len(results)} articles...\n")
    
    data = []
    successful = 0
    failed = 0
    
    for i, item in enumerate(results, 1):
        print(f"[{i}/{len(results)}] {item['title'][:60]}...")
        
        # Fetch article content
        text = fetch_article_text(item["link"])
        
        # Generate summary
        if text:
            print(f"   → Generating summary...")
            summary = summarize(text)
            
            # Check if summarization was successful
            if "not available" not in summary.lower():
                successful += 1
            else:
                failed += 1
        else:
            summary = "Summary not available - could not fetch article content."
            failed += 1

        data.append({
            "Title": item["title"],
            "Summary": summary,
            "Link": item["link"],
            "Date": item["date"]
        })
        
        # Small delay between articles
        time.sleep(1)
        print()

    # Save results
    print("=" * 60)
    print(f"✅ Successfully processed: {successful}")
    print(f"⚠️ Failed to process: {failed}")
    print("=" * 60)
    
    save_doc(data)

if __name__ == "__main__":
    main()