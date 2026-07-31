import modules.p1_factor_research.schemas as schemas

def validate_methodology(
    factor_spec: schemas.FactorSpec,
    factor_metrics_result: schemas.FactorMetricsResult,
    run_metadata: schemas.RunMetadata
) -> schemas.ValidationResult:
    """
    answers:    "given these inputs, what's the validation verdict (I need direct answer no bull shit)?" — one Claude API call, one parse attempt, one business fact produced.
                Thats why it returns schemas.ValidationResult

    on the other hand

    orschestrator.invoke_validator_subagent()
    answers:    "manage a call to that function that might fail transiently, and report the outcome including how it went." —
                retry counting, deciding when a transient failure becomes terminal, wrapping the result.
                Thats why it returns schemas.SubAgentCallResult
    """