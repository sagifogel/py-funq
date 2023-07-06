from enum import Enum


class ReuseScope(Enum):
    NoReuse = 'NoReuse'
    Container = 'Container'
    Hierarchy = 'Hierarchy'
