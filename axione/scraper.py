import pathlib

import polars as pl


def get_filtered_dataframe(filename: pathlib.Path | str, surface: float, maximum_price: float,
                           department: str) -> pl.DataFrame:
    df = pl.scan_parquet(filename)
    return (
        df.with_columns(pl.col('loypredm2').str.replace(',', '.').cast(pl.Float64).alias('rent_per_m2'))
        .select([pl.col('rent_per_m2').round(2), pl.col('LIBGEO'), pl.col('TYPPRED'), pl.col('INSEE'), pl.col('DEP')])
        .filter(
            (pl.col('rent_per_m2') * surface <= maximum_price)
            & (pl.col('TYPPRED') == 'commune')
            & (pl.col('DEP') == department)
        )
        .collect()
    )
