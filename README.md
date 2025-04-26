# Music Events

A Django application for managing and displaying music events with Spotify integration.

## Installation

For detailed installation instructions, including Docker Compose and Kubernetes Helm chart deployment, see [INSTALLING.md](./INSTALLING.md).

### Basic Installation

```bash
# Install with uv
uv pip install -e .
```

### Development Installation

For development, including running functional tests with Playwright:

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Install Playwright browsers
playwright install
```

## Configuration

### Spotify API Integration

To enable Spotify integration, you need to set up Spotify API credentials:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Log in with your Spotify account
3. Create a new app
4. Copy the Client ID and Client Secret
5. Add them to your environment variables or .env file:

```
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
```

### Fetching Spotify Data

After setting up the credentials, you can fetch Spotify data for artists using the management command:

```bash
# Fetch data for all artists
python manage.py fetch_spotify_data

# Force update even if data already exists
python manage.py fetch_spotify_data --force

# Update a specific artist by ID
python manage.py fetch_spotify_data --artist-id=1
```

You can also fetch Spotify data from the admin interface by selecting artists and using the "Fetch Spotify data for selected artists" action.

## Running Tests

```bash
# Run all tests
pytest

# Run only functional tests
pytest events/tests/functional/
```
