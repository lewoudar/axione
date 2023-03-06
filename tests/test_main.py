import pytest

from axione.scraper import get_filtered_dataframe


@pytest.mark.parametrize(
    ('bad_input', 'key'),
    [
        ({'surface': 'foo'}, 'surface'),
        ({'maximum_price': 'foo'}, 'maximum_price'),
        ({'surface': -1}, 'surface'),
        ({'surface': 0}, 'surface'),
        ({'maximum_price': -1}, 'maximum_price'),
        ({'maximum_price': 0}, 'maximum_price'),
    ],
)
def test_should_return_400_error_when_payload_is_incorrect(client, bad_input, key):
    payload = {'department': '64', 'surface': 50, 'maximum_price': 800, **bad_input}
    response = client.post('/cities', json=payload)
    assert response.status_code == 422
    data = response.json()
    assert len(data['detail']) == 1
    assert data['detail'][0]['loc'] == ['body', key]


@pytest.mark.parametrize(
    'payload',
    [
        # for information, the test parquet file only has information for departments 64, 75 and 78
        {'department': '58', 'surface': 50, 'maximum_price': 1200},
        # no apartment in Paris with the given criteria
        {'department': '75', 'surface': 50, 'maximum_price': 1200},
    ],
)
def test_should_return_empty_list_if_criteria_does_not_match_any_row_in_apartment_file(client, mocker, payload):
    fetch_mock = mocker.patch('axione.concurrency.fetch_all_cities_data')
    response = client.post('/cities', json=payload)

    assert response.status_code == 200
    assert response.json() == []
    fetch_mock.assert_not_awaited()


def test_should_return_correct_payload_given_correct_input(client, respx_mock, mock_http_calls, settings):
    payload = {'department': '64', 'surface': 50, 'maximum_price': 1200}
    df = get_filtered_dataframe(settings.apartment_data_file, 50, 800, '64')
    mock_http_calls(df)
    response = client.post('/cities', json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 49
    assert len(respx_mock.calls) == 98

    # the second call should return cached data
    response = client.post('/cities', json=payload)
    assert response.status_code == 200
    assert len(response.json()) == 49
    # respx calls should not change from the previous call
    assert len(respx_mock.calls) == 98
