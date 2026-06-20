class ChecklistError(Exception):
    """Base checklist domain error."""

    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(ChecklistError):
    status_code = 404


class ForbiddenError(ChecklistError):
    status_code = 403


class ConflictError(ChecklistError):
    status_code = 409


class ValidationError(ChecklistError):
    status_code = 422
