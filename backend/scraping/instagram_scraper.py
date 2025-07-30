import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("APIFY_API_KEY")

def scrape_instagram(hashtags):
    if not hashtags:
        return []
    payload = {"hashtags": hashtags, "resultsLimit": 2}
    url = f"https://api.apify.com/v2/acts/apify~instagram-hashtag-scraper/run-sync-get-dataset-items?token={API_KEY}"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        def find_hashtags(text):
            return set(re.findall(r"#\w+", text)) if text else set()
        extracted = set()
        for post in data:
            extracted |= find_hashtags(post.get("caption", ""))
            extracted |= find_hashtags(post.get("firstComment", ""))
            for c in post.get("latestComments", []):
                extracted |= find_hashtags(c.get("text", ""))
        return sorted(extracted)
    except Exception as e:
        print(f"Instagram scraper error: {e}")
        return []
