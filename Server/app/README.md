# App Skeleton

This directory contains the FastAPI application skeleton and shared infrastructure.

## Run locally

1. Copy `.env.example` to `.env`
2. Install dependencies from `pyproject.toml`
3. Start the service with:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
