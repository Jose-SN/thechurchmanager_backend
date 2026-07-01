from __future__ import annotations


class RotaError(Exception):
    status_code = 400

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        super().__init__(message)


class NotFoundError(RotaError):
    status_code = 404


class ForbiddenError(RotaError):
    status_code = 403


class ConflictError(RotaError):
    status_code = 409


class ValidationError(RotaError):
    status_code = 422
