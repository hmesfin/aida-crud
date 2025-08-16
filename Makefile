# AIDA-CRUD Development Makefile

.PHONY: help install test lint format clean build

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Backend commands
install-backend: ## Install backend dependencies
	cd backend && pip install -e ".[dev]"

test-backend: ## Run backend tests
	cd backend && pytest tests/ -v --cov=aida_crud --cov-report=term-missing

lint-backend: ## Lint backend code
	cd backend && ruff check aida_crud/
	cd backend && black --check aida_crud/
	cd backend && isort --check-only aida_crud/
	cd backend && mypy aida_crud/ || true

format-backend: ## Format backend code
	cd backend && ruff check --fix aida_crud/
	cd backend && black aida_crud/
	cd backend && isort aida_crud/

# Frontend commands
install-frontend: ## Install frontend dependencies
	cd frontend/aida-crud && npm install

test-frontend: ## Run frontend tests
	cd frontend/aida-crud && npm run test

test-frontend-coverage: ## Run frontend tests with coverage
	cd frontend/aida-crud && npm run test:coverage

lint-frontend: ## Lint frontend code
	cd frontend/aida-crud && npm run lint

format-frontend: ## Format frontend code
	cd frontend/aida-crud && npm run format

type-check: ## Run TypeScript type checking
	cd frontend/aida-crud && npm run type-check

# Combined commands
install: install-backend install-frontend ## Install all dependencies

test: test-backend test-frontend ## Run all tests

lint: lint-backend lint-frontend ## Lint all code

format: format-backend format-frontend ## Format all code

# Build commands
build-backend: ## Build Python package
	cd backend && python -m build

build-frontend: ## Build frontend package
	cd frontend/aida-crud && npm run build

build: build-backend build-frontend ## Build all packages

# Clean commands
clean-backend: ## Clean backend build artifacts
	cd backend && rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete

clean-frontend: ## Clean frontend build artifacts
	cd frontend/aida-crud && rm -rf dist/ node_modules/ coverage/ .vitest/

clean: clean-backend clean-frontend ## Clean all build artifacts

# Development commands
dev-backend: ## Run Django development server
	cd backend && python manage.py runserver

dev-frontend: ## Run frontend development server
	cd frontend/aida-crud && npm run dev

dev: ## Run both backend and frontend in development
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@make -j2 dev-backend dev-frontend

# Docker commands (if needed in future)
docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

# Documentation commands
docs: ## Generate documentation
	@echo "Generating documentation..."
	cd backend && python -m pydoc -w aida_crud
	@echo "Documentation generated in backend/aida_crud.html"

# Quality checks
quality: lint type-check test ## Run all quality checks

# CI simulation
ci: quality build ## Simulate CI pipeline locally
	@echo "✅ All CI checks passed!"