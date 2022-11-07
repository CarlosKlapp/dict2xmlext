from zoneinfo import ZoneInfo
import array
import calendar
from collections import ChainMap, Counter, OrderedDict, UserDict, UserList, UserString, namedtuple, deque
import enum
import datetime as dt
from dateutil import tz


class MyClass:
    name: str = 'test name'


class MySubClass(MyClass):
    ip_addr: str = '10.2.3.4'
    port: int = 8080
    __private_instance_var: str = 'private instance variable'


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


list_of_my_classes = [my_class, my_sub_class, my_sub_sub_class]


class Color(enum.Enum):
    RED = 1
    GREEN = "green"


class Shape(enum.IntEnum):
    CIRCLE = 1


class Perm(enum.IntFlag):
    R = 4


class Food(enum.Flag):
    FISH = enum.auto()
    VEGGIE = "veggie"


def dummy_function() -> None:
    return None  # pragma: no cover


Point3D = namedtuple('Point', ['x', 'y', 'z'])

# Driver Program
test_case = {
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
        'l1': ['a', 'b', 'c'],
        'dt': {
            'my timezone': dt.timezone(dt.timedelta(hours=-6), 'test'),
            'my date': dt.date(2022, 11, 12),
            'my datetime': dt.datetime(2022, 11, 12, 14, 12, 5, 78),
            'my time': dt.time(16, 15, 14),
            'my tzinfo': tz.gettz('America/Chicago'),  # cSpell:ignore gettz
            'my zoneinfo': ZoneInfo('America/Chicago'),
            'my timedelta': dt.timedelta(days=34, hours=13, minutes=46, seconds=57, milliseconds=675, microseconds=423),
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
        'list': [323],
        'tuple': (12345, 54321, 'hello!'),
        'set': {453},
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
        'ChainMap': ChainMap({'art': 'van gogh', 'opera': 'carmen'}, {'music': 'bach', 'art': 'rembrandt'}),
        'counter': Counter(a=4, b=2, c=0, d=-2),
        'OrderedDict': OrderedDict(one=1, two=2, three=3),
        'UserDict': UserDict([('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]),
        'UserList': UserList([('yellow', 1), ('blue', 2), ('yellow', 3), ('blue', 4), ('red', 1)]),
        'UserString': UserString('foobar'),
    }
}
