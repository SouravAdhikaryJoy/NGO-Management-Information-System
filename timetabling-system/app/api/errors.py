"""Structured JSON errors for every endpoint (never raw exceptions)."""

from fastapi import HTTPException
from fastapi.responses import JSONResponse


def api_error(status_code: int, code: str, message: str, details: list | None = None):
    return HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message, "details": details or []},
    )


def install_error_handlers(app):
    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        detail = exc.detail
        if not isinstance(detail, dict) or "code" not in detail:
            detail = {"code": "http_error", "message": str(detail), "details": []}
        return JSONResponse(status_code=exc.status_code, content={"error": detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"error": {
                "code": "validation_error",
                "message": "request validation failed",
                "details": exc.errors(),
            }},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": {
                "code": "internal_error",
                "message": f"{type(exc).__name__}: {exc}",
                "details": [],
            }},
        )
