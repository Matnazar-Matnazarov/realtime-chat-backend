.PHONY: help install dev test format lint clean run migrate superuser reset-db seed-users

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Install dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make format       - Format code with ruff"
	@echo "  make lint         - Lint code with ruff"
	@echo "  make run          - Run development server"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migrate-create - Create new migration (use: make migrate-create msg='message')"
	@echo "  make seed-users    - Seed database with users (admin + test users)"
	@echo "  make reset-db     - Reset database (drop all, recreate migrations)"
	@echo "  make clean        - Clean cache files"

install:
	uv pip install -r requirements.txt

dev:
	uv pip install -r requirements.txt
	uv pip install pytest pytest-asyncio httpx ruff

test:
	uv run pytest -v

test-cov:
	uv run pytest --cov=app --cov-report=html

format:
	uv run ruff format app/ tests/ scripts/

lint:
	uv run ruff check app/ tests/ scripts/

lint-fix:
	uv run ruff check app/ tests/ scripts/ --fix

run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --loop uvloop

migrate:
	uv run alembic upgrade head

migrate-create:
	uv run alembic revision --autogenerate -m "$(msg)"

seed-users:
	PYTHONPATH=$(shell pwd) uv run python scripts/seed_users.py

reset-db:
	PYTHONPATH=$(shell pwd) uv run python scripts/reset_database.py

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
