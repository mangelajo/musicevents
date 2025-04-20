# Music Events Helm Chart

This Helm chart deploys the Music Events application on a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (if persistence is enabled)

## Installing the Chart

1. Clone the repository:
```bash
git clone https://github.com/mangelajo/musicevents.git
cd musicevents
```

2. Create a values file (e.g., `my-values.yaml`):
```yaml
domain: musicevents.example.com
ticketmasterApiKey: "your-api-key"
```

3. Install the chart:
```bash
helm install musicevents ./charts/musicevents -f my-values.yaml
```

## Configuration

The following table lists the configurable parameters of the Music Events chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `domain` | Domain name for the application | `musicevents.local` |
| `ticketmasterApiKey` | Ticketmaster API key | `""` |
| `djangoSecretKey` | Django secret key (auto-generated if not set) | `""` |
| `djangoDebug` | Enable Django debug mode | `"False"` |
| `image.repository` | Image repository | `musicevents` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `persistence.enabled` | Enable persistence for media files | `true` |
| `persistence.media.storageClass` | Storage class for media PVC | `""` |
| `persistence.media.accessMode` | Access mode for media PVC | `ReadWriteOnce` |
| `persistence.media.size` | Size of media PVC | `1Gi` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class name | `"nginx"` |

## Persistence

The chart mounts a Persistent Volume for media files. The volume is created using dynamic volume provisioning.

## Ingress

The chart creates an Ingress resource to expose the application. By default, it uses the nginx ingress controller.