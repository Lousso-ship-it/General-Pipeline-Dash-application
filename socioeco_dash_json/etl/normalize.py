
import pandas as pd

def min_max_normalize(df: pd.DataFrame, value_col="value", group_cols=("date",), invert=False) -> pd.Series:
    grp = df.groupby(list(group_cols))[value_col]
    minv = grp.transform("min")
    maxv = grp.transform("max")
    rng = (maxv - minv).replace(0, 1.0)
    norm = (df[value_col] - minv) / rng
    if invert:
        norm = 1 - norm
    return norm
