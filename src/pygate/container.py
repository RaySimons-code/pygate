from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

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

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass
