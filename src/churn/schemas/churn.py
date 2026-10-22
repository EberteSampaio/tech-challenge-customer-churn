from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

YesNo = Literal["Yes", "No"]


class CustomerChurn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerID")
    gender: Literal["Male", "Female"]
    senior_citizen: bool = Field(alias="SeniorCitizen")
    partner: YesNo = Field(alias="Partner")
    dependents: YesNo = Field(alias="Dependents")
    tenure: int
    phone_service: YesNo = Field(alias="PhoneService")
    multiple_lines: str = Field(alias="MultipleLines")
    internet_service: str = Field(alias="InternetService")
    online_security: str = Field(alias="OnlineSecurity")
    online_backup: str = Field(alias="OnlineBackup")
    device_protection: str = Field(alias="DeviceProtection")
    tech_support: str = Field(alias="TechSupport")
    streaming_tv: str = Field(alias="StreamingTV")
    streaming_movies: str = Field(alias="StreamingMovies")
    contract: str = Field(alias="Contract")
    paperless_billing: YesNo = Field(alias="PaperlessBilling")
    payment_method: str = Field(alias="PaymentMethod")
    monthly_charges: float = Field(alias="MonthlyCharges")
    total_charges: float = Field(alias="TotalCharges")
