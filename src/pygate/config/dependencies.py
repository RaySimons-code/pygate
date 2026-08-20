from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends

from pygate.config import PygateConfig
from pygate.dependencies import ContainerDep


async def get_config(container: ContainerDep) -> AsyncIterator[PygateConfig]:
    with container.config_store.acquire() as config:
        yield config


ConfigDep = Annotated[PygateConfig, Depends(get_config)]
