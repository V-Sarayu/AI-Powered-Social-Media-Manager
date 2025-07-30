import requests
import json
import csv
import re
from google.generativeai import configure, GenerativeModel

# ============ CONFIGURATION ============
APIFY_API_KEY = "apify_api_mQCU1Mjo4xuKfAnxMztvno9jlrioMY2rDCM3"
YOUTUBE_API_KEY = "AIzaSyADfIZVEuyhFU0xLLicljKaVaEKughockw"
GEMINI_API_KEY = "AIzaSyAIACDvQEIh_5RxM6H7FZgVhfvZUlAXJaA"
configure(api_key=GEMINI_API_KEY)

# ============ GET INPUT ============
event_description = input("Enter event description: ").strip()
hashtags_input = input("Enter topics for Instagram scraping (comma-separated): ").strip()
hashtags = [ht.strip() for ht in hashtags_input.split(",") if ht.strip()]

# ============ SCRAPE INSTAGRAM ============
def scrape_instagram(hashtags):
    print("\nScraping Instagram...")
    if not hashtags:
        return []

    payload = {
        "hashtags": hashtags,
        "resultsLimit": 2
    }
    url = f"https://api.apify.com/v2/acts/apify~instagram-hashtag-scraper/run-sync-get-dataset-items?token={APIFY_API_KEY}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        def find_hashtags(text):
            return set(re.findall(r"#\w+", text)) if text else set()

        extracted_hashtags = set()
        for post in data:
            extracted_hashtags.update(find_hashtags(post.get("caption", "")))
            extracted_hashtags.update(find_hashtags(post.get("firstComment", "")))
            for comment in post.get("latestComments", []):
                extracted_hashtags.update(find_hashtags(comment.get("text", "")))

        return sorted(extracted_hashtags)

    except Exception as e:
        print(f"Instagram scraping failed: {e}")
        return []

# ============ SCRAPE YOUTUBE ============
def scrape_youtube(event_description):
    print("Scraping YouTube Shorts...")
    BASE_URL = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": event_description + " trending shorts",
        "type": "video",
        "videoDuration": "short",
        "maxResults": 10,
        "key": YOUTUBE_API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if "items" not in data:
            return []

        trending_ideas = []
        for item in data["items"]:
            title = item["snippet"]["title"]
            description = item["snippet"].get("description", "")
            video_id = item["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            hashtags = [word for word in description.split() if word.startswith("#")]

            trending_ideas.append({
                "title": title,
                "hashtags": hashtags,
                "video_url": video_url
            })

        return trending_ideas

    except Exception as e:
        print(f"YouTube scraping failed: {e}")
        return []

# ============ RUN SCRAPERS ============
instagram_hashtags = scrape_instagram(hashtags)
youtube_trends = scrape_youtube(event_description)

if not instagram_hashtags and not youtube_trends:
    print("No data scraped. Skipping LLM generation.")
    exit()

# ============ GENERATE CONTENT USING GEMINI ============
def generate_social_media_content(event, insta_tags, yt_trends):
    prompt = f"""
You are a social media content strategist.

Event Description: {event}

Trending Instagram Hashtags: {', '.join(insta_tags)}

YouTube Shorts Trends:
{json.dumps(yt_trends, indent=2)}

Based on the above, generate:
1. Three poster content ideas.
2. Two trending reel content ideas with themes.
3. Three suggested audio tracks (describe mood and theme).
4. Combine Instagram & YouTube hashtags into one set.
"""

    model = GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    return response.text

# ============ DISPLAY GENERATED CONTENT ============
print("\nGenerating with Gemini...")
content = generate_social_media_content(event_description, instagram_hashtags, youtube_trends)
print("\n🎯 Generated Content:\n")
print(content)
