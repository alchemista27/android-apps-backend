from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.logger import logger
import time
import uuid

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Time: {process_time:.2f}ms"
            )

            return response
            
        except Exception as e:
            logger.exception(
                f"[{request_id}] Exception handling {request.method} {request.url.path}: {str(e)}"
            )