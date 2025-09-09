# Makefile for English with Toto Django project

.PHONY: help install test lint format clean build deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  clean       - Clean up temporary files"
	@echo "  build       - Build Docker image"
	@echo "  deploy      - Deploy to staging/production"
	@echo "  backup      - Create backup"
	@echo "  restore     - Restore from backup"

# Installation
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	python manage.py test
	coverage run --source='.' manage.py test
	coverage report
	coverage html

# Linting
lint:
	flake8 .
	black --check .
	isort --check-only .
	mypy .
	bandit -r .

# Formatting
format:
	black .
	isort .

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/
	rm -rf build/ dist/

# Docker commands
build:
	docker build -t english-with-toto/backend:latest .

build-dev:
	docker build --target development -t english-with-toto/backend:dev .

# Development
dev:
	docker-compose up -d

dev-down:
	docker-compose down

dev-logs:
	docker-compose logs -f

# Database
migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

# Static files
collectstatic:
	python manage.py collectstatic --noinput

# Shell
shell:
	python manage.py shell

# Create superuser
createsuperuser:
	python manage.py createsuperuser

# Deployment
deploy-staging:
	./scripts/deploy.sh staging

deploy-production:
	./scripts/deploy.sh production

# Backup and restore
backup:
	./scripts/backup.sh staging

restore:
	@read -p "Enter backup file path: " file; \
	./scripts/restore.sh staging $$file

# Monitoring
monitor:
	docker-compose -f docker-compose.production.yml up -d monitoring grafana

# Security
security-scan:
	bandit -r . -f json -o bandit-report.json
	safety check

# Performance
performance-test:
	locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 60s

# Documentation
docs:
	cd docs && make html

# All checks
check: lint test security-scan
