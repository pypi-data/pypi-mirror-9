import random
from datetime import datetime


# ISO 8601 http://www.w3.org/TR/NOTE-datetime
DATETIME_ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def strptime(timestamp):
    """
    convert a string timestamp the conforms to ISO 8601 to a timezone aware
    datetime instance
    """
    return datetime.strptime(
        timestamp, DATETIME_ISO_FORMAT
    )


def strftime(time):
    "convert datetime instance to an ISO 8601 string"
    return time.strftime(DATETIME_ISO_FORMAT)


def hash96(seed=None):
    """
    Returns a 24 hexidecimal hash of the seed given. If no seed is given then
    it returns a random hash based on the internal clock.
    ipython:
        %timeit hash96('hello')
        10000 loops, best of 3: 21.8 microseconds per loop on a macbook air
    N.B. This function has been checked across OS platforms and cpus... yeah
    it's python...
    """

    def _hash(bits=96):
        assert bits % 8 == 0
        required_length = bits / 8 * 2
        s = hex(random.getrandbits(bits)).lstrip('0x').rstrip('L')
        if len(s) < required_length:
            return _hash(bits)
        else:
            return s
    random.seed(seed)

    return _hash()


class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, cls=None):
        if cls is None:
            cls = type(obj)
        return self.fget.__get__(obj, cls)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)
