from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def summarize(text: str) -> str:
    """
    Summarize article text using Groq API.
    Returns a concise summary or error message.
    """
    if not text or not text.strip():
        return "Summary not available - article text could not be extracted."

    # Truncate very long articles to avoid token limits
    max_chars = 8000
    if len(text) > max_chars:
        text = text[:max_chars] + "..."

    prompt = f"""Summarize the following article in 3-4 concise sentences.
Focus on digital health developments relevant to Australia.

Article text:
{text}
"""

    try:
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # More reliable model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        
        summary = chat.choices[0].message.content.strip()
        return summary if summary else "Summary not available - no response generated."
        
    except Exception as e:
        print(f"⚠️ Summarization error: {e}")
        return f"Summary not available - API error: {str(e)}"