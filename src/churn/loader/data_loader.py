import logging
from logging import Logger
from pathlib import Path

import pandas as pd

logger: Logger = logging.getLogger(__name__)

class DataLoader:
    """ Classe auxiliar para carregar o dataset"""
    def __init__(self, data_path: str) -> None:
        self.data_path: Path = Path(data_path)

    def load(self) -> pd.DataFrame:
        if not self.data_path.exists():
            raise FileNotFoundError("{} Não existe".format(str(self.data_path)))

        try:
            df: pd.DataFrame = pd.read_csv(self.data_path)

            if df.empty:
                raise ValueError("Arquivo Vazio")

            logger.info("Dados carregados: {} registros de {}".format(len(df), str(self.data_path)))

            return df

        except FileNotFoundError:
            raise ValueError("Arquivo Vazio")
        except Exception as e:
            raise ValueError("Erro ao ler o arquivo: {}".format(e))