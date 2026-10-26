from io import StringIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from churn.main import app
from churn.model import get_model
from churn.processor import CustomerChurnProcessor

CSV = """customerID,gender,SeniorCitizen,MultipleLines,Partner,Dependents,tenure,PhoneService,InternetService,OnlineSecurity,OnlineBackup,DeviceProtection,TechSupport,StreamingTV,StreamingMovies,Contract,PaperlessBilling,PaymentMethod,MonthlyCharges,TotalCharges
7590-VHVEG,Female,0,No phone service,Yes,No,1,No,DSL,No,Yes,No,No,No,No,Month-to-month,Yes,Electronic check,29.85,29.85"""


@pytest.fixture
def df():
    return pd.read_csv(StringIO(CSV))


@pytest.fixture
def payload():
    return {
        "customerID": "7590-VHVEG",
        "gender": "Female",
        "SeniorCitizen": False,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "No",
        "MultipleLines": "No phone service",
        "InternetService": "DSL",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 29.85,
        "TotalCharges": 29.85,
    }


@pytest.fixture
def processor():
    return CustomerChurnProcessor()


@pytest.fixture
def model():
    return get_model()


@pytest.fixture
def client():
    return TestClient(app)
