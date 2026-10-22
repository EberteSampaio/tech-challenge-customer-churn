from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["Health"])


class HealthCheck(BaseModel):
    status: str


@router.get("/", status_code=status.HTTP_200_OK, response_model=HealthCheck)
async def health() -> HealthCheck:
    return HealthCheck(status="ok")
