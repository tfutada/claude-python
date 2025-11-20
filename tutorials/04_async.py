"""
Async/Await Tutorial
====================

Python's asyncio provides single-threaded concurrency using
coroutines and an event loop. Excellent for I/O-bound tasks.

Key concepts:
- Event loop - schedules and runs coroutines
- Coroutines - async def functions
- await - yield control back to event loop
- Tasks - scheduled coroutines
- asyncio.gather - run coroutines concurrently
"""

import asyncio
import time
import aiohttp
import httpx

# =============================================================================
# 1. Basic Coroutines
# =============================================================================

async def hello():
    """
    Basic coroutine.
    Must be awaited or scheduled as a task.
    """
    print("Hello...")
    await asyncio.sleep(1)  # Non-blocking sleep
    print("...World!")
    return "Done"


async def demo_basic_coroutine():
    """Run a basic coroutine."""
    print("=" * 60)
    print("1. BASIC COROUTINE")
    print("=" * 60)

    result = await hello()
    print(f"Result: {result}")
    print("-" * 60)


# =============================================================================
# 2. Sequential vs Concurrent Execution
# =============================================================================

async def fetch_data(name: str, delay: float) -> dict:
    """Simulate async I/O operation."""
    print(f"  Fetching {name}...")
    await asyncio.sleep(delay)
    print(f"  {name} done!")
    return {"name": name, "delay": delay}


async def demo_sequential():
    """Run tasks sequentially - slow."""
    print("\n" + "=" * 60)
    print("2a. SEQUENTIAL EXECUTION")
    print("=" * 60)

    start = time.time()

    # Each await completes before next starts
    result1 = await fetch_data("A", 1.0)
    result2 = await fetch_data("B", 1.0)
    result3 = await fetch_data("C", 1.0)

    elapsed = time.time() - start
    print(f"\nTotal time: {elapsed:.2f}s (expected ~3s)")
    print("-" * 60)


async def demo_concurrent():
    """Run tasks concurrently - fast."""
    print("\n" + "=" * 60)
    print("2b. CONCURRENT EXECUTION (asyncio.gather)")
    print("=" * 60)

    start = time.time()

    # All tasks run concurrently
    results = await asyncio.gather(
        fetch_data("A", 1.0),
        fetch_data("B", 1.0),
        fetch_data("C", 1.0)
    )

    elapsed = time.time() - start
    print(f"\nResults: {results}")
    print(f"Total time: {elapsed:.2f}s (expected ~1s)")
    print("-" * 60)


# =============================================================================
# 3. Creating Tasks
# =============================================================================

async def demo_tasks():
    """
    Create tasks for more control over execution.
    Tasks start immediately when created.
    """
    print("\n" + "=" * 60)
    print("3. TASKS - Explicit Scheduling")
    print("=" * 60)

    start = time.time()

    # Create tasks - they start running immediately
    task1 = asyncio.create_task(fetch_data("Task1", 1.0))
    task2 = asyncio.create_task(fetch_data("Task2", 0.5))
    task3 = asyncio.create_task(fetch_data("Task3", 0.8))

    print("Tasks created and running...")

    # Wait for all tasks
    results = await asyncio.gather(task1, task2, task3)

    elapsed = time.time() - start
    print(f"\nResults: {[r['name'] for r in results]}")
    print(f"Total time: {elapsed:.2f}s")
    print("-" * 60)


# =============================================================================
# 4. Task Cancellation
# =============================================================================

async def long_running_task():
    """Task that can be cancelled."""
    try:
        print("  Long task started")
        await asyncio.sleep(10)
        print("  Long task completed")
    except asyncio.CancelledError:
        print("  Long task was cancelled!")
        raise  # Re-raise to properly handle cancellation


async def demo_cancellation():
    """Demonstrate task cancellation."""
    print("\n" + "=" * 60)
    print("4. TASK CANCELLATION")
    print("=" * 60)

    task = asyncio.create_task(long_running_task())

    # Wait a bit then cancel
    await asyncio.sleep(0.5)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("Task cancellation confirmed")

    print("-" * 60)


# =============================================================================
# 5. Timeouts
# =============================================================================

async def demo_timeout():
    """Demonstrate timeout handling."""
    print("\n" + "=" * 60)
    print("5. TIMEOUTS")
    print("=" * 60)

    try:
        # Wait max 0.5s for task that takes 2s
        async with asyncio.timeout(0.5):
            await fetch_data("SlowTask", 2.0)
    except TimeoutError:
        print("  Task timed out!")

    print("-" * 60)


# =============================================================================
# 6. Async Context Managers
# =============================================================================

class AsyncResource:
    """Async context manager for resource management."""

    async def __aenter__(self):
        print("  Acquiring async resource...")
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("  Releasing async resource...")
        await asyncio.sleep(0.1)

    async def do_work(self):
        print("  Working with resource...")
        await asyncio.sleep(0.2)


async def demo_async_context_manager():
    """Demonstrate async context manager."""
    print("\n" + "=" * 60)
    print("6. ASYNC CONTEXT MANAGERS")
    print("=" * 60)

    async with AsyncResource() as resource:
        await resource.do_work()

    print("-" * 60)


# =============================================================================
# 7. Async Iterators
# =============================================================================

async def async_range(start: int, stop: int, delay: float = 0.1):
    """Async generator - yields values with delay."""
    for i in range(start, stop):
        await asyncio.sleep(delay)
        yield i


async def demo_async_iterator():
    """Demonstrate async iteration."""
    print("\n" + "=" * 60)
    print("7. ASYNC ITERATORS")
    print("=" * 60)

    print("  Async range:")
    async for num in async_range(0, 5, 0.1):
        print(f"    {num}", end=" ")
    print()

    # Async comprehension
    result = [x async for x in async_range(0, 5, 0.05)]
    print(f"  Async comprehension: {result}")

    print("-" * 60)


# =============================================================================
# 8. Semaphores - Limiting Concurrency
# =============================================================================

async def limited_fetch(sem: asyncio.Semaphore, name: str):
    """Fetch with concurrency limit."""
    async with sem:
        print(f"  {name} starting (holding semaphore)")
        await asyncio.sleep(0.5)
        print(f"  {name} done")
        return name


async def demo_semaphore():
    """
    Use semaphore to limit concurrent operations.
    Useful for rate limiting API calls.
    """
    print("\n" + "=" * 60)
    print("8. SEMAPHORES - Limiting Concurrency")
    print("=" * 60)

    # Max 2 concurrent operations
    sem = asyncio.Semaphore(2)

    start = time.time()

    # Create 5 tasks, but only 2 run at a time
    tasks = [
        asyncio.create_task(limited_fetch(sem, f"Task{i}"))
        for i in range(5)
    ]

    await asyncio.gather(*tasks)

    elapsed = time.time() - start
    print(f"\n5 tasks with semaphore(2): {elapsed:.2f}s")
    print("(Expected ~1.5s: ceiling(5/2) * 0.5s)")
    print("-" * 60)


# =============================================================================
# 9. Real HTTP Requests
# =============================================================================

async def demo_http_requests():
    """
    Real async HTTP requests with httpx.
    Demonstrates practical async I/O.
    """
    print("\n" + "=" * 60)
    print("9. ASYNC HTTP REQUESTS")
    print("=" * 60)

    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
    ]

    # Sequential
    start = time.time()
    async with httpx.AsyncClient() as client:
        for url in urls:
            response = await client.get(url)
    sequential_time = time.time() - start

    # Concurrent
    start = time.time()
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
    concurrent_time = time.time() - start

    print(f"3 HTTP requests (1s delay each):")
    print(f"  Sequential: {sequential_time:.2f}s")
    print(f"  Concurrent: {concurrent_time:.2f}s")
    print(f"  Speedup: {sequential_time / concurrent_time:.1f}x")
    print("-" * 60)


# =============================================================================
# 10. Mixing Sync and Async
# =============================================================================

def blocking_io():
    """Synchronous blocking operation."""
    import time
    time.sleep(1)
    return "blocking result"


async def demo_run_in_executor():
    """
    Run blocking code in thread pool.
    Use when you must call sync code from async context.
    """
    print("\n" + "=" * 60)
    print("10. MIXING SYNC AND ASYNC")
    print("=" * 60)

    loop = asyncio.get_event_loop()

    start = time.time()

    # Run blocking code in thread pool - doesn't block event loop
    result = await loop.run_in_executor(None, blocking_io)

    elapsed = time.time() - start
    print(f"Ran blocking code in executor: {elapsed:.2f}s")
    print(f"Result: {result}")
    print("-" * 60)


# =============================================================================
# 11. Common Patterns
# =============================================================================

async def demo_patterns():
    """Common async patterns."""
    print("\n" + "=" * 60)
    print("11. COMMON PATTERNS")
    print("=" * 60)

    # Pattern 1: First completed
    print("\na) as_completed - Process results as they arrive:")
    tasks = [
        asyncio.create_task(fetch_data("Fast", 0.1)),
        asyncio.create_task(fetch_data("Slow", 0.5)),
        asyncio.create_task(fetch_data("Medium", 0.3)),
    ]

    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(f"   Completed: {result['name']}")

    # Pattern 2: Wait with conditions
    print("\nb) wait - Wait with conditions:")
    tasks = [
        asyncio.create_task(fetch_data("A", 0.3)),
        asyncio.create_task(fetch_data("B", 0.1)),
        asyncio.create_task(fetch_data("C", 0.5)),
    ]

    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )
    print(f"   First completed: {len(done)}")
    print(f"   Still pending: {len(pending)}")

    # Cancel pending
    for task in pending:
        task.cancel()

    # Pattern 3: gather with return_exceptions
    print("\nc) gather with exception handling:")
    async def might_fail(name: str):
        if name == "fail":
            raise ValueError("Intentional failure")
        return name

    results = await asyncio.gather(
        might_fail("ok1"),
        might_fail("fail"),
        might_fail("ok2"),
        return_exceptions=True
    )
    print(f"   Results (including exceptions): {results}")

    print("-" * 60)


# =============================================================================
# Summary
# =============================================================================

def print_summary():
    """Print async/await summary."""
    print("\n" + "=" * 60)
    print("ASYNC/AWAIT SUMMARY")
    print("=" * 60)
    print("""
Key Points:
-----------
1. async def creates a coroutine
2. await suspends execution until result ready
3. Event loop manages scheduling
4. asyncio.gather() for concurrent execution
5. asyncio.create_task() for explicit task creation
6. Semaphores for rate limiting
7. Use run_in_executor() for blocking code

When to Use Async:
------------------
- I/O-bound operations (network, disk)
- Many concurrent connections
- Web scraping, API clients
- Web servers (FastAPI, aiohttp)

When NOT to Use Async:
----------------------
- CPU-bound tasks (use multiprocessing)
- Simple scripts
- When all dependencies are synchronous
    """)
    print("=" * 60)


# =============================================================================
# Main
# =============================================================================

async def main():
    """Run all demos."""
    await demo_basic_coroutine()
    await demo_sequential()
    await demo_concurrent()
    await demo_tasks()
    await demo_cancellation()
    await demo_timeout()
    await demo_async_context_manager()
    await demo_async_iterator()
    await demo_semaphore()
    # Skip HTTP demo by default (requires network)
    # await demo_http_requests()
    await demo_run_in_executor()
    await demo_patterns()
    print_summary()


if __name__ == "__main__":
    print("\nAsync/Await Tutorial")
    print("=" * 60)
    asyncio.run(main())
