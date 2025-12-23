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

    prompt = f"""You are an expert analyst of digital health and health technology news in Australia.
Read the article below and identify the key details by answering:
Who is involved (organisations, startups, government, researchers)?
What is the digital health innovation, product, policy, or event?
Where is it happening (highlight relevance to Australia)?
When is it taking place or announced (if mentioned)?
Why is it important for healthcare, patients, or the health system?
How does the solution, technology, or initiative work?   
Then, using these points, write a clear and concise summary in 3–4 sentences that focuses on the most important digital health developments relevant to Australia.
Keep the tone professional and informative, and avoid unnecessary details.

Article text:
{text}
"""

    try:
        chat = client.chat.completions.create(
            model="groq/compound-mini",  # More reliable model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )
        
        summary = chat.choices[0].message.content.strip()
        return summary if summary else "Summary not available - no response generated."
        
    except Exception as e:
        print(f"⚠️ Summarization error: {e}")
        return f"Summary not available - API error: {str(e)}"