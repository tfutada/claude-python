# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Install dev dependencies
uv sync --all-extras

# Run Flask server
uv run python tutorials/01_flask.py

# Run FastAPI server
uv run uvicorn tutorials.02_fastapi:app --reload

# Run standalone scripts
uv run python tutorials/03_gil.py
uv run python tutorials/04_async.py
uv run python tutorials/05_advanced.py

# Run tests
uv run pytest
```

## Architecture

Educational tutorial project with self-contained Python files demonstrating:
- `01_flask.py` - WSGI web framework
- `02_fastapi.py` - Async web framework with Pydantic (module path: `tutorials.02_fastapi`)
- `03_gil.py` - Threading vs multiprocessing comparison
- `04_async.py` - Event loop and async/await patterns
- `05_advanced.py` - Decorators, context managers, generators

Each tutorial is independent and runnable standalone. No shared state between modules.
