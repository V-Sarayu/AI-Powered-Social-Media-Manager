import requests
import json
import csv
import re

import sys
from backend.updated_company_rag import CompanyRAG  # Import the updated RAG system

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Retrieve the keys
APIFY_API_KEY = os.getenv("APIFY_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini model with your API key
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-2.0-flash-lite')

def scrape_instagram_hashtags(hashtags, results_limit=2):
    """
    Scrape hashtags from Instagram posts using Apify's Instagram Hashtag Scraper
    """
    payload = {
        "hashtags": hashtags,
        "resultsLimit": results_limit
    }

    url = f"https://api.apify.com/v2/acts/apify~instagram-hashtag-scraper/run-sync-get-dataset-items?token={APIFY_API_KEY}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            print("No Instagram data returned.")
            return []

        def find_hashtags(text):
            return set(re.findall(r"#\w+", text)) if text else set()

        extracted_hashtags = set()

        for post in data:
            extracted_hashtags.update(find_hashtags(post.get("caption", "")))
            extracted_hashtags.update(find_hashtags(post.get("firstComment", "")))

            for comment in post.get("latestComments", []):
                extracted_hashtags.update(find_hashtags(comment.get("text", "")))

        return sorted(list(extracted_hashtags))

    except requests.exceptions.RequestException as e:
        print(f"Error scraping Instagram hashtags: {e}")
        return []

def get_youtube_trending_reels(event_description):
    """
    Fetch trending YouTube Shorts based on the given event description.
    Extracts video titles, hashtags, and video URLs.
    """
    search_query = event_description + " trending shorts"
    base_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": search_query,
        "type": "video",
        "videoDuration": "short",
        "maxResults": 10,
        "key": YOUTUBE_API_KEY
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "items" not in data:
            print("No YouTube data returned or API error.")
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
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching YouTube trends: {e}")
        return []

def extract_youtube_hashtags(youtube_data):
    """
    Extract all hashtags from YouTube data
    """
    all_hashtags = []
    for item in youtube_data:
        all_hashtags.extend(item.get("hashtags", []))
    return list(set(all_hashtags))

def save_hashtags_to_csv(hashtags, filename="trending_hashtags.csv"):
    """
    Save hashtags to a CSV file
    """
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows([[ht] for ht in hashtags])
        print(f"Hashtags saved to {filename}")
        return filename
    except Exception as e:
        print(f"Error saving hashtags to CSV: {e}")
        return None

def setup_rag_system():
    """
    Set up or load the RAG system
    """
    rag = CompanyRAG()
    rag_file = "company_rag.pkl"
    json_file = "company_details.json"
    
    # Check for existing RAG system
    if os.path.exists(rag_file):
        print("Loading existing RAG system...")
        if rag.load_from_disk(rag_file):
            print("RAG system loaded successfully.")
        else:
            print("Failed to load existing RAG system.")
    
    # If no company info is loaded, try loading from JSON
    if not rag.company_info and os.path.exists(json_file):
        print(f"Loading company information from {json_file}...")
        if not rag.load_company_json(json_file):
            print(f"Failed to load company details from {json_file}.")
            
            # Ask if user wants to specify a different JSON path
            custom_path = input("Enter path to your company JSON file (or press Enter to skip): ").strip()
            if custom_path and not rag.load_company_json(custom_path):
                print("Failed to load company information. Please check your JSON file.")
                sys.exit(1)
    
    # If still no company info, alert the user
    if not rag.company_info:
        print("\nWARNING: No company information loaded.")
        print("Please create a company_details.json file before running this script.")
        print("See documentation for the required JSON format.")
        sys.exit(1)
        
    return rag

def main():
    print("=== JSON-based RAG Social Media Content Generator ===\n")
    
    # Set up or load RAG system
    rag = setup_rag_system()
    company_name = rag.company_info.get("name", "your organization")
    print(f"Loaded company information for: {company_name}")
    
    # Get user input for the project
    project_description = input(f"Describe the specific campaign or post you want to create for {company_name}: ")
    target_audience = input("Who is your target audience for this specific post? ")
    desired_tone = input("What tone would you like for this specific post? (e.g., funny, informative, serious): ")
    
    # Get input for Instagram scraping
    print("\n--- Instagram Trend Scraping ---")
    instagram_hashtags_input = input("Enter Instagram hashtags to search (comma-separated): ").strip()
    instagram_hashtags = [ht.strip() for ht in instagram_hashtags_input.split(",") if ht.strip()]
    
    # Collect trending data from both platforms
    print("\nCollecting trending data... Please wait.")
    
    # Scrape Instagram
    instagram_trending_hashtags = []
    if instagram_hashtags:
        instagram_trending_hashtags = scrape_instagram_hashtags(instagram_hashtags)
        print(f"Found {len(instagram_trending_hashtags)} trending hashtags from Instagram.")
    
    # Scrape YouTube
    youtube_trends = get_youtube_trending_reels(project_description)
    youtube_hashtags = extract_youtube_hashtags(youtube_trends)
    print(f"Found {len(youtube_trends)} trending videos and {len(youtube_hashtags)} hashtags from YouTube.")
    
    # Combine hashtags from both sources
    all_trending_hashtags = list(set(instagram_trending_hashtags + youtube_hashtags))
    
    # Save combined hashtags to CSV
    csv_filename = save_hashtags_to_csv(all_trending_hashtags)
    
    # Add trending hashtags to the RAG system
    if all_trending_hashtags:
        print("Adding trending hashtags to company knowledge base...")
        rag.add_trending_hashtags(all_trending_hashtags)
        rag.save_to_disk()  # Save the updated RAG system
    
    # Display some of the collected data
    print("\n--- Trending Information Summary ---")
    print(f"Total unique hashtags found: {len(all_trending_hashtags)}")
    if all_trending_hashtags:
        print("Sample hashtags: " + ", ".join(all_trending_hashtags[:5]))
    
    if youtube_trends:
        print("\nSample trending YouTube videos:")
        for i, video in enumerate(youtube_trends[:3]):
            print(f"{i+1}. {video['title']}")
            print(f"   URL: {video['video_url']}")
    
    # Generate content ideas with RAG
    print("\n--- Generating Content Ideas with Company Context ---")
    ideas = rag.generate_content(
        project_description=project_description, 
        target_audience=target_audience, 
        desired_tone=desired_tone
    )
    
    if ideas:
        print(f"\n=== Generated Marketing Ideas for {company_name} ===\n")
        print(ideas)
    else:
        print("\nFailed to generate marketing ideas. Please check your API keys and try again.")
    
    print("\nProcess completed.")

if __name__ == "__main__":
    main()