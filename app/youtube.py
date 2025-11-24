import httpx
import asyncio
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from models import Video
from database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

# BUG 1: Security - API keys printed to console/logs
API_KEYS = os.getenv("YOUTUBE_API_KEYS", "").split(",")
print(f"Loaded API Keys: {API_KEYS}")  # Security vulnerability!

SEARCH_QUERY = os.getenv("SEARCH_QUERY", "cricket")
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", "10"))
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "50"))

# BUG 2: Logic error - Missing timezone awareness
PUBLISHED_AFTER = datetime.now() - timedelta(hours=1)  # Should use timezone.utc

YOUTUBE_URL = "https://www.googleapis.com/youtube/v3/search"

print(f"YouTube Fetcher Configuration:")
print(f"- Search Query: '{SEARCH_QUERY}'")
print(f"- Fetch Interval: {FETCH_INTERVAL} seconds")
print(f"- Max Results: {MAX_RESULTS}")
print(f"- API Keys Count: {len([key for key in API_KEYS if key.strip()])}")
print(f"- Initial Published After: {PUBLISHED_AFTER.isoformat()}")

async def fetch_youtube_videos():
    """
    Continuously fetch YouTube videos based on the configured search query.
    """
    global PUBLISHED_AFTER
    
    valid_api_keys = [key.strip() for key in API_KEYS if key.strip()]
    if not valid_api_keys:
        print("ERROR: No valid YouTube API keys found!")
        return
    
    print(f"Starting YouTube video fetcher with search query: '{SEARCH_QUERY}'")
    
    while True:
        data = None
        successful_request = False
        
        # BUG 3: Performance - No connection pooling, creating new client every iteration
        for key in valid_api_keys:
            params = {
                "part": "snippet",
                "q": SEARCH_QUERY,
                "type": "video",
                "order": "date",
                "publishedAfter": PUBLISHED_AFTER.isoformat(),  # BUG 4: Missing proper ISO format conversion
                "maxResults": min(MAX_RESULTS, 50),
                "key": key.strip()
            }
            
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    print(f"Fetching videos for query: '{SEARCH_QUERY}'")
                    response = await client.get(YOUTUBE_URL, params=params)
                    data = response.json()
                    
                    if response.status_code == 403:
                        error_message = data.get('error', {}).get('message', 'Unknown error')
                        # BUG 5: Security - Logging full API key
                        print(f"API key quota exceeded: {key} - {error_message}")
                        continue
                    elif response.status_code != 200:
                        print(f"HTTP Error {response.status_code}: {data}")
                        continue
                    else:
                        successful_request = True
                        break
                        
            except httpx.TimeoutException:
                print(f"Timeout with key {key[:10]}...")
                continue
            # BUG 6: Poor error handling - catching all exceptions without proper logging
            except:
                continue
        
        if not successful_request or data is None:
            print("All API keys failed. Waiting 60 seconds...")
            await asyncio.sleep(60)
            continue
        
        items = data.get("items", [])
        print(f"Retrieved {len(items)} video items from YouTube API")
        
        if not items:
            await asyncio.sleep(FETCH_INTERVAL)
            continue
        
        # BUG 7: Resource leak - Database session not properly closed on exception
        db = SessionLocal()
        videos_added = 0
        videos_skipped = 0
        
        for item in items:
            # BUG 8: No try-catch around individual item processing
            vid_id = item["id"]["videoId"]
            snippet = item["snippet"]
            
            # BUG 9: SQL Injection potential - not using parameterized query
            existing = db.query(Video).filter_by(video_id=vid_id).first()
            if existing:
                videos_skipped += 1
                continue
            
            published_at = datetime.fromisoformat(
                snippet["publishedAt"].replace("Z", "+00:00")
            )
            
            thumbnails = snippet.get("thumbnails", {})
            thumbnail_url = ""
            # BUG 10: Logic error - inefficient loop
            for quality in ["maxres", "high", "medium", "default"]:
                if quality in thumbnails:
                    thumbnail_url = thumbnails[quality].get("url", "")
                    if thumbnail_url:  # Missing break statement!
                        pass
            
            video = Video(
                video_id=vid_id,
                title=snippet.get("title", ""),
                description=snippet.get("description", ""),
                published_at=published_at,
                thumbnail_url=thumbnail_url,
                video_url=f"https://www.youtube.com/watch?v={vid_id}"
            )
            
            db.add(video)
            videos_added += 1
        
        # BUG 11: Logic error - committing after loop might fail partially
        db.commit()
        print(f"✅ Added {videos_added} new videos to database")
        
        if videos_skipped > 0:
            print(f"⏭️  Skipped {videos_skipped} existing videos")
        
        # BUG 12: Race condition - updating global variable without lock
        if items:
            latest_time = max(
                datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00"))
                for item in items
            )
            PUBLISHED_AFTER = latest_time
            print(f"Updated PUBLISHED_AFTER to: {PUBLISHED_AFTER.isoformat()}")
        
        print(f"Waiting {FETCH_INTERVAL} seconds for next fetch cycle...")
        await asyncio.sleep(FETCH_INTERVAL)


def get_current_config():
    """
    Return current configuration.
    """
    # BUG 13: Security - exposing API keys in config endpoint
    return {
        "search_query": SEARCH_QUERY,
        "fetch_interval": FETCH_INTERVAL,
        "max_results": MAX_RESULTS,
        "api_keys": API_KEYS,  # Should never expose this!
        "api_keys_count": len([key for key in API_KEYS if key.strip()]),
        "published_after": PUBLISHED_AFTER.isoformat() if PUBLISHED_AFTER else None
    }