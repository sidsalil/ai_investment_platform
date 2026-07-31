import pandas as pd

def bucket_into_quintiles(zscored_factor: pd.Series, n_buckets: int = 5) -> pd.Series:
    ...

def build_long_short_weights(bucketed: pd.Series) -> pd.Series:
    ...

def build_long_only_weights(bucketed: pd.Series) -> pd.Series:
    ...
