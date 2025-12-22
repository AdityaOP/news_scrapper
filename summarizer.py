from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def summarize(text: str) -> str:
    if not text.strip():
        return "Summary not available."

    prompt = f"""
Summarise the following article in 3–4 concise sentences.
Focus on digital health developments relevant to Australia.
"""

    chat = client.chat.completions.create(
        model="groq/compound",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return chat.choices[0].message.content.strip()