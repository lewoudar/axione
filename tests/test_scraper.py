import httpx
import pytest

from axione.schemas import RawCity
from axione.scraper import fetch_city_api_data, fetch_city_note, get_filtered_dataframe


class TestGetFilteredDataFrame:
    """Tests function get_filtered_dataframe"""

    def test_should_return_empty_dataframe_when_department_not_found(self, settings):
        # test parquet files contains data for departments 64, 75 and 78
        df = get_filtered_dataframe(settings.apartment_data_file, 50, 800, '77')
        assert df.is_empty()

    def test_should_return_empty_dataframe_when_criteria_does_not_match_any_row(self, settings):
        # obviously, you will not find 50m2 with 1200 € in Paris :D
        df = get_filtered_dataframe(settings.apartment_data_file, 50, 1200, '75')
        assert df.is_empty()

    def test_should_return_correct_dataframe_given_correct_input(self, settings):
        df = get_filtered_dataframe(settings.apartment_data_file, 50, 800, '64')
        assert df.shape == (49, 5)


@pytest.mark.anyio
class TestFetchCityApiData:
    """Tests function fetch_city_api_data"""

    async def test_should_return_dummy_data_when_unable_to_fetch_city_data(self, respx_mock, settings):
        insee_code = '64065'
        respx_mock.get(f'{settings.city_api_url}/{insee_code}') % dict(status_code=400, content='nothing for you!')

        async with httpx.AsyncClient() as client:
            city = await fetch_city_api_data(client, insee_code)

        assert city == RawCity(nom='N/A', codesPostaux=['N/A'], code='N/A', codeDepartement='N/A', population=0)

    async def test_should_return_city_object_when_data_is_fetched_correctly(
        self, respx_mock, get_dummy_api_data, settings
    ):
        payload = get_dummy_api_data({})
        insee_code = '64024'
        respx_mock.get(f'{settings.city_api_url}/{insee_code}') % dict(json=payload)
        async with httpx.AsyncClient() as client:
            city = await fetch_city_api_data(client, insee_code)

        assert RawCity(**payload) == city


@pytest.mark.anyio
class TestFetchCityNote:
    """Tests function fetch_city_note"""

    async def test_should_return_negative_value_when_unable_to_fetch_data(self, respx_mock, settings):
        respx_mock.get(f'{settings.well_being_city_url}/anglet-64024/') % dict(status_code=404, text='No content found')
        async with httpx.AsyncClient() as client:
            note = await fetch_city_note(client, 'Anglet', '64024')
            assert note == -1

    async def test_should_return_global_note_after_fetching_html_page(self, respx_mock, settings, get_page_content):
        html_content = get_page_content('Anglet', 3.9)
        respx_mock.get(f'{settings.well_being_city_url}/anglet-64024/') % dict(text=html_content)
        async with httpx.AsyncClient() as client:
            note = await fetch_city_note(client, 'Anglet', '64024')

        assert note == 3.9
