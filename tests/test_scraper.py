from axione.scraper import get_filtered_dataframe


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
