import asyncio

from fastapi import HTTPException
from google import genai

from config import settings

client = genai.Client(api_key=settings.GENAI_API_KEY)


async def genai_summarize(content: str, max_words: int) -> str:

    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty.")
    if max_words < 1:
        raise HTTPException(status_code=400, detail="max_words must be positive.")

    prompt = f"Summarize the following text: {content}. Make summary not longer than {max_words} words."

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=settings.GENAI_MODEL,
            contents=prompt,
        )
        return response.text.strip()

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to generate summary: {str(e)}"
        )
