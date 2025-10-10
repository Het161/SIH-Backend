from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
from app.db.models.access_log import APIAccessLog


class AccessLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_session):
        super().__init__(app)
        self.db = db_session

    async def dispatch(self, request: Request, call_next: Callable):
        response: Response = await call_next(request)

        # Extract user from request state (set by auth middleware)
        user = getattr(request.state, "user", None)
        role = getattr(user, "role", "anonymous") if user else "anonymous"
        path = request.url.path
        method = request.method

        # Log API access into database
        log_entry = APIAccessLog(user_role=role, path=path, method=method)
        self.db.add(log_entry)
        self.db.commit()

        return response
