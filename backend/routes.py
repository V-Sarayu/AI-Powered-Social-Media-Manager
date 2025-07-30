from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import TrendingTopic
from backend.scraping import fetch_trending_hashtags  # Optional generic scraper

router = APIRouter()

@router.get("/trends")
def get_trending_topics(db: Session = Depends(get_db)):
    topics = db.query(TrendingTopic).order_by(TrendingTopic.timestamp.desc()).limit(10).all()
    return {"trending_topics": [t.keyword for t in topics]}

@router.post("/scrape-and-save")
def scrape_and_save(db: Session = Depends(get_db)):
    hashtags = fetch_trending_hashtags()
    for tag in hashtags:
        db.add(TrendingTopic(platform="Instagram", keyword=tag))
    db.commit()
    return {"saved": hashtags}
