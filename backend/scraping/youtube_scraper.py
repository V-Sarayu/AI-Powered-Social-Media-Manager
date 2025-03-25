import requests
import json

# Load API key from environment variable or config file
API_KEY = "API_KEY"

BASE_URL = "https://www.googleapis.com/youtube/v3/search"

def get_trending_reels(event_description):
    """
    Fetch trending YouTube Shorts based on the given event description.
    Extracts video titles, hashtags, and music IDs.
    """
    search_query = event_description + " trending shorts"
    params = {
        "part": "snippet",
        "q": search_query,
        "type": "video",
        "videoDuration": "short",
        "maxResults": 10,
        "key": API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if "items" not in data:
        return {"error": "Failed to fetch data. Check API key or quota."}
    
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

# Example usage
event_description = "Entrepreneurship event"
youtube_trends = get_trending_reels(event_description)
print(json.dumps(youtube_trends, indent=2))
