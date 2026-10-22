from fastapi import FastAPI

from churn.router import health, predict

app = FastAPI()

app.include_router(health.router)
app.include_router(predict.router)