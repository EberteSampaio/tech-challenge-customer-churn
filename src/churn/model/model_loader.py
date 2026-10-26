import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from imblearn.pipeline import Pipeline

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[3] / "models" / "churn_model.joblib"


@dataclass(frozen=True)
class ChurnModel:
    pipeline: Pipeline
    limiar: float
    columns: list[str]

    def align(self, df: pd.DataFrame) -> pd.DataFrame:
        unexpected = set(df.columns) - set(self.columns)
        if unexpected:
            raise ValueError(f"Categorias desconhecidas geraram as colunas: {sorted(unexpected)}")
        return df.reindex(columns=self.columns, fill_value=0)

    def proba(self, df: pd.DataFrame) -> float:
        return float(self.pipeline.predict_proba(self.align(df))[0, 1])


def load_churn_model(model_path: Optional[Path] = None) -> ChurnModel:
    model_path = Path(model_path or os.getenv("CHURN_MODEL_PATH") or DEFAULT_MODEL_PATH)

    if not model_path.exists():
        raise FileNotFoundError(f"Modelo não encontrado em {model_path}")

    artifact = joblib.load(model_path)

    missing = {"modelo", "limiar", "colunas"} - artifact.keys()
    if missing:
        raise ValueError(f"Artefato inválido, chaves faltando: {sorted(missing)}")

    return ChurnModel(
        pipeline=artifact["modelo"],
        limiar=float(artifact["limiar"]),
        columns=list(artifact["colunas"]),
    )


@lru_cache(maxsize=1)
def get_model() -> ChurnModel:
    return load_churn_model()
