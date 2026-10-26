from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

YesNo = Literal["Yes", "No"]
YesNoSemTelefone = Literal["Yes", "No", "No phone service"]
YesNoSemInternet = Literal["Yes", "No", "No internet service"]
TipoInternet = Literal["DSL", "Fiber optic", "No"]
TipoContrato = Literal["Month-to-month", "One year", "Two year"]
TipoPagamento = Literal[
    "Bank transfer (automatic)",
    "Credit card (automatic)",
    "Electronic check",
    "Mailed check",
]


class CustomerChurn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerID")
    gender: Literal["Male", "Female"]
    senior_citizen: bool = Field(alias="SeniorCitizen")
    partner: YesNo = Field(alias="Partner")
    dependents: YesNo = Field(alias="Dependents")
    tenure: int = Field(ge=0)
    phone_service: YesNo = Field(alias="PhoneService")
    multiple_lines: YesNoSemTelefone = Field(alias="MultipleLines")
    internet_service: TipoInternet = Field(alias="InternetService")
    online_security: YesNoSemInternet = Field(alias="OnlineSecurity")
    online_backup: YesNoSemInternet = Field(alias="OnlineBackup")
    device_protection: YesNoSemInternet = Field(alias="DeviceProtection")
    tech_support: YesNoSemInternet = Field(alias="TechSupport")
    streaming_tv: YesNoSemInternet = Field(alias="StreamingTV")
    streaming_movies: YesNoSemInternet = Field(alias="StreamingMovies")
    contract: TipoContrato = Field(alias="Contract")
    paperless_billing: YesNo = Field(alias="PaperlessBilling")
    payment_method: TipoPagamento = Field(alias="PaymentMethod")
    monthly_charges: float = Field(alias="MonthlyCharges", ge=0)
    total_charges: float = Field(alias="TotalCharges", ge=0)

    def to_dict(self) -> dict:
        return self.model_dump(by_alias=True)