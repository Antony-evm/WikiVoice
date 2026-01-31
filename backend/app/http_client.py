import httpx


def create_http_client() -> httpx.AsyncClient:
    """Create and configure an HTTPX asynchronous client."""
    return httpx.AsyncClient(  # nosec B113
        timeout=httpx.Timeout(20.0),
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20,
        ),
    )
