#!/bin/bash

# Run migrations
uv run manage.py migrate

# Start Django Q cluster in the background
uv run manage.py qcluster &

# Start Django development server
uv run manage.py runserver 0.0.0.0:8000
