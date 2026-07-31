import modules.p1_factor_research.schemas as schemas

def extract_factor_spec(user_query: str) -> schemas.FactorSpec:
    ...

def invoke_validator_subagent(
    factor_spec: schemas.FactorSpec,
    factor_metrics_result: schemas.FactorMetricsResult,
    run_metadata: schemas.RunMetadata
) -> schemas.SubAgentCallResult:
    ...

def invoke_memo_subagent(
    factor_spec: schemas.FactorSpec,
    factor_metrics_result: schemas.FactorMetricsResult,
    validation_result: schemas.ValidationResult
) -> schemas.SubAgentCallResult:
    ...

def run_orschestrator(user_query: str) -> schemas.MemoResult | schemas.ValidationResult:
    ...