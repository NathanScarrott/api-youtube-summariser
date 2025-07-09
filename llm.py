from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key= os.getenv("OPENROUTER_API_KEY"),
)

def model_request(prompt, model = "openai/gpt-4o"):
    completion = client.chat.completions.create(
  model=model,
  messages=[
    {
      "role": "user",
      "content": prompt,
      "temperature": 0.5
    }
  ]
)

    return completion.choices[0].message.content