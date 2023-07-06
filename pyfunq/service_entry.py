from typing import Any, Callable

from pyfunq.owner import Owner
from pyfunq.reuse_scope import ReuseScope


class ServiceEntry:
    def __init__(
        self,
        container: Any,
        factory: Callable,
        reuse_scope: ReuseScope,
        instance: Any | None = None,
        owner: Owner = Owner.External
    ):
        self._owner = owner
        self._factory = factory
        self._instance = instance
        self._container = container
        self._reuse_scope = reuse_scope
