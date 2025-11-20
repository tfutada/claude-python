# Python Tutorials

Educational Python project covering web frameworks and advanced concepts.

## Topics

1. **Flask** - Traditional WSGI web framework
2. **FastAPI** - Modern async web framework
3. **GIL** - Global Interpreter Lock and concurrency
4. **Async/Await** - Asynchronous programming
5. **Advanced** - Decorators, context managers, generators

## Setup

```bash
uv sync
```

## Run Examples

```bash
# Flask
uv run python tutorials/01_flask.py

# FastAPI
uv run uvicorn tutorials.02_fastapi:app --reload

# GIL demo
uv run python tutorials/03_gil.py

# Async demo
uv run python tutorials/04_async.py

# Advanced concepts
uv run python tutorials/05_advanced.py
```

## Structure

```
tutorials/
├── 01_flask.py      # Flask basics
├── 02_fastapi.py    # FastAPI with async
├── 03_gil.py        # GIL and threading
├── 04_async.py      # Async/await patterns
└── 05_advanced.py   # Decorators, context managers
```
