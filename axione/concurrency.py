from typing import Any, TextIO

import httpx
import polars
from anyio.abc import TaskGroup

from .scraper import fetch_city_api_data, fetch_city_note


async def fetch_city_data(client: httpx.AsyncClient, file: TextIO, item: dict[str, Any]) -> None:
    city_data = await fetch_city_api_data(client, item['INSEE'])
    note = await fetch_city_note(client, city_data.name, city_data.code)
    file.write(f'{note},{city_data.code},{city_data.population},{city_data.zip_codes[0]}\n')


async def fetch_all_cities_data(
    task_group: TaskGroup, dataframe: polars.DataFrame, client: httpx.AsyncClient, tmp_file: TextIO
) -> None:
    for item in dataframe.iter_rows(named=True):
        task_group.start_soon(fetch_city_data, client, tmp_file, item)
