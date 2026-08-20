from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

import yaml

from pygate.config import PygateConfig, build_config_store
from pygate.settings import Settings


class DIContainer(ABC):
    @abstractmethod
    async def startup(self) -> None:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass

    async def __aenter__(self) -> Self:
        await self.startup()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.shutdown()


class ServiceContainer(DIContainer):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.config_store = build_config_store(
            settings=self.settings.config,
            model_cls=PygateConfig,
            parse_fn=yaml.safe_load,
        )

    async def startup(self) -> None:
        await self.config_store.start()

    async def shutdown(self) -> None:
        pass
