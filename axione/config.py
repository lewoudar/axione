from cachetools import cached
from pydantic import BaseSettings, HttpUrl


class Settings(BaseSettings):
    CITY_API_URL: HttpUrl = 'https://api.gouv.fr/documentation/api-geo/communes'


@cached(cache={})
def get_settings() -> Settings:
    return Settings()
