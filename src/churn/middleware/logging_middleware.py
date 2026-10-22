import json
import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

MAX_BODY_LOG = 10_000


def _decode(body: bytes) -> str:
    text = body[:MAX_BODY_LOG].decode("utf-8", errors="replace")
    return text + ("...[truncado]" if len(body) > MAX_BODY_LOG else "")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        request_body = await request.body()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(json.dumps({
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            }))
            raise

        response_body = b"".join([chunk async for chunk in response.body_iterator])

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "request_payload": _decode(request_body),
            "response_payload": _decode(response_body),
            "status_code": response.status_code,
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }
        logger.info(json.dumps(record, ensure_ascii=False))

        async def _body_iterator():
            yield response_body

        response.body_iterator = _body_iterator()
        response.headers["X-Request-ID"] = request_id
        return response