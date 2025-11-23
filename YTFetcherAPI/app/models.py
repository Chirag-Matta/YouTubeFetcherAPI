from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text)
    published_at = Column(DateTime, index=True)
    thumbnail_url = Column(String)
    video_url = Column(String) 
