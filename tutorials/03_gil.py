"""
GIL (Global Interpreter Lock) Tutorial
======================================

The GIL is a mutex in CPython that protects access to Python objects,
preventing multiple threads from executing Python bytecode simultaneously.

Key concepts:
- GIL prevents true parallelism for CPU-bound tasks
- I/O-bound tasks release GIL, allowing concurrency
- multiprocessing bypasses GIL (separate processes)
- Threading still useful for I/O-bound work

This tutorial demonstrates these concepts with benchmarks.
"""

import threading
import multiprocessing
import time
import os

# =============================================================================
# 1. CPU-Bound Task - GIL Impact
# =============================================================================

def cpu_bound_task(n: int) -> int:
    """
    CPU-bound task (heavy computation).
    GIL prevents parallel execution in threads.
    """
    total = 0
    for i in range(n):
        total += i ** 2
    return total


def demo_cpu_bound_threading():
    """
    Demonstrate GIL limiting threading for CPU-bound tasks.
    Two threads take similar time as single thread due to GIL.
    """
    n = 5_000_000

    # Single thread
    start = time.time()
    cpu_bound_task(n)
    cpu_bound_task(n)
    single_time = time.time() - start

    # Two threads
    start = time.time()
    t1 = threading.Thread(target=cpu_bound_task, args=(n,))
    t2 = threading.Thread(target=cpu_bound_task, args=(n,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    thread_time = time.time() - start

    print("=" * 60)
    print("CPU-BOUND: Threading (GIL Impact)")
    print("=" * 60)
    print(f"Single thread (sequential): {single_time:.3f}s")
    print(f"Two threads (concurrent):   {thread_time:.3f}s")
    print(f"Speedup: {single_time / thread_time:.2f}x")
    print("\nExpected: ~1x speedup (GIL prevents parallelism)")
    print("-" * 60)


def demo_cpu_bound_multiprocessing():
    """
    Demonstrate multiprocessing bypassing GIL.
    Two processes achieve true parallelism.
    """
    n = 5_000_000

    # Single process
    start = time.time()
    cpu_bound_task(n)
    cpu_bound_task(n)
    single_time = time.time() - start

    # Two processes
    start = time.time()
    p1 = multiprocessing.Process(target=cpu_bound_task, args=(n,))
    p2 = multiprocessing.Process(target=cpu_bound_task, args=(n,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    process_time = time.time() - start

    print("\n" + "=" * 60)
    print("CPU-BOUND: Multiprocessing (Bypasses GIL)")
    print("=" * 60)
    print(f"Single process (sequential): {single_time:.3f}s")
    print(f"Two processes (parallel):    {process_time:.3f}s")
    print(f"Speedup: {single_time / process_time:.2f}x")
    print(f"\nExpected: ~{multiprocessing.cpu_count()}x speedup on {multiprocessing.cpu_count()}-core CPU")
    print("-" * 60)


# =============================================================================
# 2. I/O-Bound Task - GIL Released
# =============================================================================

def io_bound_task(seconds: float) -> None:
    """
    I/O-bound task (simulated network/disk).
    GIL is released during I/O, allowing concurrency.
    """
    time.sleep(seconds)


def demo_io_bound_threading():
    """
    Demonstrate threading effectiveness for I/O-bound tasks.
    GIL is released during I/O, so threads run concurrently.
    """
    sleep_time = 1.0

    # Single thread
    start = time.time()
    io_bound_task(sleep_time)
    io_bound_task(sleep_time)
    single_time = time.time() - start

    # Two threads
    start = time.time()
    t1 = threading.Thread(target=io_bound_task, args=(sleep_time,))
    t2 = threading.Thread(target=io_bound_task, args=(sleep_time,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    thread_time = time.time() - start

    print("\n" + "=" * 60)
    print("I/O-BOUND: Threading (GIL Released)")
    print("=" * 60)
    print(f"Single thread (sequential): {single_time:.3f}s")
    print(f"Two threads (concurrent):   {thread_time:.3f}s")
    print(f"Speedup: {single_time / thread_time:.2f}x")
    print("\nExpected: ~2x speedup (GIL released during I/O)")
    print("-" * 60)


# =============================================================================
# 3. Mixed Workload
# =============================================================================

def mixed_task(n: int, io_time: float) -> int:
    """Mix of CPU and I/O work."""
    result = cpu_bound_task(n)
    time.sleep(io_time)
    return result


def demo_mixed_workload():
    """
    Mixed CPU and I/O workload.
    Threading helps with I/O portion but not CPU portion.
    """
    n = 1_000_000
    io_time = 0.5

    # Single thread
    start = time.time()
    mixed_task(n, io_time)
    mixed_task(n, io_time)
    single_time = time.time() - start

    # Two threads
    start = time.time()
    t1 = threading.Thread(target=mixed_task, args=(n, io_time))
    t2 = threading.Thread(target=mixed_task, args=(n, io_time))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    thread_time = time.time() - start

    print("\n" + "=" * 60)
    print("MIXED: CPU + I/O Workload")
    print("=" * 60)
    print(f"Single thread (sequential): {single_time:.3f}s")
    print(f"Two threads (concurrent):   {thread_time:.3f}s")
    print(f"Speedup: {single_time / thread_time:.2f}x")
    print("\nExpected: Between 1x and 2x (I/O overlaps, CPU serialized)")
    print("-" * 60)


# =============================================================================
# 4. Thread Safety and Race Conditions
# =============================================================================

counter = 0
lock = threading.Lock()

def unsafe_increment():
    """Unsafe increment - race condition possible."""
    global counter
    for _ in range(100000):
        counter += 1  # Not atomic!

def safe_increment():
    """Safe increment with lock."""
    global counter
    for _ in range(100000):
        with lock:
            counter += 1


def demo_race_condition():
    """
    Demonstrate race conditions and thread safety.
    Even with GIL, increments aren't atomic.
    """
    global counter

    print("\n" + "=" * 60)
    print("THREAD SAFETY: Race Conditions")
    print("=" * 60)

    # Unsafe version
    counter = 0
    threads = [threading.Thread(target=unsafe_increment) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Unsafe increment (5 threads x 100000):")
    print(f"  Expected: 500000")
    print(f"  Actual:   {counter}")
    print(f"  Lost:     {500000 - counter}")

    # Safe version
    counter = 0
    threads = [threading.Thread(target=safe_increment) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"\nSafe increment with lock:")
    print(f"  Expected: 500000")
    print(f"  Actual:   {counter}")
    print("-" * 60)


# =============================================================================
# 5. ProcessPoolExecutor for CPU-bound
# =============================================================================

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

def demo_executors():
    """
    Demonstrate Executor pattern for easy parallelism.
    ProcessPoolExecutor for CPU, ThreadPoolExecutor for I/O.
    """
    n = 2_000_000
    tasks = [n] * 4

    print("\n" + "=" * 60)
    print("EXECUTORS: ProcessPool vs ThreadPool")
    print("=" * 60)

    # ThreadPoolExecutor (limited by GIL for CPU-bound)
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(cpu_bound_task, tasks))
    thread_time = time.time() - start

    # ProcessPoolExecutor (bypasses GIL)
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(cpu_bound_task, tasks))
    process_time = time.time() - start

    print(f"4 CPU-bound tasks:")
    print(f"  ThreadPoolExecutor: {thread_time:.3f}s")
    print(f"  ProcessPoolExecutor: {process_time:.3f}s")
    print(f"  Speedup: {thread_time / process_time:.2f}x")
    print("-" * 60)


# =============================================================================
# 6. GIL Internals
# =============================================================================

def demo_gil_info():
    """
    Show information about GIL behavior.
    """
    import sys

    print("\n" + "=" * 60)
    print("GIL INFORMATION")
    print("=" * 60)

    print(f"Python version: {sys.version}")
    print(f"CPU cores: {multiprocessing.cpu_count()}")

    # GIL switch interval
    interval = sys.getswitchinterval()
    print(f"GIL switch interval: {interval * 1000:.1f}ms")
    print("\nThe switch interval determines how often Python")
    print("checks if another thread is waiting for the GIL.")

    print("\n" + "=" * 60)
    print("SUMMARY: When to Use What")
    print("=" * 60)
    print("""
CPU-bound tasks (heavy computation):
  - Use multiprocessing or ProcessPoolExecutor
  - Each process has its own GIL
  - Good for: math, image processing, data crunching

I/O-bound tasks (network, disk):
  - Use threading or asyncio
  - GIL released during I/O operations
  - Good for: web scraping, API calls, file operations

Mixed workloads:
  - Consider asyncio with ProcessPoolExecutor
  - Run I/O in event loop, CPU in process pool
    """)
    print("-" * 60)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("\nGIL (Global Interpreter Lock) Tutorial")
    print("=" * 60)

    demo_cpu_bound_threading()
    demo_cpu_bound_multiprocessing()
    demo_io_bound_threading()
    demo_mixed_workload()
    demo_race_condition()
    demo_executors()
    demo_gil_info()
