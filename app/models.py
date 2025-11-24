from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base

class Video(Base):
    __tablename__ = "videos"

    # BUG 51: No autoincrement specification (can cause issues in some databases)
    id = Column(Integer, primary_key=True, index=True)
    
    # BUG 52: video_id should have a length constraint
    video_id = Column(String, unique=True, index=True)
    
    # BUG 53: No length limit on title - can cause issues
    title = Column(String)
    
    # BUG 54: Text field without index - slow searches
    description = Column(Text)
    
    # BUG 55: Missing nullable=False constraints where appropriate
    published_at = Column(DateTime, index=True)
    
    # BUG 56: No validation for URL format
    thumbnail_url = Column(String)
    
    # BUG 57: No length constraint on URL field
    video_url = Column(String)
    
    # BUG 58: Missing created_at/updated_at timestamps
    # BUG 59: No soft delete support (deleted_at field)
    # BUG 60: Missing __repr__ method for debugging
    # BUG 61: No composite index on (published_at, video_id) for common queries
    # BUG 62: Missing channel_id field (useful for filtering)
    # BUG 63: No view_count or engagement metrics
    # BUG 64: Missing table constraints (CHECK constraints)
    # BUG 65: No relationship definitions if extending to other tables