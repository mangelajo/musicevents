# Makefile for Music Events project

.PHONY: help server sync migrate shell createsuperuser test clean

help:
        @echo "Available commands:"
        @echo "  make server      - Run development server"
        @echo "  make sync        - Run uv sync to update dependencies"
        @echo "  make migrate     - Run database migrations"
        @echo "  make shell       - Start Django shell"
        @echo "  make test        - Run tests"
        @echo "  make clean       - Remove Python bytecode files and cache"
        @echo "  make createsuperuser - Create a superuser"

server:
        uv run manage.py runserver 0.0.0.0:53324

sync:
        uv sync

migrate:
        uv run manage.py migrate

shell:
        uv run manage.py shell

test:
        uv run manage.py test

clean:
        find . -type f -name "*.pyc" -delete
        find . -type d -name "__pycache__" -delete
        find . -type d -name ".pytest_cache" -delete

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
.PHONY: container-build container-run container-stop

CONTAINER_NAME = musicevents
CONTAINER_TAG = latest
CONTAINER_PORT = 8000

container-build:
        podman build -t $(CONTAINER_NAME):$(CONTAINER_TAG) -f Containerfile .

container-run:
        podman run --name $(CONTAINER_NAME) \
                -p $(CONTAINER_PORT):8000 \
                -v $(PWD)/media:/app/media \
                -d $(CONTAINER_NAME):$(CONTAINER_TAG)

container-stop:
        -podman stop $(CONTAINER_NAME)
        -podman rm $(CONTAINER_NAME)

# Run all container commands in sequence
container-all: container-stop container-build container-run

# Show container logs
container-logs:
        podman logs -f $(CONTAINER_NAME)