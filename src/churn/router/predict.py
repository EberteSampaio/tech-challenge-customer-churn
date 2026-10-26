from fastapi import APIRouter, status, Depends, HTTPException

from churn.schemas import CustomerChurn, ChurnResponse
from churn.service import PredictService

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/", status_code=status.HTTP_200_OK)
def predict(request: CustomerChurn, service: PredictService = Depends(PredictService)) -> ChurnResponse:
    try:
        return service.predict(request)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
