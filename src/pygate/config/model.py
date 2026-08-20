from enum import StrEnum, auto
from typing import Annotated, Self

from pydantic import AnyHttpUrl, BaseModel, Field, model_validator


class Methods(StrEnum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[str]) -> str:
        return name.upper()

    GET = auto()
    POST = auto()
    PUT = auto()
    PATCH = auto()
    DELETE = auto()
    OPTIONS = auto()


class RouteConfig(BaseModel):
    path: str
    methods: Annotated[set[Methods], Field(default_factory=lambda: set[Methods](Methods))]
    upstream: AnyHttpUrl


class PygateConfig(BaseModel):
    routes: Annotated[list[RouteConfig], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_routes(self) -> Self:
        methods_by_path: dict[str, set[Methods]] = {}

        for route in self.routes:
            existing_methods = methods_by_path.setdefault(route.path, set())

            if intersection := existing_methods & route.methods:
                raise ValueError(
                    f"Duplicate route '{route.path}' for methods: {sorted(intersection)}"
                )

            existing_methods.update(route.methods)

        return self
