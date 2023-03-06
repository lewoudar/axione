import pathlib
from typing import Any

import anyio
import httpx
import polars
from anyio.abc import TaskGroup

from .scraper import fetch_city_api_data, fetch_city_note
from .logger import get_logger

logger = get_logger(__name__)


async def fetch_city_data(
    client: httpx.AsyncClient, tmp_file: pathlib.Path, item: dict[str, Any], limiter: anyio.CapacityLimiter
) -> None:
    # The geo API does not like when we hit it too quickly, so we will delay a bit
    # and we do the same thing for the well-being website
    logger.debug('fetching city data for item %s', item)
    async with limiter:
        city_data = await fetch_city_api_data(client, item['INSEE'])
        note = await fetch_city_note(client, city_data.name, city_data.code)
        with tmp_file.open('a') as file:
            file.write(f'{note},{city_data.code},{city_data.population},{city_data.zip_codes[0]}\n')


async def fetch_all_cities_data(
    task_group: TaskGroup, dataframe: polars.DataFrame, client: httpx.AsyncClient, tmp_file: pathlib.Path
) -> None:
    logger.debug('spawning multiple tasks for dataframe of shape %s', dataframe.shape)
    limiter = anyio.CapacityLimiter(5)
    for item in dataframe.iter_rows(named=True):
        task_group.start_soon(fetch_city_data, client, tmp_file, item, limiter)
