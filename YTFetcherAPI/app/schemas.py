from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class VideoOut(BaseModel):
    """Video output schema for API responses"""
    id: int = Field(description="Unique video ID")
    video_id: str = Field(description="YouTube video ID")
    title: str = Field(description="Video title")
    description: str = Field(description="Video description") 
    published_at: datetime = Field(description="Video publish date")
    thumbnail_url: str = Field(description="Video thumbnail URL")
    video_url: str = Field(description="YouTube video URL")
    
    class Config:
        orm_mode = True


class VideoSearchResponse(BaseModel):
    """Enhanced response for video searches with metadata"""
    videos: list[VideoOut] = Field(description="List of videos")
    total_count: int = Field(description="Total number of videos matching criteria")
    page: int = Field(description="Current page number")
    size: int = Field(description="Number of videos per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there are more pages")
    has_previous: bool = Field(description="Whether there are previous pages")


class VideoCountResponse(BaseModel):
    """Response for video count endpoint"""
    total_count: int = Field(description="Total number of videos matching the criteria")


class ConfigResponse(BaseModel):
    """Configuration information response"""
    search_query: str = Field(description="Current search query being used")
    fetch_interval: int = Field(description="Fetch interval in seconds")
    max_results: int = Field(description="Maximum results per fetch")
    api_keys_count: int = Field(description="Number of configured API keys")
    published_after: Optional[str] = Field(description="Last published_after timestamp")


class VideoSearchParams(BaseModel):
    """Search parameters for video queries"""
    search: Optional[str] = Field(None, description="Search keyword")
    published_after: Optional[datetime] = Field(None, description="Published after date")
    published_before: Optional[datetime] = Field(None, description="Published before date") 
    sort_by: str = Field("published_at", description="Sort field")
    sort_order: str = Field("desc", description="Sort order")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Page size")