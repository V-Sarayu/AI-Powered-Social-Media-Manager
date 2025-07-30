import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_trending_reels(event_description):
    search_query = event_description + " trending shorts"
    params = {
        "part": "snippet",
        "q": search_query,
        "type": "video",
        "videoDuration": "short",
        "maxResults": 10,
        "key": API_KEY
    }
    try:
        response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
        data = response.json()
        if "items" not in data:
            return []
        trending_ideas = []
        for item in data["items"]:
            title = item["snippet"]["title"]
            description = item["snippet"].get("description", "")
            video_id = item["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            hashtags = [w for w in description.split() if w.startswith("#")]
            trending_ideas.append({
                "title": title,
                "hashtags": hashtags,
                "video_url": video_url
            })
        return trending_ideas
    except Exception as e:
        print(f"YouTube scraper error: {e}")
        return []
