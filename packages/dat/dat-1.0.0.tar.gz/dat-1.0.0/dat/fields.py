from bson.objectid import ObjectId
from bson.timestamp import Timestamp
from types import FunctionType, ClassType
from datetime import datetime
from .utils import strptime, strftime
from .exceptions import SerializationError, ValidationError

import sys
import logging
import pymongo

logger = logging.getLogger(__name__)


def serializeDatetime(value, to_json=False):
    if to_json and isinstance(value, datetime):
        return strftime(value)
    elif isinstance(value, datetime):
        return Timestamp(value, 0)
    return value


def serializeList(iterable, to_json=False):
    "a generator function to help with serializing of lists"
    for item in iterable:
        if isinstance(item, (tuple, set, list)):
            value = list(serializeList(item, to_json))
        elif isinstance(item, dict):
            value = dict(serializeDict(item, to_json))
        else:
            value = serializeDatetime(item, to_json)
        yield value


def serializeDict(obj, to_json=False):
    "a generator function to help with serializing of dicts"
    for key, val in obj.items():
        if isinstance(val, (tuple, set, list)):
            value = list(serializeList(val, to_json))
        elif isinstance(val, dict):
            value = dict(serializeDict(val, to_json))
        else:
            value = serializeDatetime(val, to_json)
        yield key, value


class Field(object):

    value = None
    index = False
    index_weight = 100

    def __init__(self, *args, **kwargs):
        self.default = kwargs.get('default')
        self.index = kwargs.get('index')
        self.unique = kwargs.get('unique', False)
        self.background = kwargs.get('background', True)
        self.sparse = kwargs.get('sparse', False)
        if self.index == pymongo.GEO2D:
            self.geo_min = kwargs.get('geo_min')
            self.geo_max = kwargs.get('geo_max')
        if self.unique:
            self.drop_dups = kwargs.get('drop_dups', False)

    def __repr__(self):
        return '<%s: updated %s>' % (self.__class__.__name__, self.value)

    @classmethod
    def getDataType(cls):
        if not hasattr(cls, '_data_type'):
            cls._data_type = cls.construct().__class__
        return cls._data_type

    def serialize(self, value, to_json=False):
        try:
            ret = self._serialize(value, to_json=to_json)
        except Exception, e:
            raise SerializationError(str(e)), None, sys.exc_info()[2]
        else:
            return ret

    def _serialize(self, value, to_json=False):
        return self.construct(value)

    def validate(self, value):
        try:
            ret = self._validate(value)
        except Exception, e:
            raise ValidationError(str(e)), None, sys.exc_info()[2]
        else:
            return ret

    def _validate(self, value):
        if not isinstance(value, self.getDataType()):
            raise ValidationError(
                '%r'
            ), None, sys.exc_info()[2]
        return value

    def load(self, value):
        try:
            ret = self._load(value)
        except Exception, e:
            raise ValidationError(str(e)), None, sys.exc_info()[2]
        else:
            return ret

    def _load(self, value):
        return self.construct(value)

    def clean(self, value):
        value = self.load(value)
        return self.validate(value)

    def getDefault(self):
        if isinstance(self.default, (FunctionType, ClassType)):
            return self.default()
        else:
            return self.default


class Id(Field):

    construct = staticmethod(ObjectId)

    def _serialize(self, value, to_json=False):
        if to_json:
            ret = str(value)
        else:
            ret = ObjectId(value) if not isinstance(value, ObjectId) else value
        return ret


class TimeStamp(Field):

    construct = staticmethod(datetime.utcnow)
    _data_type = datetime

    def __init__(self, *args, **kwargs):
        self.auto_now = kwargs.get('auto_now', False)
        self.auto_now_add = kwargs.get('auto_now_add', False)
        super(TimeStamp, self).__init__(*args, **kwargs)

    def _load(self, value):
        if isinstance(value, str):
            return strptime(value)
        return Timestamp(value, 0)

    def _serialize(self, value, to_json=False):
        # 0 is tz increment for utc/gmt
        if isinstance(value, Timestamp):
            value = value.as_datetime()
        return strftime(value) if to_json else Timestamp(value, 0)

    def getDefault(self):
        if self.auto_now_add or self.auto_now:
            return self.construct()
        return None


class Int(Field):

    construct = staticmethod(int)


class Float(Field):

    construct = staticmethod(float)


class Char(Field):

    construct = staticmethod(unicode)
    _data_type = (str, unicode)


class List(Field):

    construct = staticmethod(list)
    _data_type = (tuple, list)

    def _serialize(self, value, to_json=False):
        return list(serializeList(value))


class Set(Field):

    construct = staticmethod(set)

    def _serialize(self, value, to_json=False):
        return tuple(serializeList(value))


class Dict(Field):

    construct = staticmethod(dict)

    def _serialize(self, value, to_json=False):
        return dict(serializeDict(value))
