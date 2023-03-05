from cachetools import cached
from pydantic import BaseSettings, HttpUrl


class Settings(BaseSettings):
    CITY_API_URL: HttpUrl = 'https://api.gouv.fr/documentation/api-geo/communes'
    WELL_BEING_CITY_URL: HttpUrl = 'https://www.bien-dans-ma-ville.fr'

    class Config:
        env_prefix = 'axione_'


@cached(cache={})
def get_settings() -> Settings:
    return Settings()
