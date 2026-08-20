from typing import Annotated, cast

from fastapi import Depends, Request

from pygate.container import ServiceContainer


def get_container(request: Request) -> ServiceContainer:
    container = cast(ServiceContainer, request.state.container)
    return container


ContainerDep = Annotated[ServiceContainer, Depends(get_container)]
