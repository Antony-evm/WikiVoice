import uvicorn

from app import create_app
from app.config import get_settings
from app.logging_config import configure_logging

configure_logging()
app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        workers=1,
        timeout_graceful_shutdown=settings.shutdown_timeout_seconds,
    )
