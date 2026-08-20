from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

from pygate.config.loader import ConfigLoader
from pygate.config.settings import ConfigSettings, ConfigSourceTypes
from pygate.config.source import ConfigSource, FileConfigSource
from pygate.config.store import ConfigStore


def build_config_store[ConfigT: BaseModel](
    settings: ConfigSettings,
    model_cls: type[ConfigT],
    parse_fn: Callable[[bytes], dict[str, Any]],
) -> ConfigStore[ConfigT]:
    match settings.source_type:
        case ConfigSourceTypes.FILE:
            source: ConfigSource = FileConfigSource(settings.path)
        case _:
            raise ValueError(f"Unknown source_type: {settings.source_type}")

    loader = ConfigLoader(source, model_cls, parse_fn)
    store: ConfigStore[ConfigT] = ConfigStore(loader)

    return store
