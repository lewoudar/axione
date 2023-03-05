import random

import anyio
import httpx
import pytest

from axione.concurrency import fetch_all_cities_data, fetch_city_data
from axione.scraper import get_filtered_dataframe

pytestmark = pytest.mark.anyio


def get_random_note() -> float:
    return round(random.uniform(0, 5), 1)


class TestFetchCityData:
    """Tests function fetch_city_data"""

    async def test_should_write_csv_file_given_correct_input(
        self, tmp_path, respx_mock, settings, get_page_content, get_dummy_api_data
    ):
        csv_file = tmp_path / 'file.csv'
        csv_file.write_text('note,INSEE,population,zip_code\n')
        insee_code = '64024'
        payload = get_dummy_api_data({'code': insee_code, 'codesPostaux': ['64600']})
        respx_mock.get(f'{settings.city_api_url}/{insee_code}') % dict(json=payload)
        html_content = get_page_content('Anglet', 3.9)
        respx_mock.get(f'{settings.well_being_city_url}/anglet-64024/') % dict(text=html_content)

        async with httpx.AsyncClient() as client:
            await fetch_city_data(client, csv_file.open('a'), {'INSEE': insee_code})

        assert csv_file.read_text() == f'note,INSEE,population,zip_code\n3.9,{insee_code},39719,64600\n'


class TestFetchAllCitiesData:
    """Tests function fetch_all_cities_data"""

    async def test_should_write_csv_file_like_expected(
        self, tmp_path, settings, respx_mock, get_dummy_api_data, get_page_content
    ):
        csv_file = tmp_path / 'file.csv'
        csv_file.write_text('note,INSEE,population,zip_code\n')
        df = get_filtered_dataframe(settings.apartment_data_file, 50, 800, '64')
        for item in df.iter_rows(named=True):
            insee_code = item['INSEE']
            city = item['LIBGEO']
            # the zip code is not correct, but we never mind here
            payload = get_dummy_api_data({'code': insee_code, 'codesPostaux': [insee_code], 'nom': city})
            respx_mock.get(f'{settings.city_api_url}/{insee_code}') % dict(json=payload)
            html_content = get_page_content(city, get_random_note())
            respx_mock.get(f'{settings.well_being_city_url}/{city.lower()}-{insee_code}/') % dict(text=html_content)

        client = httpx.AsyncClient()
        file = csv_file.open('a+')
        async with anyio.create_task_group() as tg:
            await fetch_all_cities_data(tg, df, client, file)

        file.seek(0)
        lines = [line for line in file]
        assert len(lines) == df.shape[0] + 1
        # Anglet city
        assert '64024,39719,64024' in lines[2]

        file.close()
        await client.aclose()
