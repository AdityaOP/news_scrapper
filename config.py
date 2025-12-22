import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

QUERY = "digital health Australia news related to AI"
MAX_RESULTS = 10
OUTPUT_FILE = "digital_health_news.docx"

TIME_FILTER = None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}