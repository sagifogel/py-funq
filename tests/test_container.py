import gc
import unittest
import weakref
from abc import ABC, abstractmethod
from typing import cast

from pyfunq.container import Container
from pyfunq.owner import Owner
from pyfunq.resolution_error import ResolutionError
from pyfunq.reuse_scope import ReuseScope


class TestContainer:
    def test_register_type_and_get_instance(self):
        container = Container()
        container.register(IBar, lambda c: Bar())
        container.configure()
        bar = container.resolve(IBar)

        assert bar is not None
        assert isinstance(bar, Bar)

    def test_container_supports_auto_registration(self):
        container = Container()
        container.register(Bar)
        container.configure()
        bar = container.resolve(Bar)

        assert bar is not None
        assert isinstance(bar, Bar)

    def test_container_does_not_supports_self_registration_abstract_classes(self):
        container = Container()
        container.register(IBar)
        container.configure()

        try:
            container.resolve(IBar)
            raise AssertionError()
        except TypeError:
            assert True

    def test_resolve_dependencies_injected(self):
        container = Container()
        container.register(IBar, lambda c: Bar())
        container.register(IFoo, lambda c: Foo(c.resolve(IBar)))
        container.configure()
        foo = cast(Foo, container.resolve(IFoo))

        assert foo is not None
        assert foo.bar is not None

    def test_constructor_arguments_passed_on_resolve(self):
        container = Container()
        container.register([IBar, str], lambda c, s: Bar(arg1=s))
        container.configure()
        bar = cast(Bar, container.resolve(IBar, "foo"))

        assert bar is not None
        assert bar.arg1 == "foo"

    def test_constructor_with_multiple_arguments_passed_on_resolve(self):
        container = Container()
        container.register([IBar, str, bool], lambda c, s, b: Bar(arg1=s, arg2=b))
        container.configure()
        bar = cast(Bar, container.resolve(IBar, "foo", True))

        assert bar is not None
        assert bar.arg1 == "foo"
        assert bar.arg2 is True

    def test_container_should_resolve_named_instances_in_no_particular_order(self):
        container = Container()
        container.register(IBar, lambda c: Bar("noname"))
        container.register(IBar, lambda c: Bar("a")).named("a")
        container.register(IBar, lambda c: Bar("b")).named("b")
        container.configure()
        a = cast(Bar, container.resolve_named(IBar, "a"))
        b = cast(Bar, container.resolve_named(IBar, "b"))
        noname = cast(Bar, container.resolve(IBar))
        assert a.arg1 == "a"
        assert b.arg1 == "b"
        assert noname.arg1 == "noname"

    def test_container_should_raise_resolution_error_when_a_service_was_not_found(self):
        bar: IBar | None = None
        container = Container()
        container.configure()

        try:
            bar = container.resolve(IBar)
        except ResolutionError:
            assert bar is None

    def test_container_should_raise_resolution_error_when_using_resolve_names_and_service_was_not_found(self):
        bar: IBar | None = None
        container = Container()
        container.configure()

        try:
            bar = container.resolve_named(IBar, '*')
        except ResolutionError:
            assert bar is None

    def test_container_should_not_raise_resolution_error_when_using_try_resolve_a_service_was_not_found(self):
        bar: IBar | None = None
        container = Container()
        container.configure()
        bar = container.try_resolve(IBar)
        assert bar is None

    def test_container_should_not_raise_resolution_error_when_using_try_resolve_named(self):
        bar: IBar | None = None
        container = Container()
        container.configure()
        bar = container.try_resolve_named(IBar, '*')
        assert bar is None

    def test_container_should_reuse_instances_within_scope(self):
        container = Container()
        container.register(IBar, lambda c: Bar()).reused_within(ReuseScope.Container)
        container.configure()
        bar1 = container.resolve(IBar)
        bar2 = container.resolve(IBar)
        assert bar1 is bar2

    def test_container_should_reuse_self_register_instances_within_scope(self):
        container = Container()
        container.register(Bar) \
            .reused_within(ReuseScope.Container)
        container.configure()
        bar1 = container.resolve(Bar)
        bar2 = container.resolve(Bar)

        assert bar1 is not None
        assert bar2 is not None
        assert isinstance(bar1, Bar)
        assert bar1 is bar2

    def test_child_container_should_resolve_registration_made_at_its_parent_container(self):
        container = Container()
        container.register(IBar, lambda c: Bar())
        container.configure()
        child_container = container.create_child_container()
        bar = child_container.resolve(IBar)
        assert bar is not None

    def test_calling_the_child_containers_configure_method_configures_all_parents(self):
        container = Container()
        child_container = container.create_child_container()
        container.register(IBar, lambda c: Bar())
        child_container.configure()
        child_container.resolve(IBar)
        try:
            container.resolve(IBar)
        except ResolutionError:
            assert True

    def test_container_using_reuse_scope_container_should_create_different_instances(self):
        container = Container()
        container.register(IBar, lambda c: Bar()).reused_within(ReuseScope.Container)
        container.configure()
        child_container = container.create_child_container()
        bar1 = container.resolve(IBar)
        bar2 = child_container.resolve(IBar)
        assert bar1 is not bar2

    def test_container_using_reuse_scope_hierarchy_should_create_a_singleton_instance(self):
        container = Container()
        container.register(IBar, lambda c: Bar()).reused_within(ReuseScope.Hierarchy)
        container.configure()
        child_container = container.create_child_container()
        bar1 = container.resolve(IBar)
        bar2 = child_container.resolve(IBar)
        assert bar1 is bar2

    def test_container_using_non_reuse_scope_should_create_an_instance_every_time(self):
        container = Container()
        container.register(IBar, lambda c: Bar()).reused_within(ReuseScope.NoReuse)
        container.configure()
        bar1 = container.resolve(IBar)
        bar2 = container.resolve(IBar)
        assert bar1 is not bar2

    def test_disposable_instance_owned_and_reused_by_container_is_disposed(self):
        foo: FooContextManager

        with Container() as container:
            container \
                .register(IFoo, lambda c: FooContextManager()) \
                .reused_within(ReuseScope.Container) \
                .owned_by(Owner.Container)

            container.configure()
            foo = cast(FooContextManager, container.resolve(IFoo))

        assert foo.is_disposed

    def test_disposable_instance_owned_by_container_and_reused_by_hierarchy_is_disposed(self):
        foo: FooContextManager

        with Container() as container:
            container \
                .register(IFoo, lambda c: FooContextManager()) \
                .reused_within(ReuseScope.Hierarchy) \
                .owned_by(Owner.Container)

            container.configure()
            foo = cast(FooContextManager, container.resolve(IFoo))

        assert foo.is_disposed

    def test_non_disposable_instance_owned_by_container_is_not_disposable_is_not_disposed(self):
        foo: FooContextManager

        with Container() as container:
            container \
                .register(IFoo, lambda c: Foo(Bar())) \
                .reused_within(ReuseScope.NoReuse) \
                .owned_by(Owner.Container)

            container.configure()
            foo = cast(FooContextManager, container.resolve(IFoo))

        assert foo is not None

    def test_disposable_instance_owned_externally_is_not_disposable_is_not_disposed(self):
        foo: FooContextManager

        with Container() as container:
            container \
                .register(IFoo, lambda c: Foo(Bar())) \
                .reused_within(ReuseScope.NoReuse) \
                .owned_by(Owner.Container)

            container.configure()
            foo = cast(FooContextManager, container.resolve(IFoo))

        assert foo is not None

    def test_disposed_instance_is_not_kept_alive_by_container(self):
        foo: FooContextManager | None

        with Container() as container:
            container \
                .register(IFoo, lambda c: FooContextManager()) \
                .reused_within(ReuseScope.NoReuse) \
                .owned_by(Owner.Container)

            container.configure()
            foo = cast(FooContextManager, container.resolve(IFoo))
            weak_ref = weakref.ref(foo)
            assert weak_ref() is foo
            foo = None
            gc.collect()
            assert weak_ref() is None

    def test_child_container_with_parent_registration_which_is_not_reused_is_disposed(self):
        foo: FooContextManager | None

        with Container() as container:
            container \
                .register(IFoo, lambda c: FooContextManager()) \
                .owned_by(Owner.Container)

            container.configure()
            with container.create_child_container() as child_container:
                foo = cast(FooContextManager, child_container.resolve(IFoo))

            assert foo._is_disposed

    def test_child_container_with_parent_registration_reused_by_hierarchy_is_not_disposed(self):
        foo: FooContextManager | None

        with Container() as container:
            container \
                .register(IFoo, lambda c: FooContextManager()) \
                .reused_within(ReuseScope.Hierarchy) \
                .owned_by(Owner.Container)

            container.configure()
            with container.create_child_container() as child_container:
                foo = cast(FooContextManager, child_container.resolve(IFoo))

            assert not foo._is_disposed


class IFoo(ABC):
    pass


class IBar(ABC):
    @abstractmethod
    def abc(self):
        pass


class FooContextManager(IFoo):
    def __init__(self):
        self._is_disposed = False

    @property
    def is_disposed(self) -> bool:
        return self._is_disposed

    def __enter__(self):
        return self

    def __exit__(self, ex_type, value, traceback):
        self._is_disposed = True


class Bar(IBar):
    def abc(self):
        pass

    def __init__(self, arg1: str | None = None, arg2: bool | None = None):
        self._arg1 = arg1
        self._arg2 = arg2

    @property
    def arg1(self) -> str | None:
        return self._arg1

    @property
    def arg2(self) -> bool | None:
        return self._arg2


class Foo(IFoo):
    def __init__(self, bar: Bar):
        self._bar = bar

    @property
    def bar(self) -> IBar:
        return self._bar
