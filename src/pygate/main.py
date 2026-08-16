from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TypedDict

import structlog
from fastapi import FastAPI

from pygate.container import ServiceContainer
from pygate.settings import get_settings

logger = structlog.get_logger(__name__)


class State(TypedDict):
    container: ServiceContainer


def build_app(config_path: Path | None = None) -> FastAPI:
    settings = get_settings()

    logger.warn(f"Use config: {config_path}")
    logger.debug(f"Config details:\n{settings.model_dump_json(indent=2, ensure_ascii=False)}\n")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[State]:
        async with ServiceContainer(settings) as container:
            yield {"container": container}

    app = FastAPI(lifespan=lifespan)

    app.state.host = settings.host
    app.state.port = settings.port

    return app


app = build_app()


def startup(app: FastAPI) -> None:
    import uvicorn

    uvicorn.run(
        app=app,
        host=app.state.host,
        port=app.state.port,
        log_config=None,
    )


def main() -> None:
    startup(app)


if __name__ == "__main__":
    main()
