FROM python:3.12-slim-bookworm

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app


# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN uv pip install --system -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN uv run manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Copy and make start script executable
COPY start.sh .
RUN chmod +x start.sh

# Run migrations and start both servers
CMD ["./start.sh"]
