"""
FastAPI Tutorial - Modern Async Web Framework
=============================================

FastAPI is built on Starlette and Pydantic. It's async-first,
provides automatic API documentation, and type validation.

Key concepts:
- Async/await endpoints
- Pydantic models for validation
- Automatic OpenAPI docs
- Dependency injection
- Path/Query/Body parameters

Run: uvicorn tutorials.02_fastapi:app --reload
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body
from pydantic import BaseModel, Field
from typing import Optional
import asyncio
import time

app = FastAPI(
    title="FastAPI Tutorial",
    description="Learning FastAPI async web framework",
    version="1.0.0"
)

# =============================================================================
# 1. Pydantic Models - Request/Response Validation
# =============================================================================

class Item(BaseModel):
    """Request/response model with automatic validation."""
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    in_stock: bool = True

class ItemResponse(BaseModel):
    """Response model."""
    id: int
    name: str
    price: float
    description: Optional[str]
    in_stock: bool

# In-memory database
items_db: dict[int, Item] = {}
item_counter = 0


# =============================================================================
# 2. Basic Routes - Sync vs Async
# =============================================================================

@app.get("/")
def root():
    """
    Sync endpoint (def).
    FastAPI runs this in a thread pool to avoid blocking.
    """
    return {"message": "FastAPI Tutorial"}


@app.get("/async")
async def async_root():
    """
    Async endpoint (async def).
    Runs directly on the event loop - more efficient for I/O.
    """
    return {"message": "Async endpoint"}


# =============================================================================
# 3. Path Parameters with Validation
# =============================================================================

@app.get("/items/{item_id}")
async def get_item(
    item_id: int = Path(..., ge=1, description="Item ID must be >= 1")
):
    """Path parameter with validation."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, **items_db[item_id].model_dump()}


# =============================================================================
# 4. Query Parameters
# =============================================================================

@app.get("/search")
async def search_items(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Query parameters with validation and defaults."""
    results = [
        {"id": id, **item.model_dump()}
        for id, item in items_db.items()
        if q.lower() in item.name.lower()
    ]
    return {
        "query": q,
        "results": results[skip:skip + limit],
        "total": len(results)
    }


# =============================================================================
# 5. Request Body with Pydantic
# =============================================================================

@app.post("/items", response_model=ItemResponse)
async def create_item(item: Item):
    """
    Create item with automatic validation.
    Pydantic validates the request body against the Item model.
    """
    global item_counter
    item_counter += 1
    items_db[item_counter] = item
    return {"id": item_counter, **item.model_dump()}


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    """Update existing item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = item
    return {"id": item_id, **item.model_dump()}


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Delete item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    return {"deleted": item_id}


# =============================================================================
# 6. Dependency Injection
# =============================================================================

async def get_current_user(token: str = Query(...)):
    """
    Dependency that validates auth token.
    In real apps, this would verify JWT, check database, etc.
    """
    if token != "secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user_id": 1, "username": "demo_user"}


@app.get("/me")
async def get_my_info(user: dict = Depends(get_current_user)):
    """Endpoint using dependency injection for auth."""
    return user


# Reusable dependency
def pagination(skip: int = 0, limit: int = 10):
    """Common pagination dependency."""
    return {"skip": skip, "limit": limit}


@app.get("/items")
async def list_items(pagination: dict = Depends(pagination)):
    """List items with pagination dependency."""
    items = [
        {"id": id, **item.model_dump()}
        for id, item in items_db.items()
    ]
    skip = pagination["skip"]
    limit = pagination["limit"]
    return items[skip:skip + limit]


# =============================================================================
# 7. Async Operations - The Power of FastAPI
# =============================================================================

@app.get("/slow-sync")
def slow_sync():
    """
    Sync endpoint with blocking I/O.
    FastAPI runs this in threadpool - limited concurrency.
    """
    time.sleep(2)
    return {"message": "Sync slow response"}


@app.get("/slow-async")
async def slow_async():
    """
    Async endpoint with non-blocking I/O.
    Can handle many concurrent requests efficiently.
    """
    await asyncio.sleep(2)
    return {"message": "Async slow response"}


@app.get("/parallel")
async def parallel_tasks():
    """
    Run multiple I/O operations in parallel.
    This is where async really shines.
    """
    async def fetch_data(name: str, delay: float):
        await asyncio.sleep(delay)
        return {"name": name, "delay": delay}

    # Run 3 tasks concurrently - total time ~1s, not 1.5s
    results = await asyncio.gather(
        fetch_data("A", 0.5),
        fetch_data("B", 1.0),
        fetch_data("C", 0.3)
    )
    return {"results": results}


# =============================================================================
# 8. Background Tasks
# =============================================================================

from fastapi import BackgroundTasks

def write_log(message: str):
    """Background task - runs after response is sent."""
    with open("log.txt", "a") as f:
        f.write(f"{message}\n")


@app.post("/notify")
async def send_notification(
    email: str = Body(...),
    background_tasks: BackgroundTasks = None
):
    """
    Return response immediately, process in background.
    Good for emails, logging, etc.
    """
    background_tasks.add_task(write_log, f"Notification sent to {email}")
    return {"message": f"Notification will be sent to {email}"}


# =============================================================================
# 9. Exception Handling
# =============================================================================

class CustomException(Exception):
    def __init__(self, detail: str):
        self.detail = detail

from fastapi.responses import JSONResponse

@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
    """Custom exception handler."""
    return JSONResponse(
        status_code=400,
        content={"error": exc.detail, "type": "custom_error"}
    )


@app.get("/error")
async def trigger_error():
    """Trigger custom exception."""
    raise CustomException(detail="This is a custom error")


# =============================================================================
# 10. Middleware
# =============================================================================

from fastapi import Request

@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    """Middleware to add response timing."""
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    response.headers["X-Response-Time"] = f"{elapsed:.4f}s"
    return response


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("""
FastAPI Tutorial
================
Run with: uvicorn tutorials.02_fastapi:app --reload

API Docs: http://localhost:8000/docs
ReDoc:    http://localhost:8000/redoc

Key Endpoints:
  GET  /              - Sync endpoint
  GET  /async         - Async endpoint
  GET  /items         - List items
  POST /items         - Create item
  GET  /search?q=...  - Search items
  GET  /me?token=...  - Auth dependency demo
  GET  /slow-sync     - Blocking endpoint
  GET  /slow-async    - Non-blocking endpoint
  GET  /parallel      - Concurrent I/O demo
    """)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
