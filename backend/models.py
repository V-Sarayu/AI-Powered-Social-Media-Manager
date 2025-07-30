from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TrendingTopic(Base):
    __tablename__ = "trending_topics"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False)       # E.g. Instagram, YouTube
    keyword = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
