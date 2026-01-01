import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SEARCH_QUERIES = [
    "Digital health AI",
    "Digital health startup funding",
    "Hospital digital transformation health",
    "Telehealth technology platform",
    "Digital health AI clinical decision support",
    "Digital health data analytics platform",
    "Digital health medtech digital diagnostics",
    "Digital health policy regulation",
    "Digital health research clinical trial",
    "Digital health population health digital platform",
    "Digital health wearable technology",
    "Digital health remote patient monitoring",
    ]

MAX_RESULTS_PER_QUERY = 15

OUTPUT_FILE = "digital_health_news.docx"

TIME_FILTER = "d"  # 'd' = past day, 'w' = past week, 'm' = past month

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}