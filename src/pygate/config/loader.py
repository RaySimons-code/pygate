from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

from pygate.config.source import ConfigSource


class ConfigLoader[ConfigT: BaseModel]:
    def __init__(
        self,
        source: ConfigSource,
        model_cls: type[ConfigT],
        parse_fn: Callable[[bytes], dict[str, Any]],
    ):
        self._source = source
        self._model_cls = model_cls
        self._parse_fn = parse_fn

    async def load(self) -> ConfigT:
        raw = await self._source.fetch()
        data = self._parse_fn(raw)
        return self._model_cls.model_validate(data)

    async def fingerprint(self) -> str | None:
        return await self._source.fingerprint()
