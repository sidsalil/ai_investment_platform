from typing import Literal
from datetime import date
import pandas as pd

async def get_price_history(tickers: list[str], start_date: date, end_date: date) -> dict[str, pd.DataFrame]:
    ...

async def get_universe_constituents(universe: Literal['NASDAQ100', 'SP500'], as_of_date: date) -> list[str]:
    ...

async def get_sector_classification(tickers: list[str]) -> dict[str, str]:
    ...