from fastapi import APIRouter
from scraping import scrape_twitter_trends

router = APIRouter()

@router.get("/trends")
def get_trending_topics():
    trends = scrape_twitter_trends()
    return {"trending_topics": trends}
