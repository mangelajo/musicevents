# Makefile for Music Events project

.PHONY: help server sync migrate shell createsuperuser test test-coverage test-verbose test-parallel test-functional clean
.PHONY: compile-messages

# Container configuration
CONTAINER_TOOL ?= podman
CONTAINER_NAME = musicevents
CONTAINER_TAG = latest
CONTAINER_PORT = 8000

# Environment variables
ENV_FILE ?= .env
TICKETMASTER_API_KEY ?= $(shell grep TICKETMASTER_API_KEY $(ENV_FILE) 2>/dev/null | cut -d '=' -f2)
SPOTIFY_CLIENT_ID ?= $(shell grep SPOTIFY_CLIENT_ID $(ENV_FILE) 2>/dev/null | cut -d '=' -f2)
SPOTIFY_CLIENT_SECRET ?= $(shell grep SPOTIFY_CLIENT_SECRET $(ENV_FILE) 2>/dev/null | cut -d '=' -f2)

# Docker Compose configuration
COMPOSE_PROJECT_NAME = musicevents
COMPOSE ?= docker compose

help:
	    @echo "Available commands:"
	    @echo "  make server           - Run development server"
	    @echo "  make sync             - Run uv sync to update dependencies"
	    @echo "  make migrate          - Run database migrations"
	    @echo "  make migrations       - Create new migrations in the database"
	    @echo "  make compile-messages - Compile i18n message files"
	    @echo "  make shell            - Start Django shell"
	    @echo "  make test             - Run tests (keeps test database)"
	    @echo "  make test-verbose     - Run tests with verbose output"
	    @echo "  make test-coverage    - Run tests with coverage report"
	    @echo "  make test-specific    - Run specific test (use TEST=path.to.test)"
	    @echo "  make test-functional  - Run functional tests with Playwright"
	    @echo "  make clean            - Remove Python bytecode files and cache"
	    @echo "  make createsuperuser  - Create a superuser"
	    @echo ""
	    @echo "Container commands (using $(CONTAINER_TOOL)):"
	    @echo "  make container-build      - Build development container image"
	    @echo "  make container-build-prod - Build production container image"
	    @echo "  make container-run        - Run container"
	    @echo "  make container-stop       - Stop and remove container"
	    @echo "  make container-all        - Run all container commands"
	    @echo "  make container-logs       - Show container logs"
	    @echo ""
	    @echo "Docker Compose commands:"
	    @echo "  make compose-up    - Start services with docker compose"
	    @echo "  make compose-watch - Start Watch services"
	    @echo "  make compose-down  - Stop services"
	    @echo "  make compose-build - Build services"
	    @echo "  make compose-logs  - Show service logs"
	    @echo "  make compose-ps    - List running services"
	    @echo ""
	    @echo "Environment variables:"
	    @echo "  CONTAINER_TOOL     - Container tool to use (default: podman)"
	    @echo "                       Supported: podman, docker"
	    @echo "  ENV_FILE          - Environment file to use (default: .env)"
	    @echo "  COMPOSE           - Docker compose command (default: docker compose)"
	    @echo "  TICKETMASTER_API_KEY - Ticketmaster API key (from $(ENV_FILE))"
	    @echo "  SPOTIFY_CLIENT_ID    - Spotify Client ID (from $(ENV_FILE))"
	    @echo "  SPOTIFY_CLIENT_SECRET - Spotify Client Secret (from $(ENV_FILE))"

server:
	    TICKETMASTER_API_KEY=$(TICKETMASTER_API_KEY) \
	    SPOTIFY_CLIENT_ID=$(SPOTIFY_CLIENT_ID) \
	    SPOTIFY_CLIENT_SECRET=$(SPOTIFY_CLIENT_SECRET) \
	    ./start.sh

sync:
	    uv sync --all-extras

migrate:
	    uv run manage.py migrate

migrations:
	    uv run manage.py makemigrations

shell:
	    uv run manage.py shell

test: compile-messages
	    uv run manage.py test

test-verbose: compile-messages
	    uv run manage.py test -v 2

test-coverage:
	    uv run coverage run manage.py test
	    uv run coverage report
	    uv run coverage html

test-specific: compile-messages
	    @if [ "$(TEST)" = "" ]; then \
	            echo "Please specify a test with TEST=path.to.test"; \
	            exit 1; \
	    fi
	    uv run manage.py test $(TEST)

test-functional:
	    uv run playwright install --with-deps
	    uv run pytest events/tests/functional/

clean:
	    find . -type f -name "*.pyc" -delete
	    find . -type d -name "__pycache__" -delete
	    find . -type d -name ".pytest_cache" -delete
	    find . -type d -name "htmlcov" -delete
	    find . -type f -name ".coverage" -delete

createsuperuser:
	    uv run manage.py createsuperuser

compile-messages:
	    uv run manage.py compilemessages >/dev/null

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
.PHONY: container-build container-build-prod container-run container-stop container-all container-logs compose-up compose-down compose-build compose-logs compose-ps
.PHONY: migrations

# Check if .env file exists, if not create from example
check-env:
	    @if [ ! -f "$(ENV_FILE)" ]; then \
	            echo "Creating $(ENV_FILE) from .env.example..."; \
	            cp .env.example $(ENV_FILE); \
	            echo "Please edit $(ENV_FILE) and set your environment variables."; \
	            exit 1; \
	    fi

container-build:
	    $(CONTAINER_TOOL) build \
	            -t $(CONTAINER_NAME):$(CONTAINER_TAG) \
	            -f Containerfile .

container-build-prod:
	    $(CONTAINER_TOOL) build \
	            -t $(CONTAINER_NAME)-prod:$(CONTAINER_TAG) \
	            -f Containerfile.prod .

container-run: check-env
	    $(CONTAINER_TOOL) run --name $(CONTAINER_NAME) \
	            -p $(CONTAINER_PORT):8000 \
	            -v $(PWD)/media:/app/media \
	            -e TICKETMASTER_API_KEY=$(TICKETMASTER_API_KEY) \
	            -e SPOTIFY_CLIENT_ID=$(SPOTIFY_CLIENT_ID) \
	            -e SPOTIFY_CLIENT_SECRET=$(SPOTIFY_CLIENT_SECRET) \
	            -d $(CONTAINER_NAME):$(CONTAINER_TAG)

container-stop:
	    -$(CONTAINER_TOOL) stop $(CONTAINER_NAME)
	    -$(CONTAINER_TOOL) rm $(CONTAINER_NAME)

# Run all container commands in sequence
container-all: container-stop container-build container-run

# Show container logs
container-logs:
	    $(CONTAINER_TOOL) logs -f $(CONTAINER_NAME)

# Docker Compose commands
compose-up: check-env
	    $(COMPOSE) up -d

compose-watch: check-env
	    $(COMPOSE)  up --build --watch

compose-down:
	    $(COMPOSE) down

compose-build: check-env
	    $(COMPOSE) build

compose-logs:
	    $(COMPOSE) logs -f

compose-ps:
	    $(COMPOSE) ps
