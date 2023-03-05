import typing
from pathlib import Path

import pytest
from jinja2 import Environment, PackageLoader, select_autoescape

from axione.config import Settings


@pytest.fixture(scope='session')
def parquet_file() -> Path:
    """Returns Pathlib.Path to parquet file used in tests"""
    test_dir = Path(__file__).parent
    return test_dir / 'test_apartments.parquet'


@pytest.fixture
def anyio_backend() -> str:
    """Returns async backend used in tests, in our case it is always asyncio"""
    return 'asyncio'


@pytest.fixture(scope='session')
def settings() -> Settings:
    """Returns settings object used in tests"""
    return Settings()


@pytest.fixture()
def get_page_content() -> typing.Callable[[str, float], str]:
    """Generates HTML to used scraping tests"""
    env = Environment(loader=PackageLoader('tests'), autoescape=select_autoescape())

    def _get_page_content(city: str, note: float) -> str:
        template = env.get_template('well_being.jinja2')
        return template.render(city=city, note=note)

    yield _get_page_content
