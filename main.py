import uvicorn
from core.web.application import app
from core.settings.base import settings

if __name__ == "__main__":
    uvicorn.run(
        "core.web.application:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )