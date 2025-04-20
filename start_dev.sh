#!/bin/bash

# Start Django development server in the background
uv run manage.py runserver 0.0.0.0:53324 &

# Start Django-Q cluster
uv run manage.py qcluster