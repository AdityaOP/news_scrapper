# 🏥 Digital Health News Aggregator

An automated news aggregation tool that searches, fetches, and summarizes digital health news from Australia, with a focus on AI developments.

## 📋 Features

- **Multi-source news search**: Combines Google News RSS and DuckDuckGo
- **Multiple search queries**: Covers various aspects of digital health and AI
- **Intelligent article extraction**: Uses multiple fallback strategies to fetch article content
- **AI-powered summarization**: Generates concise summaries using Groq's LLM API
- **Word document output**: Creates formatted reports with timestamped filenames
- **Duplicate detection**: Automatically removes duplicate articles across searches
- **Date filtering**: Configurable time filters for recent news

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API key (free tier available at [console.groq.com](https://console.groq.com))

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd digital-health-news-aggregator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Usage

Run the aggregator:
```bash
python main.py
```

The script will:
1. Search for news articles using multiple queries
2. Fetch the full article content
3. Generate AI summaries for each article
4. Save results to a Word document with timestamp

Output file format: `digital_health_news_YYYYMMDD_HHMMSS.docx`

## 📁 Project Structure

```
.
├── main.py              # Main orchestration script
├── search.py            # Multi-source news search functionality
├── article_fetcher.py   # Article content extraction with fallbacks
├── summarizer.py        # AI-powered summarization
├── storage.py           # Word document generation
├── config.py            # Configuration and search queries
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in repo)
└── .gitignore          # Git ignore rules
```

## ⚙️ Configuration

Edit `config.py` to customize:

### Search Queries
Add or modify search terms in the `SEARCH_QUERIES` list:
```python
SEARCH_QUERIES = [
    "Australia digital health AI",
    "Australia healthtech artificial intelligence",
    # Add your own queries
]
```

### Time Filter
Set how far back to search:
```python
TIME_FILTER = "3d"  # Options: "d" (day), "w" (week), "m" (month), None (all)
```

### Results Limit
```python
MAX_RESULTS_PER_QUERY = 10  # Articles per search query
```

## 🛠️ How It Works

### 1. Multi-Source Search
The tool searches both Google News RSS and DuckDuckGo:
- Runs multiple targeted queries
- Deduplicates results by URL
- Filters by date range
- Sorts by recency

### 2. Intelligent Article Fetching
Uses a three-strategy approach with fallbacks:
1. **Standard requests** with comprehensive headers
2. **Cloudscraper** for Cloudflare-protected sites
3. **Newspaper3k** as final fallback

Includes site-specific selectors for major news outlets:
- ABC News Australia
- SMH, The Age
- News.com.au
- And more...

### 3. AI Summarization
- Uses Groq's Llama 3.3 70B model
- Generates 3-4 sentence summaries
- Focuses on Australian digital health relevance
- Handles API errors gracefully

### 4. Document Generation
Creates formatted Word documents with:
- Title and timestamp header
- Numbered articles with sections
- Bold field labels
- Clickable URLs

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP requests |
| `beautifulsoup4` | HTML parsing |
| `newspaper3k` | Article extraction |
| `cloudscraper` | Cloudflare bypass |
| `duckduckgo_search` | DuckDuckGo news API |
| `groq` | AI summarization |
| `python-docx` | Word document generation |
| `python-dotenv` | Environment variable management |
| `lxml` | HTML/XML processing |
| `feedparser` | RSS feed parsing |

## 🔒 Privacy & Ethics

- Respects robots.txt and rate limits
- Uses reasonable delays between requests
- Only fetches publicly available news
- Properly attributes sources in output

## 🐛 Troubleshooting

**No articles fetched:**
- Check your internet connection
- Verify search queries are relevant
- Try adjusting `TIME_FILTER` to a longer period

**Summarization errors:**
- Verify your Groq API key in `.env`
- Check API rate limits at console.groq.com
- Ensure you have API credits remaining

**Import errors:**
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`
- Try creating a fresh virtual environment

## 📝 Output Format

Each article in the generated Word document includes:
- **Title**: Original article headline
- **Summary**: AI-generated 3-4 sentence summary
- **Link**: Original article URL
- **Date**: Publication date

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional news sources
- Better article extraction for specific sites
- Enhanced summarization prompts
- Improving article fetching
- Export to additional formats (PDF, HTML, Markdown)

## 📄 License

This project is open source and available under the MIT License.


---

**Note**: This tool is for informational purposes. Always verify critical information from original sources.