import os
from typing import Annotated, Any

from pydantic import Field
from pydantic_settings import BaseSettings, CliSettingsSource, SettingsConfigDict

from pygate.argparser import create_root_parser, parse_env_file_path
from pygate.config import ConfigSettings

ENV_FILE_OVERRIDE_VAR = "PYGATE_ENV_FILE"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PYGATE_",
        env_file=".env",
        env_file_encoding="UTF-8",
        cli_parse_args=True,
        cli_kebab_case=True,
        cli_avoid_json=True,
        env_nested_delimiter="__",
    )

    host: str = "0.0.0.0"
    port: Annotated[int, Field(ge=1, le=65535)] = 8080

    config: Annotated[ConfigSettings, Field(default_factory=ConfigSettings)]


def get_settings(env_file: str | None = None) -> Settings:
    kwargs: dict[str, Any] = {}

    if env_file is None:
        root_parser = create_root_parser() if env_file is None else None
        kwargs["_cli_settings_source"] = CliSettingsSource(
            Settings,
            cli_show_env_vars=True,
            cli_parse_args=True,
            cli_kebab_case=True,
            root_parser=root_parser,
        )
        env_file = parse_env_file_path(root_parser) or os.environ.get(ENV_FILE_OVERRIDE_VAR)

    if env_file is not None:
        kwargs["_env_file"] = env_file

    return Settings(**kwargs)
