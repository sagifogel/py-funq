from typing import Type, cast


class ServiceKey:
    def __init__(self, service_type: Type, factory_type: tuple, name: str | None = None):
        self._name = name
        self._service_type = service_type
        self._factory_type = factory_type

    @property
    def service_type(self) -> Type:
        return self._service_type

    @property
    def factory_type(self) -> tuple:
        return self._factory_type

    @property
    def name(self) -> str | None:
        return self._name

    def __eq__(self, other):
        if other is None or type(self) != type(other):
            return False

        if self is other:
            return True

        other_service_key = cast(ServiceKey, other)
        return (
            self.name == other_service_key.name and
            self.service_type == other_service_key.service_type and
            self.factory_type == other_service_key.factory_type
        )

    def __hash__(self):
        return hash((self.service_type, self.factory_type, self.name))
