import logging
import sys
import time
import uuid
from typing import Callable


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def trace_id_middleware_factory(get_response: Callable):
    async def middleware(request, call_next):
        trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
        request.state.trace_id = trace_id
        start = time.time()
        try:
            response = await call_next(request)
        finally:
            duration_ms = int((time.time() - start) * 1000)
            logger = get_logger("request")
            logger.info(f"{request.method} {request.url.path} {duration_ms}ms trace_id={trace_id}")
        response.headers["X-Trace-Id"] = trace_id
        return response

    return middleware


