from fastapi import APIRouter, status

from churn.schemas import Churn

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/", response_model=Churn, status_code=status.HTTP_200_OK)
async def predict(request: Churn) -> Churn:
    return request
