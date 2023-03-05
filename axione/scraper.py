import pathlib

import httpx
import polars as pl
from fastapi import HTTPException
from parsel import Selector

from .config import get_settings
from .schemas import RawCity


def get_filtered_dataframe(
    filename: pathlib.Path | str, surface: float, maximum_price: float, department: str
) -> pl.DataFrame:
    df = pl.scan_parquet(filename)
    return (
        df.with_columns(pl.col('loypredm2').str.replace(',', '.').cast(pl.Float64).alias('rent_per_m2'))
        .select([pl.col('rent_per_m2').round(2), pl.col('LIBGEO'), pl.col('TYPPRED'), pl.col('INSEE'), pl.col('DEP')])
        .filter(
            (pl.col('rent_per_m2') * surface <= maximum_price)
            & (pl.col('TYPPRED') == 'commune')
            & (pl.col('DEP') == department)
        )
        .collect()
    )


async def fetch_city_data(client: httpx.AsyncClient, insee_code: str) -> RawCity:
    settings = get_settings()
    response = await client.get(f'{settings.CITY_API_URL}/{insee_code}')
    if response.status_code >= 400:
        raise HTTPException(status_code=503, detail=f'Unable to fetch data for city with insee code {insee_code}')
    return RawCity(**response.json())


async def fetch_city_note(client: httpx.AsyncClient, city: str, zip_code: str) -> float:
    settings = get_settings()
    response = await client.get(f'{settings.WELL_BEING_CITY_URL}/{city.lower()}-{zip_code}/')
    if response.status_code >= 400:
        raise HTTPException(
            status_code=503, detail=f'Unable to fetch global note for city {city} and zip code {zip_code}'
        )

    selector = Selector(response.text)
    str_note = selector.css('h3 + div.total::text').get()
    return float(str_note)
