from enum import StrEnum

from pydantic import BaseModel


class ConfigSourceTypes(StrEnum):
    FILE = "file"


class ConfigSettings(BaseModel):
    source_type: ConfigSourceTypes = ConfigSourceTypes.FILE
    path: str = "pygate.yaml"
