from typing import Type


class ResolutionError(ValueError):
    def __init__(self, message: str, service_type: Type | None, *args):
        self.message = message
        self.service_type = service_type
        super().__init__(message, service_type, *args)
