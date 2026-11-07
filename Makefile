.PHONY: help install run test lint docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install     Install all dependencies"
	@echo "  make run         Start FastAPI development server with hot-reload"
	@echo "  make worker      Start Celery background worker"
	@echo "  make test        Execute Pytest test suite"
	@echo "  make lint        Run Ruff linter and code formatter"
	@echo "  make docker-up   Start full stack with Docker Compose"
	@echo "  make docker-down Stop Docker Compose stack"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	celery -A app.workers.celery_app.celery_app worker --loglevel=info --concurrency=4

test:
	pytest -v

lint:
	ruff check . --fix
	ruff format .

docker-up:
	docker compose -f docker/docker-compose.yml up --build -d

docker-down:
	docker compose -f docker/docker-compose.yml down -v
