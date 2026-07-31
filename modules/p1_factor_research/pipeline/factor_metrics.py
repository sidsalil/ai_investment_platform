import pandas as pd
import modules.p1_factor_research.schemas as schemas
from typing import Literal

def compute_ic(factor_scores: pd.Series, forward_returns: pd.Series, method: Literal['pearson', 'spearman'] = 'pearson') -> float:
    ...

def compute_factor_metrics(backtest_results: pd.DataFrame, split: Literal['in_sample', 'out_of_sample', 'hold_out']) -> schemas.FactorMetricsResult:
    ...