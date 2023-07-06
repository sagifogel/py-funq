from abc import ABC, abstractmethod

from pyfunq.owner import Owner
from pyfunq.reuse_scope import ReuseScope


class OwnedSyntax(ABC):
    @abstractmethod
    def owned_by(self, owner: Owner) -> None:
        pass


class ReusedSyntax(ABC):
    @abstractmethod
    def reused_within(self, scope: ReuseScope) -> OwnedSyntax:
        pass


class ReusedOwnedSyntax(ReusedSyntax, OwnedSyntax, ABC):
    pass


class NamedSyntax(ABC):
    @abstractmethod
    def named(self, name: str) -> ReusedOwnedSyntax:
        pass


class RegistrationSyntax(NamedSyntax, ReusedOwnedSyntax, ABC):
    pass
