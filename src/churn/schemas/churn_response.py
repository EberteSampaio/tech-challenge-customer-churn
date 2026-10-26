from pydantic import BaseModel


class ChurnResponse(BaseModel):
    churn: bool
    proba: float
    limiar: float