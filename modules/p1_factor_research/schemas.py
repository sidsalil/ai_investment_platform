from pydantic import BaseModel, Field
from typing import Literal, Annotated


class FactorSpec(BaseModel):
    """
    Example:
        hypothesis_text: "Test 12-month momentum on the NASDAQ-100"
        factor_type: "momentum"
        universe: "NASDAQ100"
        lookback_months: 12
        exclusion_months: 1 # 12 months lookback plus 1 extra month to exclude
        exclusion_criteria:	None
        rebalance_frequency: "monthly"
        long_short:	True
    """
    hypothesis_text: str
    factor_type: Literal['momentum', 'volatility', 'liquidity', 'value']
    universe: Literal['NASDAQ100', 'SP500']
    lookback_months: int = Field(ge=1)
    exclusion_months: int = Field(default=0, ge=0)
    exclusion_criteria: list[str] | None=None
    rebalance_frequency: Literal['monthly', 'weekly', 'daily'] = 'monthly'
    long_short: bool = True

class FactorMetricsResult(BaseModel):
    ic_mean: float
    ic_stat: float
    rank_ic_mean: float
    hit_rate: float = Field(ge=0, le=1)
    sharpe: float
    sortino: float
    max_drawdown: float # negative example -0.23 means 23% drawdown
    calmar: float
    beta_to_market: float
    beta_long_leg: float
    beta_short_leg: float
    turnover_cost_drag_bps: float
    holdout_split: Literal['in_sample', 'out_of_sample', 'holdout']

class RunMetadata(BaseModel):
    variants_tested: int = Field(ge=1)
    holdout_touched: bool
    universe_wide_zscore_diff: float | None
    walk_forward_window_type: Literal['rolling', 'expanding']
    # rolling = 12 month window. As 13 month comes into the window the first month drops out thus ensuring entire window size is always 12 months long.
    # expanding = start with (say) 12 month window. But as 13 month comes the window size increases from 12 to 13 and so on and so forth

class ValidationResult(BaseModel):
    passed: bool
    flags: list[str]
    severity: Literal['none', 'advisory', 'blocking']

class MemoResult(BaseModel):
    memo_markdown: str
    disclosed_flags: list[str]
    word_count: int = Field(ge=0)

class ValidatorCallResult(BaseModel):
    agent: Literal['validator_subagent']
    status: Literal['ok', 'failed']
    retries_used: int = Field(ge=0)
    error_summary: str | None
    result: ValidationResult | None

class MemoCallResult(BaseModel):
    agent: Literal['memo_subagent']
    status: Literal['ok', 'failed']
    retires_used: int = Field(ge=0)
    error_summary: str | None
    result: MemoResult | None

SubAgentCallResult = Annotated[
    ValidatorCallResult | MemoResult,
    Field(discriminator='agent')
]