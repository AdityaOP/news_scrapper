from search import search_news
from article_fetcher import fetch_article_text
from summarizer import summarize
from storage import save_excel

def main():
    print("🔍 Searching for digitalhealth news in Australia...")
    results = search_news()

    data = []
    for i, item in enumerate(results, 1):
        print(f"[{i}/{len(results)}] {item['title']}")
        text = fetch_article_text(item["link"])
        summary = summarize(text)

        data.append({
            "Title": item["title"],
            "Summary": summary,
            "Link": item["link"],
            "Date": item["date"]
        })

    save_excel(data)

if __name__ == "__main__":
    main()