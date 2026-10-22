from typing import Literal

from pydantic import BaseModel


class Churn(BaseModel):
    customer_id: str
    gender: Literal["Male", "Female"]
    senior_citizen: bool
    multiple_lines: str
    partner: str
    dependents: str
    tenure: int
    phone_service: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float | int
    TotalCharges: float | int
