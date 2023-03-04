from pathlib import Path

import pytest


@pytest.fixture(scope='session')
def parquet_file() -> Path:
    """Returns Pathlib.Path to parquet file used in tests"""
    test_dir = Path(__file__).parent
    return test_dir / 'test_apartments.parquet'
