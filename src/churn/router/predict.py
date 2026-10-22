from fastapi import APIRouter, status

from churn.schemas import CustomerChurn

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/", response_model=CustomerChurn, status_code=status.HTTP_200_OK)
async def predict(request: CustomerChurn) -> CustomerChurn:
    return request
