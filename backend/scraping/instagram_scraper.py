import requests
import json
import csv
import re

API_KEY = "YOUR_APIFY_API_KEY" 

hashtags_input = input("Enter topics (comma-separated): ").strip()
hashtags = [ht.strip() for ht in hashtags_input.split(",") if ht.strip()]

if not hashtags:
    exit()

payload = {
    "hashtags": hashtags,
    "resultsLimit": 2
}

url = f"https://api.apify.com/v2/acts/apify~instagram-hashtag-scraper/run-sync-get-dataset-items?token={API_KEY}"
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    if not data:
        exit()

    def find_hashtags(text):
        return set(re.findall(r"#\w+", text)) if text else set()

    extracted_hashtags = set()

    for post in data:
        extracted_hashtags.update(find_hashtags(post.get("caption", "")))
        extracted_hashtags.update(find_hashtags(post.get("firstComment", "")))

        for comment in post.get("latestComments", []):
            extracted_hashtags.update(find_hashtags(comment.get("text", "")))

    extracted_hashtags = sorted(extracted_hashtags)

    if extracted_hashtags:
        with open("hashtags.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows([[ht] for ht in extracted_hashtags])

except requests.exceptions.RequestException:
    exit()