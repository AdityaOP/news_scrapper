import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

QUERY = (
    "Australia (\"digital health\" OR healthtech OR medtech) "
    "AND (AI OR \"artificial intelligence\") "
    "AND (startup OR funding OR grant OR pilot OR launch) "
    "news"
)
MAX_RESULTS = 10
OUTPUT_FILE = "digital_health_news.docx"

TIME_FILTER = None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}