import pandas as pd
from typing import Literal
import modules.p1_factor_research.schemas as schemas

def chronological_three_way_split(data_df: pd.DataFrame, touch_holdout: bool = False) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ...

def walk_forward_backtest(
    factor_spec: schemas.FactorSpec,
    price_panel: pd.DataFrame,
    window_type: Literal['rolling', 'expanding']
) -> pd.DataFrame:
    ...

def apply_transaction_cost(returns: pd.DataFrame, turnover: pd.Series, cost_bps: float = 10.0) -> pd.DataFrame:
    ...