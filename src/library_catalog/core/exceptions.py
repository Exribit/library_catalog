class AppException(Exception):
    """Базовое исключение приложения."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
    ) -> None:
        self.message = message
        self.status_code = status_code

        super().__init__(message)

class NotFoundException(AppException):
    """Базовое исключение для отсутствующих ресурсов."""

    def __init__(
        self,
        resource: str,
        identifier: object,
    ) -> None:
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            status_code=404,
        )