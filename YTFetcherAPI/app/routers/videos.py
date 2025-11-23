from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime
import schemas, models, database

router = APIRouter()

@router.get("/videos", response_model=List[schemas.VideoOut])
def get_videos(
    # Pagination
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    size: int = Query(10, ge=1, le=100, description="Number of videos per page (max 100)"),
    
    # Search
    search: Optional[str] = Query(None, description="Search keyword in title or description"),
    
    # Date filtering
    published_after: Optional[datetime] = Query(None, description="Filter videos published after this date (ISO format)"),
    published_before: Optional[datetime] = Query(None, description="Filter videos published before this date (ISO format)"),
    
    # Sorting
    sort_by: str = Query("published_at", regex="^(published_at|title)$", description="Sort by field: published_at or title"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order: asc or desc"),
    
    db: Session = Depends(database.get_db)
):
    """
    Get videos with enhanced filtering, searching, and sorting capabilities.
    
    - **page**: Page number (starts from 1)
    - **size**: Number of videos per page (1-100)
    - **search**: Search keyword in video title or description
    - **published_after**: Filter videos published after this date
    - **published_before**: Filter videos published before this date  
    - **sort_by**: Sort by 'published_at' or 'title'
    - **sort_order**: Sort order 'asc' or 'desc'
    """
    
    # Start with base query
    query = db.query(models.Video)
    
    # Apply search filter
    if search:
        search_filter = or_(
            models.Video.title.ilike(f"%{search}%"),
            models.Video.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Apply date range filters
    date_filters = []
    if published_after:
        date_filters.append(models.Video.published_at >= published_after)
    if published_before:
        date_filters.append(models.Video.published_at <= published_before)
    
    if date_filters:
        query = query.filter(and_(*date_filters))
    
    # Apply sorting
    if sort_by == "published_at":
        sort_column = models.Video.published_at
    else:  # sorting by "title"
        sort_column = models.Video.title
    
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:  # sorting by sort_order = "asc"
        query = query.order_by(sort_column.asc())
    
    # Applying pagination
    skip = (page - 1) * size
    videos = query.offset(skip).limit(size).all()
    
    return videos


@router.get("/videos/search", response_model=List[schemas.VideoOut])
def search_videos(
    q: str = Query(..., min_length=1, description="Search query (required)"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("published_at", regex="^(published_at|title)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(database.get_db)
):
    
    # Searches in both title and description
    search_filter = or_(
        models.Video.title.ilike(f"%{q}%"),
        models.Video.description.ilike(f"%{q}%")
    )
    
    query = db.query(models.Video).filter(search_filter)
    

    if sort_by == "published_at":
        sort_column = models.Video.published_at
    else:
        sort_column = models.Video.title
    
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    

    skip = (page - 1) * size
    videos = query.offset(skip).limit(size).all()
    
    return videos


@router.get("/videos/count")
def get_videos_count(
    search: Optional[str] = Query(None, description="Search keyword in title or description"),
    published_after: Optional[datetime] = Query(None, description="Filter videos published after this date"),
    published_before: Optional[datetime] = Query(None, description="Filter videos published before this date"),
    db: Session = Depends(database.get_db)
):
    """
    Get the total count of videos matching the filters.
    Useful for pagination calculations.
    """
    
    query = db.query(models.Video)
    
    # Applying search filter
    if search:
        search_filter = or_(
            models.Video.title.ilike(f"%{search}%"),
            models.Video.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Applying date range filters
    date_filters = []
    if published_after:
        date_filters.append(models.Video.published_at >= published_after)
    if published_before:
        date_filters.append(models.Video.published_at <= published_before)
    
    if date_filters:
        query = query.filter(and_(*date_filters))
    
    total_count = query.count()
    
    return {"total_count": total_count}