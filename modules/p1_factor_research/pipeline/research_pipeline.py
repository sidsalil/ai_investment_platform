import modules.p1_factor_research.schemas as schemas

def run_research_pipeline(factor_spec: schemas.FactorSpec) -> tuple[schemas.FactorMetricsResult, schemas.RunMetadata]:
    ...