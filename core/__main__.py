import platform
import uvicorn
from core.settings import settings


def main() -> None:
    """Entrypoint of the application."""
    if platform.system() == "Windows" or settings.reload:
        # Always use uvicorn on Windows or when reload=True (dev mode)
        uvicorn.run(
            "core.web.application:get_app",
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            workers=settings.workers_count,
            log_level=settings.log_level.value.lower(),
            factory=True,
        )
    else:
        # Import Gunicorn only when running on Linux/macOS
        from core.gunicorn_runner import GunicornApplication

        GunicornApplication(
            "core.web.application:get_app",
            host=settings.host,
            port=settings.port,
            workers=settings.workers_count,
            factory=True,
            accesslog="-",
            loglevel=settings.log_level.value.lower(),
            access_log_format='%r "-" %s "-" %Tf',
        ).run()


if __name__ == "__main__":
    main()
