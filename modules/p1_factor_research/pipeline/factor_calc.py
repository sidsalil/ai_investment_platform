import pandas as pd
from typing import Literal

def compute_raw_factor(
    price_df: pd.DataFrame,
    factor_type: Literal['momentum', 'value', 'volatility', 'liquidity'],
    lookbak_months: int,
    exclusion_months: int = 0
) -> pd.Series:
    ...

def winsorize(raw_factor: pd.Series, lower_pct: float = 0.01, upper_pct: float = 0.99) -> pd.Series:
    ...

def sector_neutral_z_score(winsorized_factor: pd.Series, sector_map: dict[str, str]) -> pd.Series:
    ...

def universe_wide_z_score(winsorized_factor: pd.Series) -> pd.Series:
    ...