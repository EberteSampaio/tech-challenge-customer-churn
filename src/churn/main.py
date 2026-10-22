from fastapi import FastAPI

from churn.middleware import LoggingMiddleware
from churn.router import health, predict
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # a mensagem já é um JSON completo
)
app = FastAPI()

app.add_middleware(middleware_class=LoggingMiddleware)
app.include_router(health.router)
app.include_router(predict.router)