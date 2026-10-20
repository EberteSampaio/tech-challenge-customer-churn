import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


class ColumnMapper(BaseEstimator, TransformerMixin):

    def __init__(self, columns: list[str], mapper: dict, dtype: type = int):
        self.columns = columns
        self.mapper = mapper
        self.dtype = dtype

    def fit(self, df: pd.DataFrame, y=None):
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for column in self.columns:
            mapped = df[column].map(self.mapper)
            unmapped = df.loc[mapped.isna() & df[column].notna(), column].unique()
            if len(unmapped) > 0:
                raise ValueError(f"Valores não mapeados em '{column}': {list(unmapped)}")
            df[column] = mapped.astype(self.dtype)
        return df
