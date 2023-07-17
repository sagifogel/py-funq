from __future__ import annotations

import weakref
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Any, Callable, Optional, Type, TypeVar

from _weakref import ReferenceType

from pyfunq.owner import Owner
from pyfunq.registration import Registration
from pyfunq.resolution_error import ResolutionError
from pyfunq.reuse_scope import ReuseScope
from pyfunq.service_entry import ServiceEntry
from pyfunq.service_key import ServiceKey

TService = TypeVar('TService')


class Container(AbstractContextManager):

    def __init__(self) -> None:
        self._registrations: list[Registration] = []
        self._parent_container: Container | None = None
        self._disposables: list[ReferenceType[Any]] = []
        self._services: dict[ServiceKey, ServiceEntry] = dict()

    def register(self, service_type: Type | list[type], factory: Optional[Callable] = None) -> Registration:
        ctor, *params = service_type if isinstance(service_type, list) else [service_type]
        if factory is None and len(params) > 0:
            raise ValueError('self registration is only available with 0 params')
        concrete_factory = factory if factory is not None else self.__closure__(ctor)
        registration = Registration(
            service_type=ctor,
            factory=concrete_factory,
            factory_type=tuple(params),
        )
        self._registrations.append(registration)
        return registration

    def configure(self) -> None:
        self._configure()
        parent_container = self._parent_container
        if parent_container is not None:
            parent_container.configure()

    def _configure(self):
        while len(self._registrations) > 0:
            registration = self._registrations.pop()
            service_key = ServiceKey(
                name=registration._name,
                service_type=registration._service_type,
                factory_type=registration._factory_type,
            )
            self._services[service_key] = ServiceEntry(
                container=self,
                owner=registration._owner,
                factory=registration._factory,
                reuse_scope=registration._reuse_scope,
            )

    def create_child_container(self) -> Container:
        container = Container()
        container._parent_container = self
        return container

    def resolve(self, ctor: Type[TService], *args) -> TService:
        return self._resolve_internal(ctor, *args)

    def resolve_named(self, ctor: Type[TService], name: str, *args) -> TService:
        return self._resolve_internal(ctor, *args, name=name)

    def try_resolve(self, ctor: Type[TService], *args) -> TService | None:
        return self._try_resolve_internal(ctor, *args)

    def try_resolve_named(self, ctor: Type[TService], name: str, *args) -> TService:
        return self._try_resolve_internal(ctor, *args, name=name)

    def dispose(self) -> None:
        self.__exit__(None, None, None)

    def __exit__(
        self,
        __exc_type: Type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None
    ) -> bool | None:
        while len(self._disposables) > 0:
            weak_ref = self._disposables.pop()
            if disposable := weak_ref():
                disposable.__exit__(None, None, None)

        return None

    @staticmethod
    def __closure__(ctor: Type) -> Callable:
        return lambda _: ctor()

    def _resolve_internal(self, ctor: Type[TService], *args, name: str | None = None) -> TService:
        arg_types = (type(arg) for arg in args)
        service_key = ServiceKey(ctor, tuple(arg_types), name)
        service_entry = self._get_service_entry(service_key)
        if service_entry is None:
            raise ResolutionError('could not resolve instance', service_type=ctor)
        return self._get_or_create(service_key, service_entry, *args)

    def _get_service_entry(self, service_key: ServiceKey) -> ServiceEntry | None:
        service_entry = self._get_hierarchy_service_entry(service_key)
        if service_entry is not None:
            reuse_scope = service_entry._reuse_scope
            container = service_entry._container
            if reuse_scope == ReuseScope.Container and container is not self:
                service_entry = self._clone_service_entry(service_entry)
                self._services[service_key] = service_entry
        return service_entry

    def _get_hierarchy_service_entry(self, service_key: ServiceKey) -> ServiceEntry | None:
        service_entry = self._services.get(service_key)
        if service_entry is not None:
            return service_entry
        if parent_container := self._parent_container:
            return parent_container._get_service_entry(service_key)
        return None

    def _get_or_create(self, service_key: ServiceKey, service_entry: ServiceEntry, *args) -> Any:
        container = service_entry._container
        reuse_scope = service_entry._reuse_scope
        if reuse_scope == ReuseScope.Hierarchy and container is not self:
            return container._get_or_create(service_key, service_entry)

        owner = service_entry._owner
        instance = service_entry._instance or service_entry._factory(self, *args)
        if reuse_scope != ReuseScope.NoReuse:
            service_entry._instance = instance
        if owner == Owner.Container and self._is_disposable(instance):
            weak_ref = weakref.ref(instance)
            self._disposables.append(weak_ref)
        return instance

    @staticmethod
    def _is_disposable(instance: Any) -> bool:
        return hasattr(instance, '__enter__') and hasattr(instance, '__exit__')

    def _clone_service_entry(self, service_entry: ServiceEntry) -> ServiceEntry:
        return ServiceEntry(
            container=self,
            owner=service_entry._owner,
            factory=service_entry._factory,
            reuse_scope=service_entry._reuse_scope,
        )

    def _try_resolve_internal(self, ctor: Type[TService], *args, name: str | None = None):
        try:
            return self._resolve_internal(ctor, *args, name=name)
        except ResolutionError:
            return None
