"""
Predefined test cases
"""
# pylint: disable=C0115,C0116
#   C0115 - missing-class-docstring
#   C0116 - missing-function-docstring
from typing import Any, Dict, Final, List, NamedTuple
from zoneinfo import ZoneInfo
import array
import calendar
from collections import ChainMap, Counter, OrderedDict, UserDict, UserList, UserString, deque
import enum
import datetime as dt
from dateutil import tz


class MyClass:
    name: str = 'test name'


class MySubClass(MyClass):
    ip_addr: str = '10.2.3.4'
    port: int = 8080
    __private_instance_var: str = 'private instance variable'

    def dummy(self) -> str:
        return self.__private_instance_var


class MySubSubClass(MySubClass):
    geolocation: str = 'America'

    def __init__(self):
        # create an instance variable
        self.instance_var = 'example instance variable'

    def dummy_func(self) -> None:
        pass  # pragma: no cover


my_class = MyClass()
my_sub_class = MySubClass()
my_sub_sub_class = MySubSubClass()


list_of_my_classes: List[MyClass] = [my_class, my_sub_class, my_sub_sub_class]


class Color(enum.Enum):
    RED = 1
    GREEN = "green"


class Shape(enum.IntEnum):
    CIRCLE = 1


class Perm(enum.IntFlag):
    R = 4


class Food(enum.Flag):
    FISH = enum.auto()
    # Intentionallyt assign a string to a integer enum
    VEGGIE = "veggie"  # type: ignore


def dummy_function() -> None:
    return None  # pragma: no cover


class Point3D(NamedTuple):
    x: int
    y: int
    z: int


# Driver Program
TEST_CASE: Final[Dict[Any, Any]] = {
    12: 144,
    'none-nothing': None,
    'empty-string': '',
    'Shape': Shape.CIRCLE,
    'Perm': Perm.R,
    'name': 'geeksforgeeks',
    'city': 'new york',
    'sub': {
        'sub1': 'v1',
        'sub2': 'v2',
        'list1': ['a', 'b', 'c'],
        'dictionary': {
            'my timezone': dt.timezone(dt.timedelta(hours=-6), 'test'),
            'my date': dt.date(2022, 11, 12),
            'my datetime': dt.datetime(2022, 11, 12, 14, 12, 5, 78),
            'my time': dt.time(16, 15, 14),
            'my tzinfo': tz.gettz('America/Chicago'),  # cSpell:ignore gettz
            'my zoneinfo': ZoneInfo('America/New_York'),
            'my timedelta': dt.timedelta(
                days=34,
                hours=13,
                minutes=46,
                seconds=57,
                milliseconds=675,
                microseconds=423
            ),
            'my timedelta -9 hrs': dt.timedelta(hours=-9),
            'my timedelta +7 hrs': dt.timedelta(hours=7),
            'my calendar': calendar.Calendar()
        },
        'Color-R': Color.RED,
        'Color-G': Color.GREEN,
        'Food-F': Food.FISH,
        'Food-V': Food.VEGGIE
    },
    'stock': 920,
    'bool T': True,
    'bool F': False,
    'binary': {
        'bytes': 'dummy'.encode('utf-8'),
        'bytearray': bytearray.fromhex('02 fe cc dd 32 14')
    },
    'sequences': {
        'list': [323, 455, 7687],
        'list_single': [12],
        'list_empty': [],
        'tuple': (12345, 54321, 'hello!'),
        'set': {453, 456, 534},
        'set_single': {453},
        'set_empty': {},
        'range': range(10),
        'array': array.array('i', [1, 2, 3]),
        'dict': {'foo': 'bar'},
        'named-tuple': Point3D(x=11, y=13, z=17)
    },
    'obj': object(),
    'dummy-func': dummy_function,
    'list_of_classes': list_of_my_classes,
    'collections': {
        'deque': deque('ghi'),
        'ChainMap': ChainMap(
            {'art': 'van gogh', 'opera': 'carmen'},
            {'music': 'bach', 'art': 'rembrandt'}
        ),
        'counter': Counter(a=4, b=2, c=0, d=-2),
        'OrderedDict': OrderedDict(one=1, two=2, three=3),
        'UserDict': UserDict([('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]),
        'UserList': UserList([('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]),
        'UserString': UserString('foobar'),
    }
}
