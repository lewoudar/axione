import httpx
import pytest
from fastapi.exceptions import HTTPException

from axione.schemas import RawCity
from axione.scraper import fetch_city_data, get_filtered_dataframe


def test_should_return_empty_dataframe_when_department_not_found(parquet_file):
    # test parquet files contains data for departments 64, 75 and 78
    df = get_filtered_dataframe(parquet_file, 50, 800, '77')
    assert df.is_empty()


def test_should_return_empty_dataframe_when_criteria_does_not_match_any_row(parquet_file):
    # obviously, you will not find 50m2 with 1200 € in Paris :D
    df = get_filtered_dataframe(parquet_file, 50, 1200, '75')
    assert df.is_empty()


def test_should_return_correct_dataframe_given_correct_input(parquet_file):
    df = get_filtered_dataframe(parquet_file, 50, 800, '64')
    assert df.shape == (49, 5)


@pytest.mark.anyio
class TestFetchCityData:
    """Tests function fetch_city_data"""

    async def test_should_return_503_http_error_when_unable_to_fetch_data(self, settings, respx_mock):
        insee_code = '64065'
        respx_mock.get(f'{settings.CITY_API_URL}/{insee_code}') % dict(status_code=400, content='nothing for you!')

        with pytest.raises(HTTPException) as exc:
            async with httpx.AsyncClient() as client:
                await fetch_city_data(client, insee_code)

        assert exc.value.status_code == 503
        assert exc.value.detail == f'Unable to fetch data for city with insee code {insee_code}'

    async def test_should_return_city_object_when_data_is_fetched_correctly(self, settings, respx_mock):
        insee_code = '64024'
        payload = {
            'nom': 'Anglet',
            'code': insee_code,
            'codesPostaux': ['64600'],
            'siren': '216400242',
            'codeEpci': '200067106',
            'codeDepartement': '64',
            'codeRegion': '75',
            'population': 39719,
        }
        respx_mock.get(f'{settings.CITY_API_URL}/{insee_code}') % dict(json=payload)
        async with httpx.AsyncClient() as client:
            city = await fetch_city_data(client, insee_code)

        assert RawCity(**payload) == city
