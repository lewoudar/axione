import pathlib

from cachetools import cached
from pydantic import BaseSettings, FilePath, HttpUrl


class Settings(BaseSettings):
    city_api_url: HttpUrl = 'https://api.gouv.fr/documentation/api-geo/communes'
    well_being_city_url: HttpUrl = 'https://www.bien-dans-ma-ville.fr'
    apartment_data_file: FilePath = pathlib.Path(__file__).parent / 'apartment.parquet'

    class Config:
        env_prefix = 'axione_'


@cached(cache={})
def get_settings() -> Settings:
    return Settings()
