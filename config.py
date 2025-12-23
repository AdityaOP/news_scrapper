import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SEARCH_QUERIES = [
    # Core digital health + AI
    "Australia digital health AI",
    "Australia digital health start-ups",
    "Australia healthtech artificial intelligence",
    "Australia medtech AI startup",
    
    # Specific events
    "Australia digital health funding",
    "Australia healthtech startup launch",
    "Australia medical AI pilot",
    
    # Policy & regulation
    "Australia digital health policy",
    "Australia health AI regulation",
]

MAX_RESULTS_PER_QUERY = 10

OUTPUT_FILE = "digital_health_news.docx"

TIME_FILTER = "d"  # 'd' = past day, 'w' = past week, 'm' = past month

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}