import typing
from pathlib import Path

import pytest
from jinja2 import Environment, PackageLoader, select_autoescape

from axione.config import Settings


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
