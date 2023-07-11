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
developer = container.resolve_named(Developer, 'foo')
developer is not container.resolve(Developer)  # True
```

### Try to resolve a dependency
The container will throw an exception if it will not be able to resolve a dependency.<br/>
You can use the ```try_resolve``` or ```try_resolve_named``` functions in order to avoid an exception:
```python
container = Container()
developer = container.try_resolve(Developer)
if developer is not None:
...

namedDeveloper = container.try_resolve_named(Developer, 'foo')
if namedDeveloper is not None:
...
```
### Register and resolve a named dependency with arguments
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
container.resolve(OneArgumentClass, 'value')
container.resolve(TwoArgumentsClass, 'value', 10)
container.resolve(ThreeArgumentsClass, 'value', 10, True)
```

### License

[MIT](https://github.com/sagifogel/py-funq/blob/master/LICENSE)
<br/>
<br/>
Copyright © 2023 foldl
