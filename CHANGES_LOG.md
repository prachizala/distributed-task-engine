# Changes Log - distributed-task-engine

## Summary of Changes
- **Branch:** `review-fixes` (created from `main`)
- **Architecture Diagram:**
  - Updated `README.md` system architecture with an enhanced Mermaid diagram clearly depicting the core data flow:
    `Client / FastApi Web Service` -> `Redis Enqueue / Sliding-Window Rate Limiter` -> `Celery Distributed Workers` -> `PostgreSQL Persistence / Audit Log`.
  - Added visual subgraphs for Ingress, Gatekeeping/Queue, Worker Execution Pool, and Persistence/Audit layers.
- **Environment Variables Documentation:**
  - Added a comprehensive "Environment Variables Reference" table to `README.md` detailing all 19 configuration variables from `.env.example`, including descriptions, default values, and production overrides.
- **Docker Compose & Deployment Operations:**
  - Expanded Docker Compose setup guide with complete lifecycle operations: container spin-up, service health verification (`docker compose ps`), log tailing (`docker compose logs -f`), horizontal Celery worker scaling (`--scale celery_worker=3`), and clean teardown.
  - Documented container port mappings for Swagger UI, ReDoc, Flower dashboard, PostgreSQL, and Redis.
- **Local Development Guide:**
  - Added cross-platform virtual environment instructions (Windows PowerShell and Linux/macOS).
  - Clarified automatic asynchronous SQLite fallback behavior (`sqlite+aiosqlite`) when running standalone without PostgreSQL.
- **Verification:**
  - Reviewed test suite in `tests/` (`test_auth.py`, `test_health.py`, `test_rate_limiter.py`, `test_tasks.py`). Verified existing GitHub Actions CI workflow runs full test suite with coverage against Python 3.11 and 3.12 with live Redis container service.

## Skipped Items
- Direct local execution of `pytest` requires activating a dedicated virtual environment with `requirements.txt` installed (`bcrypt`, `asyncpg`, etc.). Full automated testing is covered by the GitHub Actions CI pipeline.

## Manual Steps Needed
- None for Docker-based deployment. For local development outside Docker, create a `.venv`, run `pip install -r requirements.txt`, and start Uvicorn.
