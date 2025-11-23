from fastapi import FastAPI
from database import engine, Base
from routers import videos
from youtube import fetch_youtube_videos
import asyncio

app = FastAPI()

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fetch_youtube_videos())

app.include_router(videos.router)