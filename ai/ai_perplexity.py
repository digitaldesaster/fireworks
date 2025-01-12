import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://api.perplexity.ai/chat/completions"

payload = {
    "model": "llama-3.1-sonar-small-128k-online",
    "messages": [
        {
            "role": "system",
            "content": "Du bist ein hilfreicher Assistent"
        },
        {
            "role": "user",
            "content": "Wie hat der FC Bayern gestern gespielt?"
        }
    ],
    "top_k": 0,
    "stream": False
}
headers = {
    "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)