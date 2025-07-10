import os
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def model_request(prompt: str, model: str = "openai/gpt-4o", temperature: float = 0.5) -> Optional[str]:
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling AI model: {e}")
        return None
