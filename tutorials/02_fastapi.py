"""
FastAPI - Async Web Framework
=============================

FastAPI supports both sync and async endpoints.
Async endpoints can handle many concurrent requests efficiently.
"""

from fastapi import FastAPI
import asyncio
import time

app = FastAPI()


# =============================================================================
# Sync vs Async Endpoints
# =============================================================================

@app.get("/sync")
def sync_endpoint():
    """Sync (def) - FastAPI runs this in a thread pool."""
    return {"message": "Sync endpoint"}


@app.get("/async")
async def async_endpoint():
    """Async (async def) - runs on event loop, more efficient for I/O."""
    return {"message": "Async endpoint"}


# =============================================================================
# Blocking vs Non-blocking
# =============================================================================

@app.get("/slow-sync")
def slow_sync():
    """Blocks the thread pool worker for 2 seconds."""
    time.sleep(2)
    return {"message": "Sync done after 2s"}


@app.get("/slow-async")
async def slow_async():
    """Non-blocking - can handle other requests while waiting."""
    await asyncio.sleep(2)
    return {"message": "Async done after 2s"}


# =============================================================================
# Parallel I/O - Where Async Shines
# =============================================================================

@app.get("/parallel")
async def parallel():
    """Run 3 tasks concurrently - total time ~1s, not 3s."""
    async def task(name: str, delay: float):
        await asyncio.sleep(delay)
        return f"{name} done"

    results = await asyncio.gather(
        task("A", 1.0),
        task("B", 1.0),
        task("C", 1.0)
    )
    return {"results": results}


if __name__ == "__main__":
    print("""
FastAPI (Async)
===============
GET /sync        - Sync endpoint (thread pool)
GET /async       - Async endpoint (event loop)
GET /slow-sync   - Blocking 2s
GET /slow-async  - Non-blocking 2s
GET /parallel    - 3 concurrent tasks in ~1s

Run: uvicorn tutorials.02_fastapi:app --reload
Docs: http://localhost:8000/docs
    """)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
