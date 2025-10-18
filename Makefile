.PHONY: help install dev-install test coverage lint format clean docker-up docker-down migrate shell

# Colors for output
BLUE=\033[0;34m
GREEN=\033[0;32m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)BookMe.ma - Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

dev-install: ## Install development dependencies
	pip install -e ".[dev]"
	pre-commit install

# Docker Commands
docker-up: ## Start all Docker services
	docker-compose up -d

docker-down: ## Stop all Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-build: ## Build Docker images
	docker-compose build

docker-restart: ## Restart all Docker services
	docker-compose restart

docker-clean: ## Clean Docker volumes
	docker-compose down -v

# Database Commands
migrate: ## Run database migrations
	python src/manage.py migrate_schemas --shared

migrate-tenant: ## Run migrations for all tenant schemas
	python src/manage.py migrate_schemas

makemigrations: ## Create new migrations
	python src/manage.py makemigrations

create-tenant: ## Create a new tenant
	python src/manage.py create_tenant

shell: ## Open Django shell
	python src/manage.py shell_plus --ipython

dbshell: ## Open database shell
	python src/manage.py dbshell

# Testing Commands
test: ## Run all tests
	pytest

test-verbose: ## Run tests with verbose output
	pytest -v

test-failed: ## Run only failed tests
	pytest --lf

test-coverage: ## Run tests with coverage report
	pytest --cov=src --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	pytest-watch

# Code Quality Commands
lint: ## Run linting
	ruff check src/
	mypy src/

lint-fix: ## Fix linting issues
	ruff check --fix src/

format: ## Format code with black
	black src/ tests/

format-check: ## Check code formatting
	black --check src/ tests/

quality: format lint ## Run all code quality checks

# Development Server Commands
runserver: ## Run development server
	python src/manage.py runserver

celery-worker: ## Run Celery worker
	celery -A bookme worker --loglevel=info

celery-beat: ## Run Celery beat scheduler
	celery -A bookme beat --loglevel=info

flower: ## Run Flower (Celery monitoring)
	celery -A bookme flower

# Utility Commands
clean: ## Clean Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage

superuser: ## Create a superuser
	python src/manage.py createsuperuser

collectstatic: ## Collect static files
	python src/manage.py collectstatic --noinput

# Documentation Commands
docs-serve: ## Serve documentation locally
	mkdocs serve

docs-build: ## Build documentation
	mkdocs build

# Production Commands
prod-up: ## Start production stack
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production stack
	docker-compose -f docker-compose.prod.yml down

prod-logs: ## View production logs
	docker-compose -f docker-compose.prod.yml logs -f

prod-build: ## Build production images
	docker-compose -f docker-compose.prod.yml build

# Backup & Restore
backup-db: ## Backup database
	python scripts/backup_database.py

restore-db: ## Restore database
	python scripts/restore_database.py

# CI/CD
ci: quality test ## Run CI pipeline locally

# Installation Commands
setup: dev-install docker-up migrate superuser ## Complete development setup
	@echo "$(GREEN)Setup complete! Run 'make runserver' to start the development server.$(NC)"

# Quick commands
dev: docker-up ## Start development environment
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "API: http://localhost:8000"
	@echo "Admin: http://localhost:8000/admin/"
	@echo "Flower: http://localhost:5555"

logs: docker-logs ## Alias for docker-logs

ps: ## Show running containers
	docker-compose ps

# Health checks
health: ## Check service health
	@echo "$(BLUE)Checking services...$(NC)"
	@curl -s http://localhost:8000/health/ | python -m json.tool || echo "$(RED)API is down$(NC)"
	@redis-cli ping > /dev/null 2>&1 && echo "$(GREEN)Redis: OK$(NC)" || echo "$(RED)Redis: DOWN$(NC)"
