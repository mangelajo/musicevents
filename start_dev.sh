#!/bin/bash


# Start Django-Q cluster
uv run manage.py qcluster &

# Start Django development server in the background
uv run manage.py runserver 0.0.0.0:53324

