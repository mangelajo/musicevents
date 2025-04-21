#!/bin/bash

# Function to cleanup background processes
cleanup() {
    echo "Cleaning up background processes..."
    if [ -n "${QCLUSTER_PID}" ]; then
        echo "Stopping Django Q cluster (PID: ${QCLUSTER_PID})"
        kill ${QCLUSTER_PID} 2>/dev/null
        wait ${QCLUSTER_PID} 2>/dev/null
    fi
    exit 0
}

# Set up trap to catch termination signals
trap cleanup SIGINT SIGTERM EXIT

# Start Django-Q cluster in the background
echo "Starting Django Q cluster..."
uv run manage.py qcluster &
QCLUSTER_PID=$!
echo "Django Q cluster started with PID: ${QCLUSTER_PID}"

# Start Django development server
echo "Starting Django development server..."
uv run manage.py runserver 0.0.0.0:53324

