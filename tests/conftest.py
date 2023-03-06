import random
import typing
from pathlib import Path

import polars
import pytest
from fastapi.testclient import TestClient
from jinja2 import Environment, PackageLoader, select_autoescape

from axione.config import Settings, get_settings
from axione.main import app


@pytest.fixture
def anyio_backend() -> str:
    """Returns async backend used in tests, in our case it is always asyncio"""
    return 'asyncio'


@pytest.fixture(scope='session')
def settings() -> Settings:
    """Returns settings object used in tests"""
    test_dir = Path(__file__).parent
    parquet_file = test_dir / 'test_apartments.parquet'
    return Settings(apartment_data_file=parquet_file)


@pytest.fixture()
def client(settings) -> TestClient:
    """FastAPI test client"""
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


@pytest.fixture()
def get_page_content() -> typing.Callable[[str, float], str]:
    """Generates HTML to used scraping tests"""
    env = Environment(loader=PackageLoader('tests'), autoescape=select_autoescape())

    def _get_page_content(city: str, note: float) -> str:
        template = env.get_template('well_being.jinja2')
        return template.render(city=city, note=note)

    yield _get_page_content


@pytest.fixture()
def get_dummy_api_data() -> typing.Callable[[dict | None], dict]:
    """Gets dummy city api data"""

    def _get_dummy_api_data(payload: dict | None = None) -> dict:
        payload = {} if payload is None else payload
        return {
            'nom': 'Anglet',
            'code': '64024',
            'codesPostaux': ['64600'],
            'siren': '216400242',
            'codeEpci': '200067106',
            'codeDepartement': '64',
            'codeRegion': '75',
            'population': 39719,
            **payload,
        }

    yield _get_dummy_api_data


def get_random_note() -> float:
    return round(random.uniform(0, 5), 1)


@pytest.fixture()
def mock_http_calls(
    respx_mock, settings, get_dummy_api_data, get_page_content
) -> typing.Callable[[polars.DataFrame], None]:
    """Mocks different http calls to simulate city data fetching."""

    def _mock_http_calls(dataframe: polars.DataFrame) -> None:
        for item in dataframe.iter_rows(named=True):
            insee_code = item['INSEE']
            city = item['LIBGEO']
            # the zip code is not correct, but we never mind here
            payload = get_dummy_api_data({'code': insee_code, 'codesPostaux': [insee_code], 'nom': city})
            respx_mock.get(f'{settings.city_api_url}/{insee_code}') % dict(json=payload)
            html_content = get_page_content(city, get_random_note())
            respx_mock.get(f'{settings.well_being_city_url}/{city.lower()}-{insee_code}/') % dict(text=html_content)

    yield _mock_http_calls
