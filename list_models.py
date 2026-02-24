from google import genai
import os
from decouple import config

api_key = config('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

print("Available models:")
for model in client.models.list():
    print(f"- {model.name}")
