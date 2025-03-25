import requests
from bs4 import BeautifulSoup

def fetch_trending_hashtags():
    url = "https://best-hashtags.com/hashtag/trending/"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    hashtags = [tag.text for tag in soup.find_all("a", class_="trend-name")][:10]
    
    # Print hashtags in the terminal
    print("Trending Hashtags:", hashtags)

    return hashtags
