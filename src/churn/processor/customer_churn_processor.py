import logging

import pandas as pd

from churn.cleaning import ColumnMapper, Mappings

logger = logging.getLogger(__name__)


class CustomerChurnProcessor:

    def apply_raw_cleaning_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        return df

    def apply_raw_mapping_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = ColumnMapper(["PhoneService", "PaperlessBilling", "Partner", "Dependents", "Churn"],
                          Mappings.YES_NO).transform(df)
        df = ColumnMapper(["MultipleLines"], Mappings.PHONE).transform(df)
        df = ColumnMapper(Mappings.INTERNET_SERVICE, Mappings.INTERNET).transform(df)
        df = ColumnMapper(['gender'], {"Male": 0, "Female": 1}).transform(df)

        return df

    def apply_raw_categorical_encoding(self, df: pd.DataFrame) -> pd.DataFrame:
        df = pd.get_dummies(df, columns=["PaymentMethod", "InternetService", "Contract"], dtype=int)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.apply_raw_cleaning_data(df)
        df = self.apply_raw_mapping_data(df)
        df = self.apply_raw_categorical_encoding(df)

        return df
