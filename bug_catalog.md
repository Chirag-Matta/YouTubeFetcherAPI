# Bug Catalog for YouTubeFetcherAPI
## Testing Automated PR Reviewer System

This document catalogs 65+ bugs intentionally introduced into the YouTubeFetcherAPI codebase for testing an automated PR reviewer system.

---

## 🔴 CRITICAL SECURITY ISSUES

### Bug #1: API Keys Exposed in Logs
**File**: `youtube.py`, Line 13  
**Severity**: Critical  
**Category**: Security
```python
print(f"Loaded API Keys: {API_KEYS}")  # Exposes sensitive credentials
```
**Expected Review**: Flag as security vulnerability, suggest redacting sensitive data in logs.

### Bug #5: Full API Key Logged on Error
**File**: `youtube.py`, Line 60  
**Severity**: Critical  
**Category**: Security
```python
print(f"API key quota exceeded: {key} - {error_message}")  # Should only show key[:10]
```
**Expected Review**: Recommend masking API keys in error messages.

### Bug #13: API Keys in Config Response
**File**: `youtube.py`, Line 152  
**Severity**: Critical  
**Category**: Security
```python
"api_keys": API_KEYS,  # Never expose API keys via API endpoint!
```
**Expected Review**: Flag as data exposure vulnerability.

### Bug #14: SQL Injection Vulnerability
**File**: `videos.py`, Line 26  
**Severity**: Critical  
**Category**: Security
```python
raw_sql = f"SELECT * FROM videos WHERE title LIKE '%{search}%'"
```
**Expected Review**: Critical SQL injection vulnerability, recommend parameterized queries.

### Bug #28: Hardcoded Database Credentials
**File**: `database.py`, Line 9  
**Severity**: High  
**Category**: Security
```python
DATABASE_URL = os.getenv("DATABASE_URL","postgresql://fampay_user:fampay_pass@localhost/youtube_db")
```
**Expected Review**: Credentials in default values can be committed to version control.

---

## 🟠 HIGH SEVERITY BUGS

### Bug #2: Missing Timezone Awareness
**File**: `youtube.py`, Line 18  
**Severity**: High  
**Category**: Logic Error
```python
PUBLISHED_AFTER = datetime.now() - timedelta(hours=1)  # Missing timezone.utc
```
**Expected Review**: Can cause timezone-related bugs in production.

### Bug #4: Incorrect ISO Format
**File**: `youtube.py`, Line 46  
**Severity**: High  
**Category**: Logic Error
```python
"publishedAfter": PUBLISHED_AFTER.isoformat(),  # Missing Z suffix conversion
```
**Expected Review**: YouTube API expects specific ISO format with Z suffix.

### Bug #6: Bare Exception Clause
**File**: `youtube.py`, Line 73  
**Severity**: High  
**Category**: Error Handling
```python
except:  # Catches all exceptions including SystemExit, KeyboardInterrupt
    continue
```
**Expected Review**: Bare except clause is dangerous, recommend specific exception types.

### Bug #7: Resource Leak
**File**: `youtube.py`, Line 86  
**Severity**: High  
**Category**: Resource Management
```python
db = SessionLocal()  # No try-finally or context manager
```
**Expected Review**: Database session may not close on exception.

### Bug #39: Dropping Production Tables
**File**: `main.py`, Line 9  
**Severity**: Critical  
**Category**: Data Loss
```python
Base.metadata.drop_all(bind=engine)  # DESTROYS ALL DATA ON STARTUP!
```
**Expected Review**: This will delete all production data every time the app starts.

---

## 🟡 MEDIUM SEVERITY BUGS

### Bug #3: No Connection Pooling
**File**: `youtube.py`, Line 41  
**Severity**: Medium  
**Category**: Performance
```python
async with httpx.AsyncClient(timeout=30) as client:  # Created in loop
```
**Expected Review**: Creating new client for each API key iteration is inefficient.

### Bug #8: No Error Handling for Items
**File**: `youtube.py`, Line 93  
**Severity**: Medium  
**Category**: Error Handling
```python
for item in items:
    vid_id = item["id"]["videoId"]  # KeyError if structure changes
```
**Expected Review**: Should wrap in try-except to handle malformed responses.

### Bug #10: Missing Break Statement
**File**: `youtube.py`, Line 108  
**Severity**: Medium  
**Category**: Logic Error
```python
for quality in ["maxres", "high", "medium", "default"]:
    if quality in thumbnails:
        thumbnail_url = thumbnails[quality].get("url", "")
        if thumbnail_url:
            pass  # Missing break!
```
**Expected Review**: Loop continues unnecessarily after finding thumbnail.

### Bug #11: Batch Commit Risk
**File**: `youtube.py`, Line 128  
**Severity**: Medium  
**Category**: Data Integrity
```python
db.commit()  # After adding all videos - all-or-nothing approach
```
**Expected Review**: If commit fails, all videos are lost. Consider per-item or batch commits.

### Bug #12: Race Condition
**File**: `youtube.py`, Line 136  
**Severity**: Medium  
**Category**: Concurrency
```python
PUBLISHED_AFTER = latest_time  # Global variable without lock
```
**Expected Review**: Multiple tasks could cause race condition.

### Bug #15: Conditional Logic Error
**File**: `videos.py`, Line 31  
**Severity**: Medium  
**Category**: Logic Error
```python
if not search:  # Date filters only applied when no search
    date_filters = []
```
**Expected Review**: Date filters should work with search parameter.

### Bug #17: Integer Overflow Risk
**File**: `videos.py`, Line 45  
**Severity**: Medium  
**Category**: Validation
```python
skip = (page - 1) * size  # No validation for large values
```
**Expected Review**: Could overflow with malicious large page numbers.

### Bug #19: Case-Sensitive Search
**File**: `videos.py`, Line 56  
**Severity**: Medium  
**Category**: Inconsistency
```python
models.Video.title.like(f"%{q}%"),  # Should be ilike
```
**Expected Review**: Inconsistent with main endpoint that uses ilike.

### Bug #23: Inefficient Count Query
**File**: `videos.py`, Line 92  
**Severity**: Medium  
**Category**: Performance
```python
total_count = query.count()  # Fetches all rows first
```
**Expected Review**: Use COUNT(*) query for better performance.

### Bug #30-31: Missing Connection Pool Config
**File**: `database.py`, Line 16  
**Severity**: Medium  
**Category**: Performance/Reliability
```python
engine = create_engine(DATABASE_URL, ...)  # No pool settings
```
**Expected Review**: Should configure pool_size, max_overflow, pool_pre_ping.

### Bug #33: No Rollback on Exception
**File**: `database.py`, Line 25  
**Severity**: Medium  
**Category**: Transaction Management
```python
finally:
    db.close()  # Should rollback before close
```
**Expected Review**: Add db.rollback() in exception handler.

---

## 🟢 LOW SEVERITY / CODE QUALITY ISSUES

### Bug #16: Missing Input Validation
**File**: `videos.py`, Line 39  
**Severity**: Low  
**Category**: Error Handling
```python
sort_column = getattr(models.Video, sort_by)  # Could raise AttributeError
```
**Expected Review**: Add try-except even though regex validation exists.

### Bug #18: No Database Error Handling
**File**: `videos.py`, Line 49  
**Severity**: Low  
**Category**: Error Handling
```python
return videos  # No try-except for database query
```
**Expected Review**: Should handle potential database exceptions.

### Bug #20: Code Duplication
**File**: `videos.py`, Line 62-69  
**Severity**: Low  
**Category**: Code Quality
```python
# Same sorting logic repeated in multiple endpoints
```
**Expected Review**: Extract common sorting logic into helper function.

### Bug #21: Inconsistent Filter Logic
**File**: `videos.py`, Line 81-91  
**Severity**: Low  
**Category**: Consistency
```python
# Different filter application than get_videos
```
**Expected Review**: Ensure consistent filtering across all endpoints.

### Bug #29: Missing SSL Configuration
**File**: `database.py`, Line 11  
**Severity**: Low  
**Category**: Security
```python
# No SSL/TLS configuration for PostgreSQL
```
**Expected Review**: Add SSL requirements for production databases.

### Bug #38: Deprecated API Usage
**File**: `database.py`, Line 19  
**Severity**: Low  
**Category**: Maintenance
```python
Base = declarative_base()  # Deprecated in SQLAlchemy 2.0
```
**Expected Review**: Use DeclarativeBase for SQLAlchemy 2.0 compatibility.

### Bug #40: Missing CORS Configuration
**File**: `main.py`, Line 10  
**Severity**: Low  
**Category**: Configuration
```python
app = FastAPI()  # No CORS middleware
```
**Expected Review**: Add CORS configuration for frontend access.

### Bug #42-43: Untracked Background Task
**File**: `main.py`, Line 17  
**Severity**: Low  
**Category**: Task Management
```python
asyncio.create_task(fetch_youtube_videos())  # No tracking or error handling
```
**Expected Review**: Store task reference and add exception handling.

### Bug #52-57: Missing Model Constraints
**File**: `models.py`, Various lines  
**Severity**: Low  
**Category**: Data Integrity
```python
video_id = Column(String, unique=True)  # No length limit
title = Column(String)  # No length limit
published_at = Column(DateTime)  # Missing nullable=False
```
**Expected Review**: Add appropriate constraints, lengths, and nullable specifications.

### Bug #60: Missing __repr__ Method
**File**: `models.py`, Line N/A  
**Severity**: Low  
**Category**: Debugging
```python
class Video(Base):
    # No __repr__ method
```
**Expected Review**: Add __repr__ for better debugging experience.

---

## 🔵 MISSING FEATURES / TECHNICAL DEBT

### Bugs #24-27: Missing Endpoints
**File**: `videos.py`  
**Category**: Missing Features
- No health check endpoint
- No single video fetch by ID
- No rate limiting
- No authentication

### Bugs #34-37: Database Best Practices
**File**: `database.py`  
**Category**: Missing Features
- No connection health check
- No Alembic migrations
- No retry logic
- No operation logging

### Bugs #44-50: Application Features
**File**: `main.py`  
**Category**: Missing Features
- No shutdown handler
- No root endpoint
- No health endpoint
- No API metadata
- No request logging
- No response time tracking

### Bugs #58-65: Model Enhancements
**File**: `models.py`  
**Category**: Missing Features
- No created_at/updated_at
- No soft delete support
- No composite indexes
- No additional YouTube metadata fields
- No table constraints

---

## Testing Recommendations

Your PR reviewer system should be able to identify:

1. **Security vulnerabilities** (SQL injection, exposed credentials, data leaks)
2. **Logic errors** (timezone issues, missing break statements, conditional errors)
3. **Performance issues** (inefficient queries, missing indexes, no connection pooling)
4. **Error handling problems** (bare exceptions, resource leaks, missing try-catch)
5. **Code quality issues** (duplication, inconsistency, deprecated APIs)
6. **Missing features** (endpoints, middleware, logging, monitoring)
7. **Data integrity risks** (missing constraints, transaction issues)
8. **Concurrency problems** (race conditions, global state)

## Expected Output Format

Your reviewer should generate comments like:
```
🔴 CRITICAL: SQL Injection Vulnerability
File: videos.py, Line 26
Never use f-strings for SQL queries. This allows attackers to inject malicious SQL.
Recommendation: Use SQLAlchemy's parameterized queries instead.
```

Good luck testing your automated PR reviewer! 🚀