# py-funq
<a href="https://github.com/jlyonsmith/Funq/" target="_blank">Funq</a> Dependency injection container port for python

### Installation

```python
pip install py-funq

```
### Create Dependencies
```python
from abc import ABC, abstractmethod


class Developer(ABC):
    @abstractmethod
    def code(self) -> str:
        pass


class PythonDeveloper(Developer):
    def code(self) -> str:
        return 'Python'


class Person:
    def __init__(self, developer: Developer):
        self._developer = developer


```
### Create the container and register a dependency
```python
from pyfunq import Container

container = Container()
container.register(Developer, lambda c: PythonDeveloper())
```

### Resolve a dependency
```python
container.configure()
resolved = container.resolve(Developer)
```

### Use auto registrations using non abstract types

types that don't have dependencies can be auto registered
```python
container.register(PythonDeveloper)
container.configure()
container.resolve(PythonDeveloper)
```

### Register and resolve a complex dependency
```python
container.register(Person, (
    lambda c: Person(c.resolve(PythonDeveloper)))
)

container.configure()
person = container.resolve(Person)
```

### Register and resolve a named dependency
```python

container.register(Developer, lambda c: PythonDeveloper()) \
         .named('foo')
container.register(Developer, lambda c: PythonDeveloper())
container.configure()
developer = container.resolve(Developer)
named_developer = container.resolve_named(Developer, 'foo')
developer is not named_developer  # True
```

### Try to resolve a dependency
The container will throw an exception if it will not be able to resolve a dependency.<br/>
You can use the ```try_resolve``` or ```try_resolve_named``` functions in order to avoid an exception:
```python
container = Container()
container.configure()
developer = container.try_resolve(Developer)
if developer is not None:
...

namedDeveloper = container.try_resolve_named(Developer, 'foo')
if namedDeveloper is not None:
...

```
### Register and resolve a dependency with arguments
You can register a dependency that accepts any number of arguments
```python
class OneArgumentClass:
    def __init__(self, arg1: str):
        self._arg1 = arg1

class TwoArgumentsClass:
    def __init__(self, arg1: str, arg2: int):
        self._arg1 = arg1
        self._arg2 = arg2

class ThreeArgumentsClass:
    def __init__(self, arg1: str, arg2: int, arg3: bool):
        self._arg1 = arg1
        self._arg2 = arg2
        self._arg3 = arg3

container = Container()
container.register([OneArgumentClass, str], lambda c, arg1: OneArgumentClass(arg1))
container.register([TwoArgumentsClass, str, int], lambda c, arg1, arg2: TwoArgumentsClass(arg1, arg2))
container.register([ThreeArgumentsClass, str, int, bool], lambda c, arg1, arg2, arg3: ThreeArgumentsClass(arg1, arg2, arg3))
```

And resolve the dependencies using the appropriate arguments
```python
container.configure()
container.resolve(OneArgumentClass, 'value')
container.resolve(TwoArgumentsClass, 'value', 10)
container.resolve(ThreeArgumentsClass, 'value', 10, True)
```

### Creating child containers
By default all child containers can resolve dependencies within themselves and their parent.

```python
container = Container()
child_container = container.create_child_container()
container.register(Developer, lambda c: PythonDeveloper())
child_container.configure()
child_container.resolve(Developer)
try:
    container.resolve(Developer)
except ResolutionError:
    assert True
```

### Controlling the lifetime of an instance
The lifetime of an instance can be a singleton or per call (transient) <br/>
You can control the lifetime using the ```ReuseScope``` enum.<br/> 

```python
from enum import Enum

class ReuseScope(Enum):
    NoReuse = 'NoReuse'
    Container = 'Container'
    Hierarchy = 'Hierarchy'

```
By default all registrations are marked using  the ```ReuseScope.container``` scope.

```python
from pyfunq.reuse_scope import ReuseScope

# transient
container.register(Developer, lambda c: PythonDeveloper()) \
         .reused_within(ReuseScope.NoReuse) 

# singleton 
container.register(Developer, lambda c: PythonDeveloper()) \
         .reused_within(ReuseScope.Hierarchy) 

# singleton per container
container.register(Developer, lambda c: PythonDeveloper()) \
         .reused_within(ReuseScope.Container) 
```

### Disposing registered instances
You can let the container handle disposal of instances using the ```Owner``` enum.<br/>

```python
from enum import Enum


class Owner(Enum):
    External = 'External'
    Container = 'Container'

```
Only context manager instances can be managed within the container.
By default, all registrations are marked using  the ```Owner.Container``` scope.

```python
from pyfunq.owner import Owner

class Disposable:
    def __init__(self):
        self._is_disposed = False

    @property
    def is_disposed(self) -> bool:
        return self._is_disposed

    def __enter__(self):
        return self

    def __exit__(self, ex_type, value, traceback):
        self._is_disposed = True


container = Container()

# The container is responsible for disposing the instance
container.register(PythonDeveloper).owned_by(Owner.Container)

# The container is not responsible for disposing the instance 
container.register(PythonDeveloper).owned_by(Owner.External)
```

### Changing the default ReuseScope/Owner

```python
container = Container()

container.default_owner = Owner.External
container.default_reuse = ReuseScope.NoReuse
```

### License

[MIT](https://github.com/sagifogel/py-funq/blob/master/LICENSE)
<br/>
<br/>
Copyright © 2023 foldl
