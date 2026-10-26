import pandas as pd
from fastapi import Depends

from churn.model import ChurnModel, get_model
from churn.processor import CustomerChurnProcessor
from churn.schemas import CustomerChurn, ChurnResponse


class PredictService:
    def __init__(
            self,
            churn_processor: CustomerChurnProcessor = Depends(CustomerChurnProcessor),
            model: ChurnModel = Depends(get_model),
    ) -> None:
        self.churn_processor = churn_processor
        self.model = model

    def predict(self, request: CustomerChurn) -> ChurnResponse:
        df = pd.DataFrame([request.to_dict()])
        df = self.churn_processor.transform(df=df)
        proba = self.model.proba(df)

        return ChurnResponse(
            churn=proba >= self.model.limiar,
            proba=proba,
            limiar=self.model.limiar,
        )
