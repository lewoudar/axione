from pathlib import Path

import pytest

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
