import modules.p1_factor_research.schemas as schemas

def generate_memo(
    factor_spec: schemas.FactorSpec,
    factor_metrics_result: schemas.FactorMetricsResult,
    validation_result: schemas.ValidationResult
) -> schemas.MemoResult:
    ...