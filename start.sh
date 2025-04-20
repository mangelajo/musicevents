#!/bin/bash

# Run migrations
python manage.py migrate

# Start Django Q cluster in the background
python manage.py qcluster &

# Start Django development server
python manage.py runserver 0.0.0.0:8000