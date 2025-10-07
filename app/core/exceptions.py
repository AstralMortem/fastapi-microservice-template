from app.conf import settings
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status


def register_exception(app: FastAPI):
    """Register custom exception handlers."""
    @app.exception_handler(ServiceError)
    async def service_error_handler(request, exc: ServiceError):
        return exc.to_response()


class ServiceError(Exception):
    def __init__(
        self,
        code: int,
        title: str,
        message: str | None = None,
        debug: str | Exception | None = None,
        headers: dict | None = None,
    ):
        self.code = code
        self.title = title
        self.message = message
        self.debug = debug
        self.headers = headers or {}

    def to_response(self):
        payload = {
            "status_code": self.code,
            "title": self.title,
            "message": self.message,
        }

        if settings.DEBUG and self.debug:
            payload["debug"] = str(self.debug)

        return JSONResponse(
            content=payload, status_code=self.code, headers=self.headers
        )

    def __repr__(self):
        return f"<ServiceError [{self.code}] {self.title}>"


# JWT Errors


class InvalidToken(ServiceError):
    def __init__(self, message: str, title: str = "Invalid token"):
        super().__init__(
            code=status.HTTP_401_UNAUTHORIZED, title=title, message=message
        )


class InvalidTokenType(InvalidToken):
    def __init__(self, expected: str, received: str):
        super().__init__(
            title="Invalid token type",
            message=f"Expected token type '{expected}', but received '{received}'",
        )
