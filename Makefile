# Makefile for Music Events project

.PHONY: help server sync migrate shell createsuperuser test test-coverage test-verbose test-parallel clean

# Container configuration
CONTAINER_TOOL ?= podman
CONTAINER_NAME = musicevents
CONTAINER_TAG = latest
CONTAINER_PORT = 8000

help:
	@echo "Available commands:"
	@echo "  make server          - Run development server"
	@echo "  make sync           - Run uv sync to update dependencies"
	@echo "  make migrate        - Run database migrations"
	@echo "  make shell          - Start Django shell"
	@echo "  make test           - Run tests (keeps test database)"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make test-parallel  - Run tests in parallel"
	@echo "  make test-specific  - Run specific test (use TEST=path.to.test)"
	@echo "  make test-clean     - Run tests and destroy test database"
	@echo "  make clean          - Remove Python bytecode files and cache"
	@echo "  make createsuperuser - Create a superuser"
	@echo ""
	@echo "Container commands (using $(CONTAINER_TOOL)):"
	@echo "  make container-build - Build container image"
	@echo "  make container-run  - Run container"
	@echo "  make container-stop - Stop and remove container"
	@echo "  make container-all  - Run all container commands"
	@echo "  make container-logs - Show container logs"
	@echo ""
	@echo "Environment variables:"
	@echo "  CONTAINER_TOOL     - Container tool to use (default: podman)"
	@echo "                       Supported: podman, docker"

server:
	uv run manage.py runserver 0.0.0.0:53324

sync:
	uv sync

migrate:
	uv run manage.py migrate

shell:
	uv run manage.py shell

test:
	python3 manage.py test --keepdb

test-verbose:
	python3 manage.py test -v 2 --keepdb

test-coverage:
	pip install coverage
	coverage run manage.py test --keepdb
	coverage report
	coverage html

test-parallel:
	python3 manage.py test --parallel --keepdb

test-specific:
	@if [ "$(TEST)" = "" ]; then \
	        echo "Please specify a test with TEST=path.to.test"; \
	        exit 1; \
	fi
	python3 manage.py test $(TEST) --keepdb

test-clean:
	python3 manage.py test --noinput --keepdb=false

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "htmlcov" -delete
	find . -type f -name ".coverage" -delete

createsuperuser:
	uv run manage.py createsuperuser

# Add migrations command to create new migrations
makemigrations:
	uv run manage.py makemigrations

# Add a command to collect static files
collectstatic:
	uv run manage.py collectstatic --noinput

# Add a command to run both makemigrations and migrate
migrateall: makemigrations migrate

# Add a command to start fresh (clean and sync)
fresh: clean sync

# Container related commands
.PHONY: container-build container-run container-stop container-all container-logs

container-build:
	$(CONTAINER_TOOL) build -t $(CONTAINER_NAME):$(CONTAINER_TAG) -f Containerfile .

container-run:
	$(CONTAINER_TOOL) run --name $(CONTAINER_NAME) \
	        -p $(CONTAINER_PORT):8000 \
	        -v $(PWD)/media:/app/media \
	        -d $(CONTAINER_NAME):$(CONTAINER_TAG)

container-stop:
	-$(CONTAINER_TOOL) stop $(CONTAINER_NAME)
	-$(CONTAINER_TOOL) rm $(CONTAINER_NAME)

# Run all container commands in sequence
container-all: container-stop container-build container-run

# Show container logs
container-logs:
	$(CONTAINER_TOOL) logs -f $(CONTAINER_NAME)