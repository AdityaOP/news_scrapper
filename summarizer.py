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

    prompt = f"""You are an expert analyst of digital health and health technology news in Australia.

Your task:
1. Read the article carefully
2. Think about what top question this article is answering
4. Write question in full, followed by a comprehensive 5-6 sentence answer

Format your response EXACTLY like this:

Question: [Write the full question here, e.g., "What new digital health initiative has been launched in Victoria?"]
Answer: [Provide a detailed 5-6 sentence answer that fully addresses this question. Include specific details, names, dates, and context from the article. Make sure the answer is comprehensive and self-contained.]

IMPORTANT RULES:
- Question must be a complete.
- Question should be tailored to what THIS article actually discusses
- Answers must be detailed and include specific information from the article
- Focus on the most newsworthy and important aspects
- If the article doesn't provide information for a typical question (e.g., "When"), skip it and choose a different question that the article DOES answer
- Do not add any extra text, summaries, or commentary beyond the one Q&A pairs

Article text:
{text}
"""

    try:
        chat = client.chat.completions.create(
            model="groq/compound",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )
        
        summary = chat.choices[0].message.content.strip()
        return summary if summary else "Summary not available - no response generated."
        
    except Exception as e:
        print(f"   ⚠️ Summarization error: {e}")
        return f"Summary not available - API error: {str(e)}"