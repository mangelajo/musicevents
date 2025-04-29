# Installing Music Events

This document provides detailed instructions for installing the Music Events application using different methods.

## Table of Contents

- [Docker Compose Installation](#docker-compose-installation)
- [Helm Chart Installation](#helm-chart-installation)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration Options](#configuration-options)
  - [Upgrading](#upgrading)
  - [Uninstalling](#uninstalling)
- [Manual Installation](#manual-installation)

## Docker Compose Installation

For local development or simple deployments, you can use Docker Compose:

1. Create a `.env` file with your configuration:
   ```
   # Django settings
   DEBUG=False
   DJANGO_SECRET_KEY=your_django_secret_key
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database URL (follows RFC-1738 format)
   DATABASE_URL=postgres://musicevents:musicevents@postgres:5432/musicevents
   
   # API keys
   TICKETMASTER_API_KEY=your_ticketmaster_api_key
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   
   # Admin configuration
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=secure_password
   ADMIN_EMAIL=admin@example.com
   ```

2. Start the application:
   ```bash
   docker-compose up -d
   ```

3. Access the application at http://localhost:8001

## Helm Chart Installation

### Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (if persistence is enabled)

### Installation

1. Create a values file (e.g., `my-values.yaml`):
   ```yaml
   domain: musicevents.example.com
   ticketmasterApiKey: "your-ticketmaster-api-key"
   djangoSecretKey: "your-django-secret-key"
   spotifyClientId: "your-spotify-client-id"
   spotifyClientSecret: "your-spotify-client-secret"
   
   # Admin configuration
   adminUsername: "admin"
   adminPassword: "secure_password"
   adminEmail: "admin@example.com"
   
   # Database configuration (using DATABASE_URL format)
   databaseUrl: "postgres://musicevents:musicevents@postgres-service:5432/musicevents"
   ```

2. Install the chart directly from the OCI registry:
   ```bash
   helm install musicevents oci://ghcr.io/mangelajo/charts/musicevents --version <version> -f my-values.yaml
   ```

To list available versions:

```bash
helm registry login ghcr.io -u <username>
helm search repo oci://ghcr.io/mangelajo/charts/musicevents --versions
```

### Configuration Options

The following table lists the main configurable parameters of the Music Events chart and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `domain` | Domain name for the application | `musicevents.local` |
| `ticketmasterApiKey` | Ticketmaster API key | `""` |
| `spotifyClientId` | Spotify Client ID | `""` |
| `spotifyClientSecret` | Spotify Client Secret | `""` |
| `djangoSecretKey` | Django secret key (auto-generated if not set) | `""` |
| `djangoDebug` | Enable Django debug mode | `"False"` |
| `djangoSettingsModule` | Django settings module | `"music_events_project.settings.prod"` |
| `djangoSecureSslRedirect` | Enable SSL redirect | `"False"` |
| `corsAllowedOrigins` | CORS allowed origins | `""` |
| `adminUsername` | Admin username | `"admin"` |
| `adminPassword` | Admin password | `"admin"` |
| `adminEmail` | Admin email | `"admin@example.com"` |
| `databaseUrl` | Database URL (RFC-1738 format) | `"postgres://musicevents:musicevents@postgres-service:5432/musicevents"` |

The `databaseUrl` parameter follows the RFC-1738 format: `postgres://user:password@host:port/dbname`. The PostgreSQL database container will automatically extract the credentials from this URL.
| `image.repository` | Image repository | `ghcr.io/mangelajo/music-events` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `persistence.enabled` | Enable persistence for media files | `true` |
| `persistence.media.storageClass` | Storage class for media PVC | `""` |
| `persistence.media.size` | Size of media PVC | `1Gi` |
| `persistence.postgres.storageClass` | Storage class for PostgreSQL PVC | `""` |
| `persistence.postgres.size` | Size of PostgreSQL PVC | `5Gi` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class name | `"nginx"` |

For a complete list of configuration options, refer to the [values.yaml](./charts/musicevents/values.yaml) file.

### Upgrading

To upgrade the release:

```bash
helm upgrade musicevents oci://ghcr.io/mangelajo/charts/musicevents --version <version> -f my-values.yaml
```

### Uninstalling

To uninstall/delete the `musicevents` release:

```bash
helm uninstall musicevents
```

Note: This will not delete the Persistent Volume Claims. To delete them:

```bash
kubectl delete pvc -l app.kubernetes.io/instance=musicevents
```

## Manual Installation

For manual installation instructions, refer to the [README.md](./README.md) file.