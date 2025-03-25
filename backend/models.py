from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TrendingTopic(Base):
    __tablename__ = "trending_topics"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False)  # e.g., Twitter, Instagram
    keyword = Column(String, nullable=False)  # Trending topic or hashtag
    timestamp = Column(DateTime, default=datetime.utcnow)
