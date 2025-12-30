import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SEARCH_QUERIES = [
    "Australia digital health AI",
    "Australia digital health startup funding",
    "Australia hospital digital transformation health",
    "Australia telehealth technology platform",
    "Australia medical AI clinical decision support",
    "Australia health data analytics platform",
    "Australia medtech digital diagnostics",
    "Australia digital health policy regulation",
    "Australia digital health research clinical trial",
    "Australia population health digital platform",
    ]

MAX_RESULTS_PER_QUERY = 15

OUTPUT_FILE = "digital_health_news.docx"

TIME_FILTER = "d"  # 'd' = past day, 'w' = past week, 'm' = past month

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}