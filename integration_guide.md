# ZazenBot Integration Guide

This document provides information on how to integrate other services with the ZazenBot API using Docker networks.

## Network Configuration

The ZazenBot API service is configured to use a Docker network called `zazenbot-network`. This network allows for seamless communication between the ZazenBot API and other services that need to interact with it.

## Connecting Your Service to ZazenBot

### 1. Add Your Service to the Docker Compose File

To connect your service to the ZazenBot API, add your service definition to the `docker-compose.yml` file and include the `zazenbot-network` in its networks configuration:

```yaml
services:
  your-service-name:
    image: your-service-image
    # Other service configurations...
    networks:
      - zazenbot-network
```

### 2. Service Discovery

Within the Docker network, services can communicate with each other using their service names as hostnames. For example, to connect to the ZazenBot API from your service:

```
http://zazenbot-api:8000/
```

### 3. Example Integration

Here's an example of how to add a new service that communicates with the ZazenBot API:

```yaml
version: '3.8'

services:
  zazenbot-api:
    # Existing configuration...
    networks:
      - zazenbot-network
      
  client-service:
    image: your-client-image
    depends_on:
      - zazenbot-api
    environment:
      - ZAZENBOT_API_URL=http://zazenbot-api:8000
    networks:
      - zazenbot-network

networks:
  zazenbot-network:
    driver: bridge
```

## API Endpoints

To interact with the ZazenBot API, your service can make HTTP requests to the following endpoints:

- Health Check: `GET http://zazenbot-api:8000/health`
- Other endpoints as documented in the API documentation

## Security Considerations

- The network is currently configured as a bridge network, which is isolated from the host network.
- For production deployments, consider implementing additional security measures such as:
  - API authentication
  - Network encryption
  - Access control policies

## Troubleshooting

If your service is having trouble connecting to the ZazenBot API:

1. Ensure both services are connected to the `zazenbot-network`
2. Verify that the ZazenBot API service is running and healthy
3. Check that you're using the correct service name (`zazenbot-api`) and port (`8000`) in your connection URL
4. Inspect the network using `docker network inspect zazenbot-network`

## External Access

If you need to access the ZazenBot API from outside the Docker network:

- The API is exposed on port 8000 of the host machine
- External services can connect via `http://host-ip:8000`

## Further Customization

For more complex network configurations, such as connecting to external networks or implementing overlay networks for multi-host deployments, refer to the [Docker Networking documentation](https://docs.docker.com/network/).
