# YouTubeFetcherAPI

A FastAPI-based backend service that continuously fetches YouTube videos for a predefined search query using the YouTube Data API v3. The service stores video metadata in a database and provides RESTful APIs for searching and filtering videos.

## 🚀 Features

- **Continuous Video Fetching**: Automatically fetches latest YouTube videos at configurable intervals
- **Multiple API Key Support**: Handles API quota limits by rotating through multiple YouTube API keys
- **Advanced Search & Filtering**: Search videos by keywords, filter by date ranges, and sort results
- **Pagination Support**: Efficient pagination for large datasets
- **Database Storage**: Stores video metadata including title, description, thumbnails, and publish dates
- **Real-time Configuration**: Environment-based configuration management

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: SQLite (configurable to PostgreSQL)
- **ORM**: SQLAlchemy
- **HTTP Client**: httpx
- **Environment Management**: python-dotenv
- **Data Validation**: Pydantic

## 📋 Prerequisites

- Python 3.8+
- YouTube Data API v3 keys
- pip (Python package manager)

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone
cd fampay-backend-assignment
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:

```env

YOUTUBE_API_KEYS=key1,key2,key3
SEARCH_QUERY=cats

# DB Configuration
DATABASE_URL=sqlite:///./videos.db
# For PostgreSQL: DATABASE_URL=postgresql://fampay_user:fampay_pass@localhost/youtube_db

# Fetcher Configuration
FETCH_INTERVAL=10
MAX_RESULTS=50

# Database Pool Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_PRE_PING=true
DB_POOL_RECYCLE=300

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=youtube_fetcher.log

# API Rate Limiting
REQUESTS_PER_MINUTE=100
```

### 5. Get YouTube API Keys
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add multiple API keys to handle quota limits

## 🚦 Running the Server

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

## 📡 API Endpoints

### 1. Main Videos Endpoint
```http
GET /videos
```

**Query Parameters:**
- `page` (int): Page number (starts from 1, default: 1)
- `size` (int): Number of videos per page (1-100, default: 10)
- `search` (string): Search keyword in title or description
- `published_after` (datetime): Filter videos published after this date (ISO format)
- `published_before` (datetime): Filter videos published before this date (ISO format)
- `sort_by` (string): Sort by field - `published_at` or `title` (default: `published_at`)
- `sort_order` (string): Sort order - `asc` or `desc` (default: `desc`)

**Example:**
```http
GET /videos?page=1&size=10&search=football&published_after=2024-01-01T00:00:00&sort_by=published_at&sort_order=desc
```

### 2. Dedicated Search Endpoint
```http
GET /videos/search
```

**Query Parameters:**
- `q` (string, required): Search query
- `page` (int): Page number (default: 1)
- `size` (int): Results per page (1-100, default: 10)
- `sort_by` (string): Sort by `published_at` or `title` (default: `published_at`)
- `sort_order` (string): Sort order `asc` or `desc` (default: `desc`)

**Example:**
```http
GET /videos/search?q=football&page=1&size=10&sort_by=title&sort_order=asc
```

### 3. Count Endpoint
```http
GET /videos/count
```

**Query Parameters:**
- `search` (string): Search keyword in title or description
- `published_after` (datetime): Filter videos published after this date
- `published_before` (datetime): Filter videos published before this date

**Example:**
```http
GET /videos/count?search=football&published_after=2024-01-01T00:00:00
```

## 🔍 Usage Examples

### 1. Get Latest Videos
```bash
curl "http://localhost:8000/videos"
```

### 2. Search for Football Videos
```bash
curl "http://localhost:8000/videos?search=football"
```

### 3. Get Videos from Last Week
```bash
curl "http://localhost:8000/videos?published_after=2024-06-03T00:00:00"
```

### 4. Sort Videos by Title Alphabetically
```bash
curl "http://localhost:8000/videos?sort_by=title&sort_order=asc"
```

### 5. Combined Search with Date Range
```bash
curl "http://localhost:8000/videos?search=goals&published_after=2024-06-01T00:00:00&published_before=2024-06-10T00:00:00"
```

### 6. Get Video Count for Search Query
```bash
curl "http://localhost:8000/videos/count?search=football"
```

### 7. Dedicated Search Endpoint
```bash
curl "http://localhost:8000/videos/search?q=cats&page=1&size=5"
```

## 📊 Response Format

### Video Object
```json
{
  "id": 1,
  "video_id": "dQw4w9WgXcQ",
  "title": "Sample Video Title",
  "description": "Sample video description...",
  "published_at": "2024-06-10T12:00:00Z",
  "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

### Videos List Response
```json
[
  {
    "id": 1,
    "video_id": "dQw4w9WgXcQ",
    "title": "Sample Video Title",
    "description": "Sample video description...",
    "published_at": "2024-06-10T12:00:00Z",
    "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }
]
```

### Count Response
```json
{
  "total_count": 150
}
```

## 🐛 Testing the API

### Using cURL
```bash
# Test basic endpoint
curl -X GET "http://localhost:8000/videos" -H "accept: application/json"

# Test search functionality
curl -X GET "http://localhost:8000/videos?search=python" -H "accept: application/json"

# Test pagination
curl -X GET "http://localhost:8000/videos?page=2&size=5" -H "accept: application/json"
```

### Using Python requests
```python
import requests

# Basic request
response = requests.get("http://localhost:8000/videos")
print(response.json())

# Search request
response = requests.get("http://localhost:8000/videos", params={
    "search": "python",
    "page": 1,
    "size": 10
})
print(response.json())
```

## 🔧 Configuration Options

| Environment Variable | Description | Default Value |
|---------------------|-------------|---------------|
| `YOUTUBE_API_KEYS` | Comma-separated YouTube API keys | Required |
| `SEARCH_QUERY` | Default search query for fetching videos | Required |
| `DATABASE_URL` | Database connection URL | `sqlite:///./videos.db` |
| `FETCH_INTERVAL` | Interval between API calls (seconds) | `10` |
| `MAX_RESULTS` | Maximum results per API call | `50` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `REQUESTS_PER_MINUTE` | API rate limiting | `100` |

## 🗂️ Project Structure

```
fampay-backend-assignment/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and connection
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas for API validation
├── youtube.py           # YouTube API integration and video fetching
├── routers/
│   └── videos.py        # Video-related API endpoints
├── .env                 # Environment variables (create this)
├── README.md            # Project documentation
└── videos.db            # SQLite database (auto-created)
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Quota Exceeded**
   - Add multiple API keys to the `YOUTUBE_API_KEYS` environment variable
   - The system automatically rotates through available keys

2. **Database Connection Issues**
   - Ensure the database URL is correct in the `.env` file
   - For SQLite, the file will be created automatically
   - For PostgreSQL, ensure the database exists and credentials are correct

3. **No Videos Being Fetched**
   - Check if your YouTube API keys are valid
   - Verify the search query is not too restrictive
   - Check the logs for any error messages

4. **Port Already in Use**
   - Change the port in the uvicorn command: `--port 8001`
   - Or kill the process using the port

### Logs and Debugging
- Check console output for real-time logs
- Video fetcher logs show API call status and results
- Enable debug mode with `--reload` flag for development

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For any issues or questions, please create an issue in the repository or contact the development team.

---

**Note**: Make sure to keep your YouTube API keys secure and never commit them to version control. Always use environment variables for sensitive configuration.
