import httpx
import asyncio
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from models import Video
from database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

API_KEYS = os.getenv("YOUTUBE_API_KEYS", "").split(",")
SEARCH_QUERY = os.getenv("SEARCH_QUERY", "cricket")
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", "10"))
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "50"))

# Initialized published_after to 1 hour ago in UTC
PUBLISHED_AFTER = datetime.now(timezone.utc) - timedelta(hours=1)

YOUTUBE_URL = "https://www.googleapis.com/youtube/v3/search"

# config for debugging ease
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
        print("ERROR: No valid YouTube API keys found! Please check YOUTUBE_API_KEYS in .env file")
        return
    
    print(f"Starting YouTube video fetcher with search query: '{SEARCH_QUERY}'")
    
    while True:
        data = None
        successful_request = False
        
        for key in valid_api_keys:
            params = {
                "part": "snippet",
                "q": SEARCH_QUERY,
                "type": "video",
                "order": "date",
                "publishedAfter": PUBLISHED_AFTER.isoformat(timespec="seconds").replace("+00:00", "Z"),
                "maxResults": min(MAX_RESULTS, 50),
                "key": key.strip()
            }
            
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    print(f"Fetching videos for query: '{SEARCH_QUERY}' after {PUBLISHED_AFTER.isoformat()}")
                    response = await client.get(YOUTUBE_URL, params=params)
                    data = response.json()
                    
                    if response.status_code == 403:
                        error_message = data.get('error', {}).get('message', 'Unknown error')
                        print(f"API key quota exceeded: {key[:10]}... - {error_message}")
                        continue
                    elif response.status_code == 400:
                        error_message = data.get('error', {}).get('message', 'Bad request')
                        print(f"Bad request with key {key[:10]}...: {error_message}")
                        continue
                    elif response.status_code != 200:
                        print(f"HTTP Error {response.status_code}: {data}")
                        continue
                    elif "error" in data:
                        print(f"YouTube API Error: {data['error']}")
                        continue
                    else:
                        successful_request = True
                        print(f"Successfully fetched data using API key: {key[:10]}...")
                        break
                        
            except httpx.TimeoutException:
                print(f"Timeout with key {key[:10]}...")
                continue
            except Exception as e:
                print(f"HTTP Exception with key {key[:10]}...: {e}")
                continue
        
        if not successful_request or data is None:
            print("All API keys failed. Waiting 60 seconds before retry...")
            await asyncio.sleep(60)
            continue
        
        items = data.get("items", [])
        print(f"Retrieved {len(items)} video items from YouTube API")
        
        if not items:
            print("No new videos found. Waiting for next fetch cycle...")
            await asyncio.sleep(FETCH_INTERVAL)
            continue
        
        
        db: Session = SessionLocal()
        try:
            videos_added = 0
            videos_skipped = 0
            
            for item in items:
                try:
                    vid_id = item["id"]["videoId"]
                    snippet = item["snippet"]
                    
            
                    if db.query(Video).filter_by(video_id=vid_id).first():
                        videos_skipped += 1
                        continue
                    
            
                    published_at = datetime.fromisoformat(
                        snippet["publishedAt"].replace("Z", "+00:00")
                    )
                    
            
                    thumbnails = snippet.get("thumbnails", {})
                    thumbnail_url = ""
                    for quality in ["maxres", "high", "medium", "default"]:
                        if quality in thumbnails:
                            thumbnail_url = thumbnails[quality].get("url", "")
                            break
                    
                    # Create video record
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
                    
                except KeyError as e:
                    print(f"Missing key in video data: {e}")
                    continue
                except ValueError as e:
                    print(f"Error parsing video data: {e}")
                    continue
                except Exception as e:
                    print(f"Error processing video: {e}")
                    continue
            
    
            if videos_added > 0:
                db.commit()
                print(f"✅ Added {videos_added} new videos to database")
            
            if videos_skipped > 0:
                print(f"⏭️  Skipped {videos_skipped} existing videos")
                
        except Exception as e:
            print(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()
        

        if items:
            try:
                latest_time = max(
                    datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00"))
                    for item in items
                )
                PUBLISHED_AFTER = latest_time
                print(f"Updated PUBLISHED_AFTER to: {PUBLISHED_AFTER.isoformat()}")
            except Exception as e:
                print(f"Error updating PUBLISHED_AFTER: {e}")
        

        print(f"Waiting {FETCH_INTERVAL} seconds for next fetch cycle...")
        await asyncio.sleep(FETCH_INTERVAL)


def get_current_config():
    """
    Return current configuration for debugging purposes.
    """
    return {
        "search_query": SEARCH_QUERY,
        "fetch_interval": FETCH_INTERVAL,
        "max_results": MAX_RESULTS,
        "api_keys_count": len([key for key in API_KEYS if key.strip()]),
        "published_after": PUBLISHED_AFTER.isoformat() if PUBLISHED_AFTER else None
    }