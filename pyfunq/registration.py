from __future__ import annotations

from typing import Callable, Type

from pyfunq.owner import Owner
from pyfunq.reuse_scope import ReuseScope
from pyfunq.syntax import OwnedSyntax, RegistrationSyntax, ReusedOwnedSyntax


class Registration(RegistrationSyntax):
    def __init__(self, service_type: Type, factory_type: tuple, factory: Callable):
        self._factory = factory
        self._name: str | None = None
        self._service_type = service_type
        self._factory_type = factory_type
        self._owner: Owner = Owner.Container
        self._reuse_scope: ReuseScope = ReuseScope.NoReuse

    def named(self, name: str) -> ReusedOwnedSyntax:
        self._name = name
        return self

    def reused_within(self, reuse_scope: ReuseScope) -> OwnedSyntax:
        self._reuse_scope = reuse_scope
        return self

    def owned_by(self, owner: Owner) -> None:
        self._owner = owner
