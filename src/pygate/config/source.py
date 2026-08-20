import abc
import asyncio
from pathlib import Path


class ConfigSource(abc.ABC):
    @abc.abstractmethod
    async def fetch(self) -> bytes: ...

    async def fingerprint(self) -> str | None:
        return None


class FileConfigSource(ConfigSource):
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    async def fetch(self) -> bytes:
        return await asyncio.to_thread(self._path.read_bytes)

    async def fingerprint(self) -> str | None:
        return await asyncio.to_thread(self._mtime, self._path)

    @staticmethod
    def _mtime(path: Path) -> str | None:
        try:
            return str(path.stat().st_mtime_ns)
        except FileNotFoundError:
            return None
