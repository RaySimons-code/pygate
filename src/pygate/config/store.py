from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from pygate.config.loader import ConfigLoader

logger = logging.getLogger("config_system")


@dataclass
class _VersionedConfig[ConfigT: BaseModel]:
    config: ConfigT
    version: float
    refcount: int = 0
    retired: bool = False
    drained: asyncio.Event = field(default_factory=asyncio.Event)


class ConfigHande[ConfigT: BaseModel]:
    __slots__ = ("_entry", "_store", "_released")

    def __init__(self, entry: _VersionedConfig[ConfigT], store: ConfigStore[ConfigT]) -> None:
        self._entry = entry
        self._store = store
        self._released = False

    @property
    def config(self) -> ConfigT:
        return self._entry.config

    @property
    def version(self) -> float:
        return self._entry.version

    def release(self) -> None:
        if not self._released:
            self._released = True
            self._store.release(self._entry)

    def __enter__(self) -> ConfigT:
        return self.config

    def __exit__(self, *exc_info: object) -> None:
        self.release()


class ConfigStore[ConfigT: BaseModel]:
    def __init__(
        self,
        loader: ConfigLoader[ConfigT],
        on_retire: Callable[[ConfigT], Any] | None = None,
    ) -> None:
        self._loader = loader
        self._on_retire = on_retire
        self._lock = asyncio.Lock()
        self._current: _VersionedConfig[ConfigT] | None = None
        self._last_fingerprint: str | None = None
        self._background_tasks: set[asyncio.Task[None]] = set()

    async def start(self) -> None:
        await self.reload(force=True)

    async def reload(self, force: bool = False) -> bool:
        if not force:
            fp = await self._loader.fingerprint()
            if fp is not None and fp != self._last_fingerprint:
                return False

        try:
            new_config = await self._loader.load()
        except Exception:
            logger.exception("Config reload failed, keeping previous version")
            return False

        async with self._lock:
            new_entry = _VersionedConfig(config=new_config, version=time.monotonic())
            old_entry, self._current = self._current, new_entry
            self._last_fingerprint = await self._loader.fingerprint()

        logger.info("Config reloaded: version=%f", new_entry.version)

        if old_entry is not None:
            task = asyncio.create_task(self._retire(old_entry))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

        return True

    def acquire(self) -> ConfigHande[ConfigT]:
        if self._current is None:
            raise RuntimeError("ConfigManager is not started yet — call start() first")
        entry = self._current
        entry.refcount += 1
        return ConfigHande(entry, self)

    def release(self, entry: _VersionedConfig[ConfigT]) -> None:
        entry.refcount -= 1
        if entry.retired and entry.refcount == 0:
            entry.drained.set()

    async def _retire(self, entry: _VersionedConfig[ConfigT]) -> None:
        entry.retired = True
        if entry.refcount == 0:
            entry.drained.set()
        await entry.drained.wait()
        if self._on_retire is not None:
            try:
                res = self._on_retire(entry.config)
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                logger.exception("`on_retire`-function failed when retire config")

        entry.config = None  # type: ignore[assignment]
        logger.info("Config version=%d retired and drained", entry.version)
