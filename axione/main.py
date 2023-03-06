# ruff: noqa: B008
from pathlib import Path

import anyio
import httpx
import polars as pl
from cachetools import TTLCache
from fastapi import Depends, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from .concurrency import fetch_all_cities_data
from .config import Settings, get_settings
from .dependencies import get_httpx_client, get_temporary_file
from .schemas import City, Input
from .scraper import get_filtered_dataframe

app = FastAPI(title='Axione test', version='0.1.0', redoc_url=None, description='Rent price comparator by department')
settings = get_settings()
# In a production environment, we probably want to use something like redis, but for this quick exercise
# we will stick with this poor man solution :)
cache = TTLCache(maxsize=settings.cache_maxsize, ttl=settings.cache_ttl)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error('bad input sent, detail: {}', exc.errors())
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({'detail': exc.errors()}),
    )


@app.post('/cities', response_model=list[City], responses={'422': {'description': 'Payload incorrect'}})
async def get_cities_info(
        input_data: Input,
        httpx_client: httpx.AsyncClient = Depends(get_httpx_client),
        temporary_file: Path = Depends(get_temporary_file),
        settings: Settings = Depends(get_settings),
):
    if input_data.identifier in cache:
        logger.info('returning data in cache for identifier {}', input_data.identifier)
        return cache[input_data.identifier]

    dataframe = get_filtered_dataframe(
        settings.apartment_data_file, input_data.surface, input_data.maximum_price, input_data.department
    )
    if dataframe.is_empty():
        logger.info('no data corresponding to the given criteria: {}', input_data.dict())
        cache[input_data.identifier] = []
        return []

    async with anyio.create_task_group() as tg:
        logger.debug('fetching city information')
        await fetch_all_cities_data(tg, dataframe, httpx_client, temporary_file)

    dtypes = {'INSEE': pl.Utf8, 'note': pl.Float64, 'population': pl.Int64, 'zip_code': pl.Utf8}
    csv_dataframe = pl.read_csv(temporary_file, dtypes=dtypes)
    dataframe = dataframe.join(csv_dataframe, left_on='INSEE', right_on='INSEE').sort(
        ['note', 'LIBGEO'], descending=True
    )
    cities = []
    dict_cities = []
    for item in dataframe.iter_rows(named=True):
        city = City(
            average_price=item['rent_per_m2'],
            city=item['LIBGEO'],
            note=item['note'],
            zip_code=item['zip_code'],
            population=item['population'],
        )
        dict_cities.append(city.dict())
        cities.append(city)

    logger.info('caching and returning {} items found', len(cities))
    cache[input_data.identifier] = dict_cities
    return cities
