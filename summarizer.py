from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def summarize(text: str) -> str:
    """
    Summarize article text using Groq API with structured format.
    Returns a formatted summary with clear answers to WHO/WHAT/WHERE/WHEN/WHY/HOW.
    """
    if not text or not text.strip():
        return "Summary not available - article text could not be extracted."

    # Truncate very long articles to avoid token limits
    max_chars = 8000
    if len(text) > max_chars:
        text = text[:max_chars] + "..."

    prompt = f"""You are an expert analyst of digital health and health technology news.

Your task:
Summarize the key points of this article in 3-4 concise bullet points focusing on the health news.

Format your response EXACTLY like this:

- [First key point - one clear sentence]
- [Second key point - one clear sentence]
- [Third key point - one clear sentence]
- [Fourth key point if needed - one clear sentence]

At the end also add a catchy sentence to interest the reader.

IMPORTANT RULES:
- Use exactly 3-4 bullet points (use • symbol)
- Each bullet point should be complete sentences of similar context
- Focus on the most important facts: who, what, where, when, why, how, outcomes
- Avoid vague language - be specific and factual
- Include specific details like names, organizations, dates, numbers
- Be concise but informative
- Do not add any extra text, headers, or commentary

Article text:
{text}
"""

    try:
        chat = client.chat.completions.create(
            model="groq/compound-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )
        
        summary = chat.choices[0].message.content.strip()
        return summary if summary else "Summary not available - no response generated."
        
    except Exception as e:
        print(f"   ⚠️ Summarization error: {e}")
        return f"Summary not available - API error: {str(e)}"